# Engenharia de Dados — Núcleo Comum (Spark SQL-first, Medallion, Delta)

Disciplina técnica comum a qualquer notebook Spark de engenharia de dados deste método, **independente da nuvem**. Isto é o que todo notebook Silver/Gold segue por padrão, seja o projeto Microsoft Fabric ou Databricks. As diferenças reais entre as duas nuvens — arquitetura de camadas, formato da célula de parâmetros, orquestração, CI/CD, governança — estão nos dois overlays curtos: `03a-fabric-overlay.md` e `03b-databricks-overlay.md`. Carregue este arquivo sempre que for criar, revisar, refatorar ou padronizar um notebook Silver/Gold, uma transformação, uma checagem de qualidade, um write Delta ou uma função de import/export de notebook.

> **Client-agnóstico.** Nomes de lakehouse/catalog/schema/domínio vêm sempre da configuração do projeto (`@client_context/` ou equivalente). Os exemplos abaixo usam placeholders genéricos (`entidade`, `transacao`, `categoria`, `sistema_origem_x`) no lugar de qualquer nome de cliente.

---

## 1. Arquitetura medallion — o que é comum

Todo projeto termina em `Silver -> Gold`: Silver contém entidades de negócio padronizadas e reutilizáveis; Gold contém produtos analíticos orientados a consumo de BI, sem prefixo `dim_`/`fact_` salvo pedido explícito. Não criar dimensão em Gold — dimensões vivem em Silver e podem ser conectadas de lá para os produtos Gold no modelo semântico.

O que muda entre nuvens é **a origem** dessa cadeia: se existe ou não uma camada Bronze física, e de onde ela lê. Isso é arquitetura, não disciplina de transformação — ver o overlay da sua nuvem antes de desenhar a primeira leitura de origem.

---

## 2. Filosofia Spark SQL-first: cadeia de temp views

Notebooks Silver/Gold são revisados junto com o PO e analistas de negócio, não só por engenheiros. Lógica de transformação escrita como `.select(...)`/`F.when(...)` encadeados em PySpark é difícil de ler para quem não programa, e isso atrasa a revisão conjunta das regras de negócio. Por isso o padrão é:

- **Lógica de transformação em Spark SQL, como uma cadeia de temp views — nunca CTE.** Projeções, casts, derivações `CASE WHEN`, de-para enum→label, joins e window functions vão dentro de `spark.sql("""...""")`, um passo lógico por temp view nomeada (**origem → tratada → derivada → final**), cada uma criada via `createOrReplaceTempView` na sua própria célula de notebook, **imediatamente precedida por uma célula Markdown** que nomeia a view e descreve em português simples o que ela contém (grão, de onde vem, o que mudou desde o passo anterior). Nunca `WITH ... AS (...)` dentro de uma única chamada `spark.sql`, e nunca duas views produzidas na mesma célula.
- **Plumbing fica em Python/DataFrame API.** É agnóstico de estilo e reescrever em SQL só prejudicaria a legibilidade: a célula de parâmetros + split de pipe, os Spark configs, `aplicar_watermark`/`calcular_watermark_efetivo`, `validar_minimo` + checagens de qualidade, `adicionar_metadados_processamento` (`data_processamento = F.current_timestamp()`), as leituras de origem, `gravar_full`/`gravar_merge` (DeltaTable), e a orquestração.
- **Regra prática:** o resultado do `spark.sql` final é envolvido no fluxo Python de escrita/validação já existente; não converta essa parte para SQL. O handle final (`df_final`) é quem dirige a validação e o write Delta controlado.

Por que isso importa na prática: um `CASE WHEN` lido de cima a baixo é a regra de negócio em si — um revisor sem Spark consegue confirmar "0 é PF, 3 é PJ, qualquer outra coisa é Indefinido" direto na célula, sem precisar entender Catalyst nem DataFrame API.

### 2.1 Exemplo antes/depois (mesma semântica, dois estilos)

Antes — helper PySpark + `.select()` encadeado (difícil de revisar por não-engenheiro):

```python
# Mapeamento de PF/PJ a partir de Entidade.TipoDocumento (0=PF, 3=PJ; demais=Indefinido).
def mapear_tipo_pessoa(coluna: str):
    return (
        F.when(F.col(coluna) == 0, F.lit("PF"))
        .when(F.col(coluna) == 3, F.lit("PJ"))
        .otherwise(F.lit("Indefinido"))
    )

df = df_entidade.select(
    F.col("EntidadeId").cast("string").alias("id_entidade"),
    mapear_tipo_pessoa("TipoDocumento").alias("tipo_pessoa"),
)
```

Depois — temp view Spark SQL, semântica idêntica, sem CTE:

```markdown
#### entidade_tratada
PF/PJ a partir de `Entidade.TipoDocumento` (0=PF, 3=PJ; demais=Indefinido). Mesmo grão da origem (1 linha por `id_entidade`).
```

```python
# entidade_tratada: PF/PJ a partir de TipoDocumento (0=PF, 3=PJ; demais=Indefinido).
def gera_view_entidade_tratada():
    spark.sql("""
        SELECT
            CAST(EntidadeId AS STRING) AS id_entidade,
            CASE
                WHEN TipoDocumento = 0 THEN 'PF'
                WHEN TipoDocumento = 3 THEN 'PJ'
                ELSE 'Indefinido'
            END AS tipo_pessoa
        FROM cad_entidade_origem
    """).createOrReplaceTempView("entidade_tratada")


gera_view_entidade_tratada()
```

O `CASE WHEN` lê como a regra de negócio: um revisor sem Spark confirma "0 é PF, 3 é PJ, o resto é Indefinido" direto. Note a forma: comentário de uma linha acima da função (documenta o código), célula Markdown acima da célula de código (documenta o notebook renderizado, para quem revisa) — as duas coisas coexistem e têm papéis diferentes.

