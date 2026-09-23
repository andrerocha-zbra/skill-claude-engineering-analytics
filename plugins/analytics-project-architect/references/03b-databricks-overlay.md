# Databricks — overlay (diferenças vs. o núcleo)

Este arquivo assume `03-datalake-core.md` já lido. Aqui só o que **muda de verdade** ao trabalhar em Databricks: arquitetura, namespace, parâmetros, ingestão, orquestração, CI/CD e governança. Toda disciplina de transformação, quality gates, convenção de coluna e catalogação é a do núcleo, sem alteração.

> **Overlay menos consolidado que o de Fabric.** Trate o que segue como ponto de partida sólido, não como convenção validada por repetição, e confirme contra a realidade do workspace/cluster policy/Unity Catalog do cliente antes de assumir como definitivo.

---

## Arquitetura

```text
Ingestão (Auto Loader / connectors) -> Bronze físico -> Silver -> Gold
```

Diferente do default Fabric, no Databricks **o Bronze físico é comum**: dado bruto ou minimamente normalizado, imutável, existe fisicamente como tabela Delta para permitir replay e histórico independente da origem. Silver e Gold seguem a mesma disciplina do núcleo.

---

## Namespace: Unity Catalog de 3 níveis

Toda tabela é endereçada como `catalog.schema.tabela` — não `schema.tabela` como em Fabric:

```text
<catalogo>.bronze.<entidade>
<catalogo>.silver.<entidade>
<catalogo>.gold.<produto>
```

Catalog costuma variar por ambiente (`<projeto>_dev`, `<projeto>_prod`), schema por camada, e dentro de Silver/Gold por domínio de negócio — mesma lógica de organização do núcleo, um nível a mais no nome.

---

## Parâmetros via `dbutils.widgets`

O equivalente Databricks à célula com tag `parameters` do Fabric. Sem tag especial — os widgets são a interface de parametrização nativa, lidos de volta como string:

```python
dbutils.widgets.text("ENV", "PRD")
dbutils.widgets.text("TARGET_TABLE", "<entidade>")
dbutils.widgets.dropdown("tipo_carga", "FULL", ["FULL", "INCREMENTAL"])

ENV = dbutils.widgets.get("ENV")
TARGET_TABLE = dbutils.widgets.get("TARGET_TABLE")
TIPO_CARGA = dbutils.widgets.get("tipo_carga")
```

Um padrão comum: usar `dbutils.widgets.dropdown` para o tipo de carga (`FULL`/`INCREMENTAL`) em vez de texto livre, para restringir o valor na UI do notebook e no Job.

---

## Ingestão Bronze via Auto Loader

Para ingestão incremental de arquivos em Bronze, use `cloudFiles` em vez de leitura batch simples — ele mantém schema inference incremental e checkpoint de progresso:

```python
(
    spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "parquet")
    .option("cloudFiles.schemaLocation", f"/Volumes/{CATALOG}/_schemas/{TABELA}")
    .load(origem)
    .writeStream
    .option("checkpointLocation", f"/Volumes/{CATALOG}/_chk/{TABELA}")
    .trigger(availableNow=True)
    .toTable(f"{CATALOG}.bronze.{TABELA}")
)
```

- `schemaLocation` e `checkpointLocation` vivem em **Volumes** (não DBFS/mounts legados).
- `trigger(availableNow=True)` processa todo o backlog disponível e para — o padrão certo para um job agendado, em vez de um stream contínuo `always-on`.

---

## Orquestração — duas opções

Databricks não tem um CSV de orquestração nativo como o Fabric; a escolha é arquitetural:

### Opção 1 — Databricks Jobs (imperativo)

Um Job com uma task por notebook/entidade, dependências explícitas entre tasks (`depends_on`), `execution_order` fica implícito no grafo de dependências em vez de uma coluna numérica. Parâmetros por task; retries e timeout na configuração do Job.

Para **manter o padrão metadata-driven** equivalente ao CSV do Fabric — um Job pode ler uma tabela/CSV de controle numa task inicial e iterar sobre as entidades via uma task `for_each_task`, espelhando o papel do CSV de orquestração do Fabric:

```yaml
resources:
  jobs:
    pipeline_silver_gold:
      name: pipeline_silver_gold
      tasks:
        - task_key: ler_controle
          notebook_task:
            notebook_path: ./jobs/ler_controle_orquestracao.py
        - task_key: executar_por_entidade
          depends_on:
            - task_key: ler_controle
          for_each_task:
            inputs: "{{tasks.ler_controle.values.entidades}}"
            task:
              task_key: executar_entidade
              notebook_task:
                notebook_path: "{{input.notebook_path}}"
                base_parameters:
                  TARGET_TABLE: "{{input.target_table}}"
                  LOAD_METHOD: "{{input.load_method}}"
```

