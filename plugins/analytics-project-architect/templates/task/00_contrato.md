# Task {{tNN}} — 00: Pré-requisitos (índice)

> **Anexo opcional de task.** Não é mais o padrão obrigatório de toda task — isso hoje é `templates/task/descricao-tarefa.md`. Use este arquivo (e os demais estágios `01_datalake.md`–`04_frontend.md`) só quando a task for genuinamente multi-etapa técnica (datalake → modelagem → DAX → frontend); eles moram em `tasks/TASK-NNN__slug/`, ao lado de `descricao-tarefa.md`.

> Ler primeiro. Aponta para o contrato de dados e as regras que **toda** a task usa.

- **Contrato de dados:** `00_contrato-dados.md` da entidade/domínio (em `powerbi/<dominio>/<pagina-ou-entidade>/`, em `specs/` da reunião de origem, ou transversal em `@client_context/`, conforme o alcance)
- **Regras de negócio:** `00_regras-negocio.md` (IDs R#, mesmo critério de local acima)
- **Spec de origem:** {{caminho da ESPEC}}

## Objetivo da task

{{1-2 frases: o que esta task entrega e para qual necessidade (D#).}}

## Estágios e dependências

| Arquivo | Estágio | Depende de |
|---------|---------|------------|
| 01_datalake.md | Dados | 00 |
| 02_modelagem.md | Modelagem | 01 (rodado) |
| 03_dax.md | DAX | 02 |
| 04_frontend.md | Frontend | 03 (bind final) |

## Pode paralelizar

- {{ex.: layout do frontend enquanto o datalake roda}}