### 2.2 Regras de forma que tornam isso consistente

- Uma temp view por passo lógico, nunca CTE — um nome de view legível diz o que ela contém, e a célula Markdown acima diz por quê.
- `CASE WHEN` carrega todo de-para enum→label e toda derivação de negócio — essa é a linha que o PO revisa.
- Só o **último** passo (`gera_tabela_final`) retorna um DataFrame em vez de registrar uma view — vira `df_final`, que dirige validação e o write Delta controlado. Todo passo anterior registra uma temp view e não precisa ser capturado em variável.
- O passo **final** enumera as colunas entregues explicitamente. `SELECT *` é aceitável numa view intermediária, nunca na projeção final nem sobre uma tabela de origem grande.
- Qualifique colunas em joins (`t.col`, `d.col`) para o leitor saber a origem de cada campo.
- Use expressões SQL nativas (`CAST`, `CASE WHEN`, `to_timestamp`, `coalesce`, window functions) em vez de UDF Python — ambas compilam para o mesmo plano Catalyst, então SQL-first não custa performance. Use `NULL` tipado (`CAST(NULL AS TIMESTAMP)`/`AS INT`/`AS BOOLEAN`), nunca um literal não tipado.

---

## 3. Nomenclatura de função

Nomes canônicos que ancoram o contrato do notebook — sob o estilo SQL-first, o papel de "plumbing" e "tratamento" se separa com clareza:

**Plumbing (Python/DataFrame API):**

- `nome_tabela`
- `ler_origem` — lê a origem espelhada/física. Pode continuar `spark.table(...)`, ou virar um `spark.sql`/temp view sobre a origem para a cadeia de transformação referenciá-la pelo nome.
- `gera_tabela_<TABELA>` — lê **uma** tabela de origem e a registra como temp view; uma função por tabela de origem, uma por célula.
- `gera_view_<nome>` — todo outro passo produtor de temp view (tratada, derivada, join, dedup, pivot, associação); um passo lógico por função, uma por célula, nunca CTE.
- `gera_tabela_final` — **exceção**: é o último passo da cadeia e **retorna um DataFrame em vez de registrar view**. Alimenta `df_final`.
- `adicionar_metadados_processamento`
- `aplicar_watermark` / `calcular_watermark_efetivo`
- `validar_minimo`
- `gravar_full` / `gravar_merge`
- `exibir_contagem`

**Tratamentos (expressão SQL canônica, reusada dentro de cada `SELECT` produtor de view — semântica idêntica a um helper PySpark equivalente):**

- `tratar_inteiro(col)` → `CAST(col AS INT)` (nulo permanece nulo).
- `tratar_booleano(col)` → `CAST(col AS BOOLEAN)` (nulo permanece nulo).
- `tratar_timestamp(col)` → parse com guarda; trata nulo, string vazia, `9999-12-31`, `9999-12-31 00:00:00`, `0001-01-01` e qualquer valor anterior a `1900-01-01` como `NULL`, senão `to_timestamp(col)`:

```sql
CASE
    WHEN col IS NULL THEN NULL
    WHEN trim(CAST(col AS STRING)) = '' THEN NULL
    WHEN trim(CAST(col AS STRING)) IN ('9999-12-31', '9999-12-31 00:00:00', '0001-01-01') THEN NULL
    WHEN trim(CAST(col AS STRING)) < '1900-01-01' THEN NULL
    ELSE to_timestamp(col)
END
```

- `tratar_timestamp_utc(col)` — as mesmas guardas de `tratar_timestamp`, seguidas de uma conversão de fuso horário (ex.: UTC → fuso local do projeto). **A forma exata da conversão (DST-aware vs. offset fixo) é uma decisão de projeto, não uma regra universal** — dois modos podem coexistir deliberadamente no mesmo repositório quando há paridade a preservar com uma view legada; ver o overlay da sua nuvem para o caso concreto e o motivo de não unificar sem confirmar com o consumidor a jusante.

Escreva nomes de função auxiliar em português. Adicione um comentário curto imediatamente antes de cada `def`. Não use o sufixo `seguro` em nomes de tratamento — prefira que o nome descreva o que o tratamento faz.

**Convenção de prefixo de ID entre sistemas.** Quando o projeto tem uma única origem confiável para uma entidade, o ID vira `CAST(<CampoOrigem> AS STRING) AS id_<entidade>` sem prefixo adicional. Quando o projeto integra múltiplas origens para a mesma entidade (múltiplos sistemas alimentando o mesmo domínio), é comum prefixar o ID com um código curto do sistema de origem (`CONCAT('<codigo_sistema_origem>', CampoOrigem) AS id_<entidade>`) para garantir unicidade entre sistemas. Essa é uma decisão de modelagem de projeto (single-source vs. multi-source), não uma regra fixa de nenhuma nuvem — declare-a explicitamente na primeira Silver da entidade e mantenha-a consistente em toda referência à mesma chave (inclusive `id_<entidade>` usado como `id_silver_<entidade>` — um alias direto do campo já prefixado, nunca uma concatenação nova, para evitar prefixo duplicado).

---

## 4. Convenção de coluna

- Colunas em `snake_case`, em português, com prefixo tipado: `id_*` (chaves), `dt_*` (timestamps/datas), `fl_*` (booleanos), `codigo_*` (enums brutos, inteiros), `valor_*` (decimais), mais colunas de label decodificado sem prefixo fixo (`origem_transacao`, `status_transacao`, `tipo_transacao`).
- **IDs são sempre `STRING`** (`CAST(EntidadeId AS STRING) AS id_entidade`), nunca numérico — mesmo quando o valor de origem parece um inteiro. Vale para toda chave: chave de negócio da própria entidade, IDs que referenciam outra entidade, e códigos de lookup/status.
- **`data_processamento` é obrigatório em todo write** de Silver e Gold, adicionado em PySpark no momento da gravação com `F.current_timestamp()` (ou equivalente nativo, ex. `CURRENT_TIMESTAMP()` em SQL se a coluna não vier de um helper):

