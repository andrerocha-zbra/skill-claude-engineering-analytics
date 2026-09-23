# Contrato de Dados — {{DOMÍNIO}}

> **Fonte de verdade compartilhada.** Mudou nome/tipo de coluna? Atualiza aqui **primeiro**, depois no código.
> **Tabela(s):** `{{schema}}.{{tabela}}` · **Grão:** {{1 linha = ...}} · **Carga:** {{FULL/MERGE}} · **PK:** {{coluna}}

## Colunas

| Coluna | Tipo | Regra / origem | Novo? | Exemplo |
|--------|------|----------------|-------|---------|
| {{id}} | string | {{origem}} | não | {{...}} |
| {{campo}} | {{tipo}} | {{regra ou mapear_*/derivar_*}} | **sim** | {{...}} |

Legenda **Novo?**: "sim" = coluna entregue por esta task (ainda não existe fisicamente).

## Enums / decodificações

| Coluna código | Coluna rótulo | Mapeamento |
|---------------|---------------|------------|
| {{codigo_x}} | {{x / descricao_x}} | {{0→A, 1→B, ...; fallback}} |

## Consumidores

- {{Power BI Doadores / medida X / visual Y}}
