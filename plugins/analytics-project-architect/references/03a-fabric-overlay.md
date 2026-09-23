# Microsoft Fabric — overlay (diferenças vs. o núcleo)

Este arquivo assume `03-datalake-core.md` já lido. Aqui só o que **muda de verdade** ao trabalhar em Microsoft Fabric: arquitetura, formato de parâmetros, orquestração, e as pegadinhas específicas da plataforma. Toda disciplina de transformação, quality gates, convenção de coluna, write Delta e catalogação é a do núcleo, sem alteração.

---

## Arquitetura

```text
Mirrored Database -> Silver -> Gold
```

**Sem Bronze físico por default.** A mirrored database é tratada como a origem operacional/raw. Só crie uma camada Bronze física quando o projeto precisar explicitamente de: histórico independente, replay, snapshots, auditoria regulatória, ou desacoplamento da disponibilidade da origem espelhada. Fora esses casos, Silver lê diretamente da mirrored database.

---

## Proibido (features Databricks-only)

Evite estas features salvo pedido explícito do usuário — elas não existem ou não fazem sentido no modelo de Fabric:

- **DBFS**
- **Widgets `dbutils`** — Fabric usa a célula com tag `parameters` (Papermill), não widgets.
- **Unity Catalog** — Fabric usa lakehouse/schema gerenciado, não um catálogo de 3 níveis.
- Um dicionário de ambiente tipo `CONFIG = {"DEV": {...}, "PRD": {...}}` com `TABLE_PATH`/`STORAGE_ACCOUNT`/`abfss://` explícito, ou `CREATE TABLE ... USING DELTA LOCATION` para tabela externa — Fabric resolve ambiente/destino via a célula de parâmetros + o CSV de orquestração, e tabelas de lakehouse são gerenciadas (sem location declarada no notebook).

**Não é proibido:** `%run <notebook>` — Fabric suporta nativamente como mecanismo de notebook-reference. Só não use por padrão se o projeto ainda não tiver adotado um notebook de biblioteca compartilhada; mantenha helpers de plumbing definidos por notebook até o usuário decidir explicitamente introduzir um.

---

## Parâmetros: duas células após `#### Parameters`

**Célula 1 — tag `parameters`** (Fabric/Papermill usa esta célula para injetar valores do pipeline em runtime; adicione `"tags": ["parameters"]` nos metadados da célula). Todo valor de lista é armazenado como texto pipe-separated:

```python
# Main Conditions
ENV = "PRD"
IS_ACTIVE = True

# Domain-driven
DOMAIN = "<Domain>"
OWNER = "<Owner>"
SUBDOMAIN = "<Subdomain>"
BUSINESS_ENTITY = "<Entity>"
DDD_TYPE = "<Type>"            # Entity | Aggregate | ValueObject | Event | Service

# Catalog
SOURCE_SYSTEM = "<sistema_origem_x>"    # pipe se multiplos: "sistema_origem_x|api_y"
LAKEHOUSE = "<lakehouse>"
SOURCE_SCHEMA = "<schema_espelhado>"
SILVER_SCHEMA = "<silver>"
GOLD_SCHEMA = "<gold>"
TARGET_SCHEMA = "<target_schema>"
TARGET_TABLE = "<entidade>"
PRIMARY_KEY = "<pk_column>"             # pipe se composta: "id_col1|id_col2"

# Ingestion
LOAD_METHOD = "MERGE"                   # MERGE | FULL | APPEND
TIMEZONE = "America/Sao_Paulo"
WATERMARK_ENABLED = True
WATERMARK_COLUMN = "LastModified"
WATERMARK_START_VALUE = "1900-01-01 00:00:00"
WATERMARK_LOOKBACK_DAYS = 1
```

**Célula 2 — célula de código comum imediatamente depois** (converte as strings pipe em listas Python):

```python
# Converte parametros pipe-separated para listas Python. O `or ""` e obrigatorio: quando o
# Fabric Pipeline injeta um parametro vazio da orquestracao CSV, o valor chega como None
# (nao ""), e None.split("|") explode com AttributeError em runtime.
SOURCE_SYSTEM = (SOURCE_SYSTEM or "").split("|")
PRIMARY_KEY = (PRIMARY_KEY or "").split("|")
WATERMARK_COLUMN = (WATERMARK_COLUMN or "").split("|")
```