```python
# Adiciona a coluna de controle de processamento no momento da escrita.
def adicionar_metadados_processamento(df):
    return df.withColumn("data_processamento", F.current_timestamp())
```

- Não usar `TRIM` por padrão — só quando houver evidência de espaço em branco indevido no dado ou requisito explícito de limpeza.
- Não criar `CASE WHEN` defensivo em toda coluna por padrão — reserve `CASE WHEN` para regra de negócio real, classificação, normalização necessária, ou evidência concreta de variação no dado.

---

## 5. Deduplicação explícita (nunca silenciosa)

Dedup é um passo explícito e documentado — nunca um `dropDuplicates()` escondido, nunca `DISTINCT` silencioso sobre um problema de grão. Use `ROW_NUMBER()` com chave e critério de desempate documentados, cada estágio como sua própria temp view para o estado intermediário ficar inspecionável.

```markdown
#### entidade_com_id
Uma linha por ocorrência de `id_entidade` na origem tratada, com o ranking de desempate (`rn`) que a deduplicação seguinte usa.
```

```python
# entidade_com_id: origem já tratada, uma linha por ocorrência (ainda com duplicatas de chave).
def gera_view_entidade_com_id():
    spark.sql("""
        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY id_entidade
                   ORDER BY dt_alteracao_origem DESC, dt_criacao_origem DESC
               ) AS rn
        FROM entidade_tratada
    """).createOrReplaceTempView("entidade_com_id")


gera_view_entidade_com_id()
```

```markdown
#### entidade_deduplicada
Mantém a linha mais recente por `id_entidade` (desempate por `dt_alteracao_origem`, depois `dt_criacao_origem`, documentado na etapa anterior).
```

```python
# entidade_deduplicada: mantem a linha mais recente por id_entidade (rn = 1).
def gera_view_entidade_deduplicada():
    spark.sql("SELECT * FROM entidade_com_id WHERE rn = 1").createOrReplaceTempView("entidade_deduplicada")


gera_view_entidade_deduplicada()
```

- As colunas de desempate são a decisão de negócio — escreva-as, não escolha uma linha arbitrária.
- `<entidade>_com_id` e `<entidade>_deduplicada` não se distinguem pelo nome sozinhas — a célula Markdown antes de cada uma (mais o comentário de uma linha acima de cada `createOrReplaceTempView`) é o que as diferencia. Sempre inclua as duas.
- Valide que a chave ficou única depois do dedup no estágio de Data quality checks (seção 7).

Use este mesmo padrão (`ROW_NUMBER()` + `WHERE rn = 1`) quando precisar só do atributo do registro mais recente por chave. Quando também precisar de uma contagem/agregado sobre **todos** os registros da chave — não só o mais recente — use o padrão pivot-latest-per-key: rankeie com `ROW_NUMBER()`, depois agregue com `MAX(CASE WHEN rn = 1 THEN col END)` para o atributo atual e `COUNT(DISTINCT ...)` para o total, no mesmo `GROUP BY`:

```python
# eventos_por_entidade: 1 linha por id_entidade, atributo do evento mais recente + contagem de todos os eventos.
def gera_view_eventos_por_entidade():
    spark.sql("""
        SELECT
            id_entidade,
            MAX(CASE WHEN rn = 1 THEN tipo_evento END) AS tipo_evento_atual,
            MAX(CASE WHEN rn = 1 THEN dt_evento END) AS dt_evento_mais_recente,
            COUNT(DISTINCT id_evento) AS qtd_eventos
        FROM eventos_ordenados
        GROUP BY id_entidade
    """).createOrReplaceTempView("eventos_por_entidade")
```

---

## 6. Princípio `unhandled_case_explicit`

Toda classificação, de-para, deduplicação ou derivação precisa **declarar visivelmente o que acontece com um valor que não se encaixa**. Uma falha visível é melhor que um default silencioso. Quando um default é intencional, ele precisa de justificativa escrita e precisa ser observável.

Concretamente:

- **De-para / `CASE WHEN`** termina com um `ELSE` que é ou um catch-all nomeado (`'Indefinido'`, `'Outro'`) **contado por um aviso Tier 2** (seção 7), ou uma guarda que levanta exceção quando um código não mapeado é um defeito real. Um `CASE` sem `ELSE` retorna `NULL` silenciosamente — nunca deixe um de-para enum→label em aberto sem decidir qual dos dois comportamentos você quer.
- **`TRY_CAST`** retorna `NULL` na falha, sem erro. Se um nulo ali é aceitável, diga por quê num comentário de uma linha. Se não é (ex.: um `valor_*` obrigatório), conte os nulos e levante exceção.
- **Deduplicação** usa um desempate explícito (`ROW_NUMBER() OVER (PARTITION BY pk ORDER BY <dt> DESC)`); as colunas de ordenação são documentadas, nunca uma linha arbitrária. Valide que a chave ficou única antes e depois.
- A guarda de origem vazia, o desempate do dedup e o bloqueio de código não mapeado são o **mesmo princípio** aplicado em três pontos do pipeline.

Sem isso, um valor não mapeado vira `NULL` ou um default errado sem aviso, e o número final fica plausível mas incorreto, sem nada que sinalize o problema.

**Cuidado — literais acentuados em comparações `CASE WHEN`/`WHERE`.** Um de-para que casa um valor de enum de origem com um literal acentuado (ex.: `UPPER(status) = 'NEGOCIACAO'` tentando casar "negociação") é frágil ao encoding do arquivo: um notebook salvo ou reimportado com o encoding errado pode transformar o literal silenciosamente em mojibake, e a comparação passa a não casar nada sem levantar exceção nenhuma — um defeito real já observado em notebook de produção. Verifique que o `.ipynb` mantém UTF-8 na ida e volta antes de confiar num literal acentuado, e prefira a query de descoberta de domínio (abaixo) para confirmar os bytes exatos do valor que você está comparando, em vez de retypar à mão.

