# Task {{tNN}} — Estágio 01: Datalake

> **Anexo opcional de task.** Não é mais o padrão obrigatório de toda task — isso hoje é `templates/task/descricao-tarefa.md`. Use este arquivo (e os demais estágios) só quando a task for genuinamente multi-etapa técnica (datalake → modelagem → DAX → frontend); ele mora em `tasks/TASK-NNN__slug/`, ao lado de `descricao-tarefa.md`.

> Pré-requisitos: `00_contrato-dados.md`, `00_regras-negocio.md`. Núcleo cloud-agnóstico: `references/03-datalake-core.md`. Overlay: {{Fabric → references/03a-fabric-overlay.md | Databricks → references/03b-databricks-overlay.md}}.

## Escopo

{{O que enriquecer/criar no Silver/Gold. Referenciar IDs (DL-##, R#).}}

## Notebook(s)

- `{{NB_...}}` — {{entidade}} — destino `{{schema.tabela}}` ({{FULL/MERGE}})

## Passos

1. {{ler origem}}
2. {{transformação: mapear_*/derivar_*/tratar_*}}
3. {{DQ: validar_minimo, contagens}}
4. {{write Delta + data_processamento}}
5. {{atualizar metadata_driven (Fabric) / Asset Bundle resources (Databricks)}}

## Verificação (M3)

- {{groupBy de enum, total inalterado, domínios válidos}}
