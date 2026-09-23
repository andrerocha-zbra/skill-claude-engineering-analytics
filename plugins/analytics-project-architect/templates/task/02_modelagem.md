# Task {{tNN}} — Estágio 02: Modelagem

> **Anexo opcional de task.** Não é mais o padrão obrigatório de toda task — isso hoje é `templates/task/descricao-tarefa.md`. Use este arquivo (e os demais estágios) só quando a task for genuinamente multi-etapa técnica (datalake → modelagem → DAX → frontend); ele mora em `tasks/TASK-NNN__slug/`, ao lado de `descricao-tarefa.md`.

> Só começa após o estágio 01 rodar e o refresh trazer as colunas. Ref: `references/04-powerbi-modelagem-dax.md`. Escrita via MCP/CLI (M1).

## Escopo

{{Colunas calculadas, relacionamentos, tipos/formatação, ocultar técnicas, limpeza.}}

## Mudanças

| Objeto | Ação | Detalhe |
|--------|------|---------|
| {{tabela.coluna}} | tipar/formatar | {{summarizeBy: none; formatString}} |
| {{relacionamento}} | criar/ajustar | {{from→to, cardinalidade, direção}} |

## Verificação

- Ler de volta (MCP List/Get); relacionamento com cardinalidade esperada.