**Descoberta de domínio antes de fechar um de-para.** Antes de hardcodar o `ELSE` de um `CASE WHEN` de classificação, consulte os valores distintos observados nas origens que alimentam o de-para, para que o mapeamento seja construído a partir de evidência, não suposição. Isto é uma query diagnóstica de autoria, não faz parte do pipeline entregue — não precisa de célula Markdown antes:

```python
# Valores distintos observados nas origens que alimentam o de-para, para revisar antes de fechar o CASE WHEN.
spark.sql("""
    SELECT DISTINCT 'ENTIDADE_ATUAL' AS origem, status_entidade AS valor
    FROM cad_entidade_silver WHERE status_entidade IS NOT NULL
    UNION ALL
    SELECT DISTINCT 'HISTORICO', status_historico
    FROM historico_entidade_silver WHERE status_historico IS NOT NULL
    ORDER BY origem, valor
""").show(200, truncate=False)
```

Re-rode essa query sempre que o aviso Tier 2 de resíduo de de-para (seção 7) crescer — um valor novo não mapeado é a causa mais provável.

---

## 7. Quality gates em duas camadas

Todo notebook Silver/Gold tem uma única seção `#### Data quality checks`, e ela roda **antes** de `#### Write table`. Dentro dela, cada checagem é de um dos dois tipos — escolher o nível deliberadamente é o ponto principal.

### 7.1 Tier 1 — hard gate (`raise ValueError`, bloqueia o write)

Use quando uma checagem falha significa que a tabela entregue seria **errada ou inutilizável**, não apenas surpreendente. Um hard gate para o notebook antes de qualquer write Delta, então uma carga ruim nunca chega ao modelo semântico.

Hard gates obrigatórios em todo notebook:

- **DataFrame final não vazio** — `df_final.count() == 0` levanta exceção. Um write vazio com `overwrite` apagaria silenciosamente uma tabela boa.
- **`data_processamento` presente** — a coluna de timestamp de escrita precisa existir.
- **Sem duplicata na chave primária declarada** — `count != distinct(pk).count` levanta exceção. Para chave composta, valide a tupla completa.
- **Sem nulo em ID/chave de negócio obrigatória** — uma linha cuja chave de entidade é nula não é endereçável a jusante; descarte-a na transformação com um motivo documentado, ou levante exceção aqui. Nunca deixe passar silenciosamente.

Hard gate obrigatório só em Gold:

- **Checagem de multiplicação de linhas por join (fan-out)** — para cada join entre Silvers, compare a contagem de linhas antes e depois contra a cardinalidade que a chave do join deveria ter. Um fato que fana silenciosamente porque uma "dimensão" não era única na chave é o defeito de Gold mais comum. Bloqueie o write quando a contagem pós-join exceder o grão esperado (seção 8 tem o padrão de join que documenta essa expectativa).

### 7.2 Tier 2 — aviso de observabilidade (`print [AVISO]`, não bloqueia)

Use quando uma quebra de threshold é um **sinal para investigar**, não prova de corrupção — uma distribuição que desviou, um bucket de de-para que cresceu. Avisos imprimem com prefixo `[AVISO]` claro e um número, para que um humano lendo o output decida. Não levante exceção nestes; uma carga com 1,2% em "Outro" em vez de 0,9% ainda é uma carga correta.

Todo notebook imprime, ao final, um bloco de observabilidade base (`ambiente, origem, destino, load_method, linhas_origem, linhas_destino, ids_nulos, ids_duplicados`) — gate ou não gate.

### 7.3 Catálogo completo de checagens

| Checagem | O que detecta | Tier default |
|---|---|---|
| DataFrame final vazio | overwrite apagando tabela boa | raise |
| Duplicata na chave primária | grão quebrado, fan-out a jusante | raise |
| Nulo em ID/chave de negócio obrigatória | linhas inendereçáveis | raise |
| `data_processamento` ausente | linhagem/controle incremental quebrado | raise |
| Multiplicação de linhas por join (Gold) | fan-out de fato por chave não-única | raise |
| Datas inválidas/fora do range | `9999-12-31`, `0001-01-01`, pré-`1900`, datas futuras onde impossível | raise se corrompe métrica-chave; senão warn |
| Valores negativos onde impossível | `valor_*` negativo, contagem negativa | raise se corrompe métrica; senão warn |
| Fatos órfãos após join | linhas de fato sem dimensão correspondente | warn (raise só se a dimensão é obrigatória) |
| Schema drift na origem | uma coluna de origem sumiu/foi renomeada entre execuções | raise — implementado como `validar_contrato_origem` (seção 7.7 avisa por quê), roda antes de qualquer leitura de origem, em toda execução |
| Resíduo de de-para/classificação | fração de linhas caindo no bucket catch-all (`Outro`, `Indefinido`) acima de um limiar | warn |
| Domínio de um label decodificado | um `codigo_*` produziu valor fora do conjunto conhecido | ver seção 6 (`unhandled_case_explicit`) |

Exemplos de limiares (Tier 2), como ilustração a espelhar e não a hardcodar: `origem_transacao = 'Outro'` deveria ser `< 1%`; `forma_transacao` em branco `< 1%`; `tipo_transacao = 'Indefinido'` `< 1%`; `tipo_pessoa` dentro de `{PF, PJ, Indefinido}`; sem data futura em `dt_ultima_transacao`.

### 7.4 Validação mínima (piso, não teto)