### Opção 2 — Lakeflow / Delta Live Tables (declarativo)

Defina `@dlt.table`/`@dlt.expect_or_drop` e deixe o runtime resolver dependência entre tabelas, checagem de qualidade e incrementalidade. Bom para pipelines Bronze→Silver com expectativas de qualidade declaradas diretamente no código:

```python
import dlt

@dlt.table(name="entidade")
@dlt.expect_or_drop("pk_nao_nula", "id_entidade IS NOT NULL")
def entidade():
    return spark.readStream.table("LIVE.bronze_entidade").select(...)
```

**Quando usar cada uma:** Jobs imperativos quando o projeto precisa do controle explícito de sequência/retry por task que o CSV metadata-driven já dá em Fabric, ou quando a equipe já pensa em termos de orquestração explícita. DLT/Lakeflow quando o pipeline é majoritariamente Bronze→Silver com regras de qualidade que fazem sentido como `expect`/`expect_or_drop` declarativos e o time aceita o runtime gerenciar a execução — nesse caso as checagens do núcleo (seção 7) viram `@dlt.expect*` em vez de `raise ValueError` explícito, e a diferença Tier 1/Tier 2 mapeia para `expect_or_drop`/`expect_or_fail` (bloqueia) vs. `expect` (só registra métricas).

---

## CI/CD nativo: Databricks Asset Bundles

Cada projeto/pipeline tem seu `datalake/_tech-sync/databricks.yml`, na raiz da pasta sincronizada, com targets `dev`/`prod`:

```yaml
# datalake/_tech-sync/databricks.yml — raiz da pasta sincronizada do pipeline/projeto
bundle:
  name: <nome_do_pipeline>

include:
  - resources/*.yml

targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://<workspace-dev>.azuredatabricks.net
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/dev

  prod:
    mode: production
    workspace:
      host: https://<workspace-prod>.azuredatabricks.net
      root_path: /Workspace/Shared/.bundle/${bundle.name}/prod
    run_as:
      service_principal_name: <service-principal-prod>
```

Comandos de deploy:

```bash
databricks bundle validate -t dev
databricks bundle deploy -t dev

databricks bundle validate -t prod
databricks bundle deploy -t prod
```

`bundle validate` checa a sintaxe/referências do bundle antes de qualquer chamada de API; `bundle deploy -t <target>` sincroniza notebooks/Jobs/DLT pipelines definidos em `resources/*.yml` para o workspace do target. Mantenha `dev` como `default: true` para que rodar sem `-t` explícito nunca afete produção por engano.

Isto é a parte de autoria do pipeline (o `databricks.yml` do próprio projeto). Para como o Git folder do workspace do cliente se conecta a essa pasta (sparse checkout por cone pattern, CI de PR, escolha de nuvem por projeto), ver `08-cicd-fabric-databricks.md`.

---

## Governança (Unity Catalog)

- Permissões via `GRANT <privilegio> ON <catalog|schema|table> TO <principal>` — não há equivalente disso em Fabric (que usa permissão de workspace/item).
- Lineage e discovery são nativos do Unity Catalog — não exigem instrumentação adicional no notebook.
- **Volumes** substituem DBFS e mounts legados para arquivos (checkpoints, schema location, arquivos brutos de ingestão).
- Qualidade: `@dlt.expect*` dentro de um pipeline DLT, ou `validar_minimo(df, pk)` (mesmo helper do núcleo) fora de DLT — não são dois padrões concorrentes, são o mesmo princípio (Tier 1/Tier 2) em duas superfícies de execução diferentes.

---

## Extras de performance específicos de Databricks

Além dos princípios de performance do núcleo (projetar/filtrar cedo, broadcast só em dimensão pequena, AQE ligado, validar cardinalidade antes do join), o Databricks expõe mecanismos que Fabric não tem:

- **Liquid Clustering** (ou `OPTIMIZE` + `ZORDER` em workspaces sem Liquid Clustering habilitado) em fatos grandes, para manter data skipping eficiente sem reparticionamento manual.
- **`VACUUM`** na retenção definida pelo projeto — remove arquivos Delta órfãos de versões antigas; não rode com retenção abaixo do default sem confirmar que nenhum consumidor depende de time travel além dela.
- **Photon**, quando disponível no cluster/warehouse, para acelerar execução de queries Spark SQL sem mudança de código.

---

## Consumo por Power BI

Gold em Delta/Unity Catalog conecta ao Power BI via conector Databricks nativo (DirectQuery ou Import). A engine de dados ser Databricks em vez de Fabric não muda a camada de modelagem/DAX — segue a referência de Power BI do método normalmente.

---

## Ver também

- `03-datalake-core.md` — disciplina de transformação, quality gates, write Delta, catalogação (comum às duas nuvens).
- `03a-fabric-overlay.md` — o mesmo overlay para Microsoft Fabric.