**Cuidado real, não teórico:** o Fabric Pipeline injeta `None` (não `""`) quando o campo correspondente do CSV de orquestração está vazio. `None.split("|")` explode com `AttributeError` em runtime — por isso o `(X or "").split("|")` na célula 2 não é estilo, é obrigatório.

O grupo Domain-driven mapeia direto para as colunas do CSV de orquestração: `domain`, `subdomain`, `ddd_type`, `business_entity`, `owner`.

---

## Orquestração metadata-driven (CSV único)

Fonte única de verdade da orquestração: `datalake/_tech-sync/metadata_driven/metadata_driven_orchestration.csv`, delimitador **`;`** (não vírgula), sem aspas externas nos campos. Colunas de lista (`source_system`, `primary_key`) usam pipe `|` como separador — texto puro, sem colchetes nem aspas.

23 colunas, na ordem (principais destacadas):

`is_active` · `execution_order` · `layer` · `domain` · `subdomain` · `ddd_type` · `business_entity` · **`notebook_name`** · `owner` · **`source_system`** · `business_definition` · **`primary_key`** · **`target_schema`** · **`target_table`** · **`load_method`** · `watermark_enabled` · `watermark_column` · `watermark_start_value` · `watermark_lookback_days` · `env` · `timeout_minutes` · `retry_count` · **`notebook_id`**

- `notebook_id` (última coluna) pode ficar vazio até o notebook ser publicado no Fabric. O `ForEach` do pipeline prefere `notebook_id` para execução; `notebook_name` fica só para legibilidade, lineage e rastreabilidade no repositório.
- **Regra crítica: o destino sempre vem do CSV, nunca hardcoded no notebook.** `TARGET_SCHEMA`/`TARGET_TABLE`/`LOAD_METHOD` na célula de parâmetros são valores de dev/preview — em execução real do pipeline, o Fabric Pipeline os sobrescreve a partir da linha correspondente do CSV.
- Ao criar ou entregar um notebook novo, sempre anexe a linha de metadados correspondente ao CSV.

---

## Import de notebook editado fora do Fabric: `400 Bad Request`

O sintoma concreto da seção "Notebook import-safe" do núcleo, em Fabric: reimportar um `.ipynb` malformado pela UI web ("Import notebook") falha com `400 Bad Request` (`createArtifact`/`uploadNotebook`, `pbi.error` com `exceptionCulprit: 1`). Os dois culpados do núcleo (outputs de erro com ANSI escape codes, `source` como string única em vez de lista de linhas) são exatamente o que causa esse 400 em Fabric. Rode a limpeza (`limpar_notebook_import.py`, ver núcleo) antes de todo reimport.

Se um import já limpo continuar dando 400, suspeite de um `dependencies.environment`/`lakehouse` no metadata do notebook apontando para um workspace diferente do destino — e importe um notebook de cada vez para isolar o culpado.

Ver também `07-mecanismos-e-hooks.md` (mecanismo M2) e `08-cicd-fabric-databricks.md` para como o Git integration do Fabric e o CI leve de PR se encaixam nisso.

---

## Dois modos de timezone podem coexistir deliberadamente

`tratar_timestamp_utc` (núcleo, seção 3) pode ter duas implementações diferentes no mesmo projeto Fabric, e isso é intencional, não inconsistência a "corrigir":

- **DST-aware** — honra a história de horário de verão via fuso nomeado:

  ```sql
  ... ELSE from_utc_timestamp(to_timestamp(col), 'America/Sao_Paulo') END
  ```

- **Offset fixo** (ex. `-3h`) — usado quando é preciso paridade byte-a-byte com uma view SQL legada homologada que usa `DATEADD(HOUR, -3, ...)` em vez de um fuso DST-aware:

  ```sql
  ... ELSE to_timestamp(col) - INTERVAL 3 HOURS END
  ```

  Este modo está acoplado ao ajuste equivalente (`+3h` de volta) em `calcular_watermark_efetivo` (núcleo, seção 9.3) — mudar um sem o outro faz o piso do watermark reler demais ou pular linhas novas.

**Nunca unifique os dois modos sem confirmar com o consumidor a jusante.** Use a forma DST-aware por padrão para timestamps cadastrais/históricos; reserve o offset fixo apenas para onde paridade com uma view homologada específica é um requisito confirmado — não uma preferência de estilo.

---

## Ver também

- `03-datalake-core.md` — disciplina de transformação, quality gates, write Delta, catalogação (comum às duas nuvens).
- `03b-databricks-overlay.md` — o mesmo overlay para Databricks.