```python
# Valida volume, coluna de processamento e duplicidade de chave primaria.
def validar_minimo(df, pk: list = None):
    total = df.count()

    if total == 0:
        raise ValueError("[ERRO] DataFrame final esta vazio.")

    if "data_processamento" not in df.columns:
        raise ValueError("[ERRO] Coluna obrigatoria data_processamento ausente.")

    print(f"[OK] Total de registros: {total:,}")

    if pk:
        total_pk = df.select(*pk).dropDuplicates().count()

        if total != total_pk:
            raise ValueError("[ERRO] Chave primaria possui duplicidades.")

        print("[OK] PK sem duplicidades.")
```

`validar_minimo` é o piso, não o teto — cobre os três primeiros hard gates. Estenda-o (ou adicione checagens ao lado) para a regra de ID-nulo obrigatório e qualquer outra que se qualifique como "errado se violada".

### 7.5 Estágio único: uma query, todos os contadores

**Regra de performance:** colete todo contador Tier 1/Tier 2 através de **uma query com subqueries correlacionadas**, não uma ação `.filter().count()` separada por checagem — cada `.count()` dispara seu próprio job Spark, então um notebook com uma dúzia de checagens ad hoc paga uma dúzia de jobs onde uma query (um job) bastaria. Materialize o resultado da query uma vez como dict Python, depois avalie toda condição de raise/warn contra esse dict.

Como o último passo da cadeia (`gera_tabela_final`) retorna um DataFrame em vez de registrar view (seção 2), a query de métricas precisa de `df_final` registrado como temp view primeiro — esse registro é, ele mesmo, uma temp view, então ganha sua própria célula Markdown como qualquer outra:

```markdown
#### consolidado
`df_final` registrado como view para a query de métricas poder consultá-lo em SQL, junto com as origens.
```

```python
df_final.createOrReplaceTempView("consolidado")
```

```python
# 8. Data quality checks - gate obrigatorio antes do write.
# Uma query junta todos os contadores; o dict resultante decide raise (Tier 1) vs [AVISO] (Tier 2).

df_metricas = spark.sql("""
    SELECT
        (SELECT COUNT(*) FROM origem_silver) AS qt_origem,
        (SELECT COUNT(*) FROM consolidado) AS qt_gold,
        (SELECT COUNT(*) FROM consolidado WHERE id_entidade IS NULL) AS qt_chave_nula,
        (SELECT COUNT(*) FROM (
            SELECT id_entidade FROM consolidado GROUP BY id_entidade HAVING COUNT(*) > 1
        ) g) AS qt_grao_duplicado,
        (SELECT COUNT(*) FROM consolidado WHERE origem_transacao = 'Outro') AS qt_origem_outro
    FROM (SELECT 1)
""")
metricas = df_metricas.first().asDict()
for nome, valor in metricas.items():
    print(f"{nome}: {valor}")

# --- Tier 1: agrega todos os erros estruturais e levanta uma unica vez ---
erros = []
if metricas["qt_origem"] == 0:
    erros.append("origem vazia")
if metricas["qt_gold"] == 0:
    erros.append("consolidado Gold vazio")
if metricas["qt_chave_nula"] > 0:
    erros.append(f"{metricas['qt_chave_nula']:,} registros com chave nula")
if metricas["qt_grao_duplicado"] > 0:
    erros.append(f"{metricas['qt_grao_duplicado']:,} chaves duplicadas no grao")
if "data_processamento" not in df_final.columns:
    erros.append("coluna data_processamento ausente")

if erros:
    raise ValueError("Escrita bloqueada pelas validacoes: " + "; ".join(erros))
print("Validacoes estruturais concluidas. Escrita liberada.")

# --- Tier 2: residuos de de-para (investigar, nao bloquear) ---
pct_outro = 100 * metricas["qt_origem_outro"] / metricas["qt_gold"] if metricas["qt_gold"] else 0
if pct_outro >= 1.0:
    print(f"[AVISO] origem_transacao='Outro' em {pct_outro:.2f}% (esperado < 1%). Investigar de-para.")
else:
    print(f"[OK] origem_transacao='Outro' em {pct_outro:.2f}%.")
```

- `validar_minimo(df_final, pk=PRIMARY_KEY)` ainda roda primeiro como o piso (checagem de vazio, dedup de PK por contagem) — a query acima adiciona os contadores específicos da entidade em cima dele, não o substitui.
- Mantenha cada nome de contador no dict impresso, para que um humano lendo o output veja os mesmos números que a lógica de raise/warn usou, sem precisar re-executar nada.

Para Gold, adicione a checagem de multiplicação de linhas por join, ou como mais um par de subquery na query de métricas acima, ou isolada logo após o join quando a comparação é contra uma contagem-base fixa:

```python
# Multiplicacao de linhas: a Silver de fato nao pode crescer ao juntar com uma dimensao 1:1.
linhas_fato = spark.table("fato_base").count()
linhas_pos_join = df_join.count()
if linhas_pos_join > linhas_fato:
    raise ValueError(
        f"[ERRO] Join multiplicou linhas: {linhas_fato:,} -> {linhas_pos_join:,}. "
        "Chave da dimensao nao e unica no grao esperado."
    )
```

### 7.6 Cascatas conhecidas

Uma única causa raiz costuma disparar mais de um contador ao mesmo tempo — leia-os juntos antes de abrir investigações separadas:

- Uma origem vazia ou quase vazia aparece tanto como `qt_gold = 0` (ou contagem muito baixa) quanto como contagens altas de nulo em toda coluna de enriquecimento derivada dela — uma causa raiz, não duas.
- Fan-out de um join que não foi reduzido a uma linha por chave (pulando o padrão da seção 8) reaparece tanto como falha de multiplicação de linhas logo após aquele join, quanto de novo a jusante como `qt_grao_duplicado`/uma PK inválida na tabela consolidada final.
- Uma data ausente ou malformada numa linha levanta tanto um contador de chave-obrigatória-nula quanto um contador de órfão-de-calendário (a data não tem correspondência na dimensão calendário) — investigue como uma causa (a data de origem), não duas independentes.
- Um bucket residual alto num de-para (aviso Tier 2) é o indicador líder de que um novo valor de origem apareceu; re-rode a query de descoberta de domínio (seção 6) antes de editar o `CASE WHEN` às cegas.

