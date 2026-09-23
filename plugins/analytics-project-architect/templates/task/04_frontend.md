# Task {{tNN}} — Estágio 04: Frontend

> **Anexo opcional de task.** Não é mais o padrão obrigatório de toda task — isso hoje é `templates/task/descricao-tarefa.md`. Use este arquivo (e os demais estágios) só quando a task for genuinamente multi-etapa técnica (datalake → modelagem → DAX → frontend); ele mora em `tasks/TASK-NNN__slug/`, ao lado de `descricao-tarefa.md`.

> Fatia vertical primeiro: uma página completa antes de replicar. Ref: `references/05-powerbi-frontend.md`. Nativo onde basta; HTML onde agrega.

## Páginas / visuais

| Página | Visual | Técnica (nativo / HTML-CSS / JS+SVG) | Medidas que alimentam |
|--------|--------|--------------------------------------|-----------------------|
| {{...}} | {{card/donut/tabela}} | {{...}} | {{...}} |

## Design

- Tokens: `@client_context/design-system/` (paleta, fontes, radius).
- Tabela que exporta p/ Excel = nativa.

## Verificação

- Bind das medidas correto; empty state tratado; interatividade (tooltip) conforme spec.
