# Task {{tNN}} — Estágio 03: DAX

> **Anexo opcional de task.** Não é mais o padrão obrigatório de toda task — isso hoje é `templates/task/descricao-tarefa.md`. Use este arquivo (e os demais estágios) só quando a task for genuinamente multi-etapa técnica (datalake → modelagem → DAX → frontend); ele mora em `tasks/TASK-NNN__slug/`, ao lado de `descricao-tarefa.md`.

> Após modelagem. Ref: `references/04-powerbi-modelagem-dax.md`. Escrita via MCP/CLI (M1); DAX longo em arquivo `.dax` cru.

## Medidas

| Nome (`Página - NN.N: Medida`) | displayFolder | O que faz |
|--------------------------------|---------------|-----------|
| {{...}} | {{Regras de Negócio / Geral / ...}} | {{business}} |

## Regras reutilizadas

- {{Regras de Negócio - Janela de Atividade (R2)}}

## Verificação (M3)

- `dax_query` de sanity: contagens batem, domínios válidos, ordens de grandeza vs. Ata.