### 7.7 Por que essas regras existem

Cada regra abaixo bloqueia uma classe conhecida de erro silencioso:

- **Watermark nula excluída silenciosamente** — uma coluna de watermark nula, tratada como "não elegível" em vez de "sempre elegível", excluiu uma fatia relevante (na casa de ~15–20%) de registros ativos de uma entidade migrada de sistema legado, sem erro nenhum. Correção: nulo em coluna de watermark sempre conta como elegível (seção 9.3).
- **Watermark estático degradando MERGE em full re-read** — deixar o valor de piso do watermark fixo (o valor "frio" do CSV/parâmetro) em toda execução faz o filtro nunca estreitar, e todo notebook `LOAD_METHOD=MERGE` degrada silenciosamente para ler a origem inteira a cada execução, mesmo a escrita sendo um upsert de verdade. Correção: recalcular o piso efetivo a partir do destino (seção 9.3).
- **Datas contaminadas num limite SCD2/histórico** — uma guarda de data inválida ausente ou mal posicionada numa tabela de histórico/vigência produziu sobreposição de vigências. Correção: aplicar a guarda de `tratar_timestamp` (seção 3) de forma consistente em toda coluna de data, inclusive em vigência SCD2.
- **Chave de associação nula em registro ativo** — uma chave de associação (grupo/vínculo) nula que deveria sempre existir para um registro em estado ativo passou despercebida por falta de checagem de nulo em chave obrigatória. Correção: seção 7.1, hard gate de nulo em ID/chave de negócio.

A prática recomendada é registrar cada bug real do projeto num histórico numerado de issues (`000`, `001`, `002`, ...) e amarrar explicitamente cada hard gate novo a um desses registros quando aplicável — isso torna a regra rastreável e evita que a mesma classe de bug reapareça sem ninguém lembrar por que o gate existe.

---

## 8. Padrão de join: grão declarado + cardinalidade validada

Antes de um join, a célula Markdown declara a chave do join, o tipo do join, e o grão que o resultado deveria ter. Esse é o contrato que a checagem de multiplicação de linhas (seção 7.1/7.5) verifica.

```markdown
#### transacoes_com_entidade
Join `transacoes` (fato, grão = transação) x `entidade_dim` (1 linha por `id_entidade`). LEFT, grão do fato preservado.
```

```python
# Join transacoes (fato, grao = transacao) x entidade_dim (1 linha por id_entidade). LEFT, grao preservado.
def gera_view_transacoes_com_entidade():
    spark.sql("""
        SELECT f.*,
               d.tipo_pessoa,
               d.desc_grupo_entidade
        FROM transacoes_base AS f
        LEFT JOIN entidade_dim AS d
          ON f.id_entidade = d.id_entidade
    """).createOrReplaceTempView("transacoes_com_entidade")


gera_view_transacoes_com_entidade()
```

- Prefira `F.broadcast(df_dim)` para dimensões/tabelas de referência pequenas; nunca faça broadcast de um fato grande.
- Um `LEFT JOIN` numa dimensão cuja chave é única preserva o grão do fato — o gate de qualidade em Gold precisa confirmar que a contagem de linhas não cresceu.
- Quando uma Gold é montada a partir de mais de duas Silvers, uma origem define o grão (a **base**) e as demais são **enriquecimento**. Leia a base primeiro, depois junte cada origem de enriquecimento já reduzida a exatamente uma linha por chave de join — nunca junte uma origem de enriquecimento ainda não reduzida direto na base, ou o grão fana silenciosamente. Nomeie cada passo `base_com_<origem>` para a cadeia ler como "base, depois enriquecida com X, depois com Y". Uma linha ausente numa origem de enriquecimento é esperado, não erro: a linha da base continua existindo com colunas de enriquecimento `NULL` — só levante exceção quando o join de fato mudar a contagem de linhas.
- Quando uma entidade pode ser ligada a outra por mais de um caminho (direto por FK às vezes nula, ou indireto via tabela-ponte), resolva a associação numa única view antes do enriquecimento — `UNION ALL` seguido de `SELECT DISTINCT` combina os caminhos candidatos e deduplica o par uma vez; quando uma única linha pode resolver sua chave a partir de duas colunas (não duas tabelas), use `COALESCE(col_direto, col_via_ponte)` num único `SELECT` em vez de union.

---

## 9. Write Delta: FULL vs. MERGE

Antes de gravar qualquer tabela Silver ou Gold, adicione `data_processamento`:

```python
df_final = adicionar_metadados_processamento(df_final)
```

### 9.1 FULL

Use para rebuilds pequenos/médios ou regras de negócio que exigem reconstrução completa:

```python
(
    df_final
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(f"{TARGET_SCHEMA}.{TARGET_TABLE}")
)
```

### 9.2 MERGE

Use quando existe uma chave primária confiável e semântica de upsert é necessária. Na primeira carga, quando a tabela destino ainda não existe, cai em FULL automaticamente:

```python
from delta.tables import DeltaTable

# Grava a tabela Delta em modo MERGE usando a chave primaria informada. Na primeira carga, faz FULL.
def gravar_merge(df, schema: str, tabela: str, pk: list):
    target_name = f"{schema}.{tabela}"
    if not spark.catalog.tableExists(target_name):
        gravar_full(df, schema, tabela)
        return
    delta_target = DeltaTable.forName(spark, target_name)
    condicao = " AND ".join([f"target.{c} = source.{c}" for c in pk])
    (
        delta_target.alias("target")
        .merge(df.alias("source"), condicao)
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )
    print(f"[OK] Merge executado: {target_name}")
```

### 9.3 Watermark: piso efetivo e nulo elegível

