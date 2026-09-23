# Regras de Negócio — {{DOMÍNIO}}

> Definições canônicas numeradas. Referenciar o ID (`R#`) em notebooks/DAX/specs por comentário.

| ID | Regra | Definição (pseudocódigo / condição) | Fonte |
|----|-------|--------------------------------------|-------|
| R1 | {{nome}} | {{ex.: "pago" = IsDeleted=False AND (RemessaStatus=8 OR StatusLegacy=5)}} | {{ata/cliente}} |
| R2 | {{janela de atividade}} | {{ex.: 12 meses fixos}} | |

## Exceções e casos de borda

- {{ex.: doador falecido continua na base, mas fora de "ativo"}}

## Glossário

- **{{termo}}** — {{definição}}