Para carga incremental metadata-driven, filtre a origem pelo watermark configurado quando habilitado. `WATERMARK_COLUMN` chega como lista (múltiplas colunas candidatas) — trate como fallback ordenado via `coalesce` (a primeira não-nula vence), e trate **uma coluna de watermark nula/ausente como sempre elegível** — do contrário `>= start_ts` avalia para `NULL` e `.filter()` descarta essa linha silenciosamente para sempre (comum em registros migrados de sistema legado sem a coluna de controle):

```python
def aplicar_watermark(df):
    colunas_watermark = [c for c in WATERMARK_COLUMN if c in df.columns]
    if WATERMARK_ENABLED and colunas_watermark:
        start_ts = F.date_sub(F.to_timestamp(F.lit(WATERMARK_START_VALUE)), WATERMARK_LOOKBACK_DAYS)
        coluna_efetiva = F.coalesce(*[F.col(c) for c in colunas_watermark])
        return df.filter(coluna_efetiva.isNull() | (coluna_efetiva >= start_ts))
    return df
```

`WATERMARK_START_VALUE` é um **piso de cold-start apenas** — o valor a usar na primeira vez que a tabela destino é construída, ou quando está vazia. Não é substituto de um watermark real: se você deixar o valor estático do CSV/parâmetro em toda execução, o filtro acima nunca estreita (tudo é `>= 1900-01-01`), e todo notebook `LOAD_METHOD=MERGE` degrada silenciosamente para ler a origem inteira a cada execução, mesmo a escrita sendo um upsert de verdade. Para todo notebook com `LOAD_METHOD=MERGE` e `WATERMARK_ENABLED=True`, recalcule o piso efetivo a partir do que já está no destino antes de filtrar a origem:

```python
def calcular_watermark_efetivo():
    target_name = nome_tabela(TARGET_SCHEMA, TARGET_TABLE)
    if not spark.catalog.tableExists(target_name):
        return WATERMARK_START_VALUE
    colunas_controle = [c for c in WATERMARK_CONTROL_COLUMNS if c in spark.table(target_name).columns]
    if not colunas_controle:
        return WATERMARK_START_VALUE
    max_processado = (
        spark.table(target_name)
        .select(F.max(F.coalesce(*[F.col(c) for c in colunas_controle])).alias("max_wm"))
        .collect()[0]["max_wm"]
    )
    return WATERMARK_START_VALUE if max_processado is None else max_processado.strftime("%Y-%m-%d %H:%M:%S")


if WATERMARK_ENABLED:
    WATERMARK_START_VALUE = calcular_watermark_efetivo()
```

Se o notebook grava suas colunas de watermark através de um tratamento que desloca o fuso (ex.: `tratar_timestamp_utc` com offset fixo), lembre de adicionar esse offset de volta antes de comparar contra a coluna bruta (UTC) da origem — do contrário o piso recalculado fica desalinhado pelo deslocamento e ou lê demais ou pula linhas genuinamente novas.

---

## 10. Vocabulário de evidência para regras de negócio inferidas

Toda regra de negócio que o notebook materializa e que não tem uma origem confirmada e homologada pelo cliente/PO precisa ser marcada com o rótulo de evidência correspondente — isso é parte do método, não específico de nenhuma nuvem:

| Rótulo | Significado |
|---|---|
| `CLIENTE_CONFIRMADO` | Registrado em reunião, nota ou requisito fornecido pelo cliente. |
| `SISTEMA_DOCUMENTADO` | Capacidade/comportamento descrito pelo fornecedor do sistema de origem; precisa ser validado contra o processo real. |
| `INFERIDO` | Hipótese consistente com as evidências disponíveis, ainda não confirmada pelo negócio. |
| `PENDENTE_VALIDACAO` | Evidência insuficiente, ou decisão de negócio em aberto. |
| `SIMULADO` | Criado para protótipo, mock ou teste — não é dado oficial. |

Mais dois eixos ortogonais a aplicar junto: **implantação** (`AS_IS` / `PARCIAL` / `TO_BE`) e **validação** (`VALIDADO` / `PENDENTE` / `CONFLITANTE`). Um produto marcado `TO_BE` nunca pode aparecer como implementado sem o artefato e a verificação correspondentes.

Na prática, quando o notebook materializa uma regra de negócio sem ID canônico ainda homologado (um flag provisório, um de-para aguardando sign-off do PO, uma associação resolvida por convenção em vez de regra confirmada), adicione uma célula Markdown **"Decisões provisórias a revisar com o PO"** logo após o cabeçalho/changelog. Declare cada questão em aberto diretamente (o que a regra faz hoje, e qual alternativa o PO precisa confirmar), junto com o rótulo de evidência aplicável, para que a ambiguidade fique visível no próprio notebook — não só no histórico de conversa. Quando a regra for confirmada e ganhar um ID canônico, substitua a entrada provisória por uma referência a esse ID e remova a célula se nada mais provisório restar.

---

## 11. Notebook import-safe (`.ipynb` editado fora da UI nativa da plataforma)

Qualquer `.ipynb` editado fora da interface nativa da plataforma (programaticamente, em VS Code, via tooling/agente) precisa ser **limpo antes de ser reimportado**. Um `.ipynb` malformado nesse sentido pode falhar o import da plataforma de forma obscura (ver o overlay da sua nuvem para o sintoma exato).

Dois culpados recorrentes:

1. **Outputs de célula salvos** — especialmente um output de `error`, cujo `traceback` contém códigos de escape ANSI. O parser de import de algumas plataformas rejeita esses caracteres de controle e falha o arquivo inteiro. Outputs de `display_data`/metadados de execução também aumentam o risco.
2. **`source` armazenado como uma string única** em vez de uma lista de linhas. O formato nativo de notebook armazena `source` como lista de linhas; alguns editores/ferramentas escrevem como uma string só, o que torna o import frágil.

A limpeza correta (idempotente) é: converter `source` de string para lista de linhas quando necessário, zerar `outputs`/`execution_count` de toda célula de código, e manter o arquivo como **UTF-8 sem BOM**, preservando `nbformat`/`nbformat_minor` e o bloco `metadata` específico da plataforma (kernel, ambiente de computação, dependências de lakehouse/cluster). Essa limpeza é automatizada pelo script `limpar_notebook_import.py`: rode-o sempre antes de reimportar um notebook editado fora da UI nativa. A ação manual equivalente, dentro da própria plataforma, é **"Limpar todos os outputs"**, usada sempre que a última execução tiver terminado em erro. Ver `07-mecanismos-e-hooks.md` (mecanismo M2) para a invocação exata do script e o hook associado.

---

## 12. Estrutura de 11 seções do notebook

Esta sequência é **igual nas duas nuvens** — o que muda é só o formato da célula de Parâmetros (seção 4 abaixo, ver overlays):

1. Cabeçalho e metadados de destino (inclui histórico de atualizações e, quando aplicável, a célula "Decisões provisórias a revisar com o PO" — seção 10)
2. Spark configs
3. Imports
4. Parâmetros
5. Funções auxiliares
6. Leitura das tabelas de origem (valide o contrato de origem — `validar_contrato_origem`, checagem de schema drift da seção 7.3 — antes da primeira leitura)
7. Transformações (cadeia de temp views, sem CTE — uma view por célula, Markdown antes de cada uma — seção 2)
8. Data quality checks (métricas coletadas numa única query com subqueries correlacionadas — seção 7.5)
9. Tabela final
10. Write Delta
11. Catalogação (sempre por último, ver seção 13) e checklist de produção

Use estes rótulos de seção padrão em Markdown quando útil:

```markdown
#### Spark Configs
#### Import libraries and packages
#### Parameters
#### Helping functions
#### Tables importing
#### Tables transforming
#### Data quality checks
#### Final table
#### Write table
```

Validação de contrato de origem — roda em **toda** execução, não só quando o notebook é escrito, e é a implementação concreta do check "schema drift na origem" (seção 7.3):

```python
# Contrato das origens: tabela -> colunas obrigatorias que a transformacao usa.
CONTRATO_ORIGENS = {
    nome_tabela(SOURCE_SCHEMA, "Entidade"): ["EntidadeId", "TipoDocumento", "DataCadastro"],
    nome_tabela(SILVER_SCHEMA, "cad_entidade"): ["id_entidade", "tipo_pessoa"],
}

# Valida existencia da tabela e das colunas obrigatorias antes de ler qualquer origem.
def validar_contrato_origem(contrato: dict):
    erros = []
    for tabela, colunas_obrigatorias in contrato.items():
        if not spark.catalog.tableExists(tabela):
            erros.append(f"tabela inexistente: {tabela}")
            continue
        colunas_reais = {c.name.lower() for c in spark.catalog.listColumns(tabela)}
        ausentes = [c for c in colunas_obrigatorias if c.lower() not in colunas_reais]
        if ausentes:
            erros.append(f"{tabela} sem colunas: {', '.join(ausentes)}")
    if erros:
        raise ValueError("Contrato das origens invalido: " + "; ".join(erros))
    print(f"Contrato de {len(contrato)} origem(ns) validado.")


validar_contrato_origem(CONTRATO_ORIGENS)
```

Declare só as colunas que a transformação de fato referencia, não o schema completo da origem — a checagem deve falhar quando uma coluna que o notebook depende some ou é renomeada, não em toda mudança de schema não relacionada. Colete todo erro antes de levantar exceção (como acima), para que uma execução quebrada reporte toda tabela/coluna faltante de uma vez.

---

## 13. Catalogação — sempre a etapa final

Todo notebook termina com uma etapa de catalogação, depois de "Write table", nunca antes. Duas regras não negociáveis:

- **Roda depois do write**, porque um write com `overwriteSchema=true` descarta os comentários da execução anterior — catalogar antes seria trabalho perdido.
- **Nunca levanta exceção.** A carga já aconteceu; falta de privilégio para comentar (ex. `MODIFY`/`COMMENT`) não pode reverter um write que já foi bem-sucedido. Trate falha de catalogação como aviso, não como gate.

O padrão SQL é `COMMENT ON TABLE` para o resumo de negócio da tabela, mais `ALTER TABLE ... ALTER COLUMN ... COMMENT` por coluna relevante — funciona tanto sobre um catálogo gerenciado (Unity Catalog) quanto sobre uma tabela Delta gerenciada de lakehouse, porque é DDL padrão do Spark SQL, não um recurso exclusivo de uma nuvem.

Mantenha o **dicionário de comentários separado da aplicação genérica** do notebook — não misture o texto de negócio (o que cada tabela/coluna significa, para quem consulta o catálogo depois) com a lógica de transformação. Um arquivo/estrutura de dados à parte (por tabela ou por domínio) que mapeia `tabela/coluna -> comentário de negócio` mantém essa documentação editável por alguém não-técnico e reutilizável entre notebooks que tocam a mesma tabela, sem exigir que a pessoa edite Spark.

Quando o projeto usa uma flag de tipo de carga (FULL vs. incremental), é comum condicionar a catalogação para sempre rodar em carga FULL e só rodar em carga incremental quando forçada explicitamente — evita custo de metadados repetido numa tabela que já foi comentada, mas mantém a opção de forçar quando o dicionário de comentários mudou.

---

## Ver também

- `03a-fabric-overlay.md` — arquitetura Mirrored DB → Silver → Gold, célula de parâmetros formato Fabric, orquestração metadata-driven CSV, o que é proibido.
- `03b-databricks-overlay.md` — arquitetura Bronze físico → Silver → Gold, Unity Catalog, Databricks Jobs vs. Lakeflow/DLT, Asset Bundles, governança.
