# Prompt — criar (ou revisar) uma Gold

## Como usar

Copie o bloco de "Prompt" abaixo e cole como pedido para o agente, trocando `<ENTIDADE>` e
`<SILVERS_DE_ORIGEM>` (uma ou mais) pelos valores reais. Se a origem ainda não existir
(Silver correspondente), rode primeiro `criar_silver.md`.

Prefira colar este prompt no início de uma conversa nova.

---

## Prompt

```
Preciso criar (ou revisar) a Gold de `<ENTIDADE>`, a partir de `<SILVERS_DE_ORIGEM>`,
seguindo a skill `analytics-project-architect` vendorizada em
`.claude/skills/analytics-project-architect/` e os arquivos de governança do projeto
(`CLAUDE.md`, `PROJETO.md`, `@client_context/`).

Regra de execução: faça as leituras você mesmo, nesta mesma conversa. Não delegue a um
subagente a menos que uma busca direta falhe ou volte ambígua.

Regra de conteúdo: o notebook gerado nunca cita, por nome, `CLAUDE.md`, `PROJETO.md`, a
skill, um hook ou `tasks/` — nem em comentário nem em célula Markdown.

1. Contexto do projeto
   - Leia `references/03-datalake-core.md` e o overlay da nuvem deste projeto
     ({{OVERLAY_NUVEM}}).
   - Leia `@client_context/` relevante para `<ENTIDADE>` (KPI, indicador, definição de
     negócio que a Gold precisa materializar).
2. Entenda as origens
   - Leia cada Silver de `<SILVERS_DE_ORIGEM>` inteira. Liste grão e chave de cada uma.
3. Confira o consumidor
   - Se já existir consumo Power BI para esta entidade, veja o que o modelo semântico
     espera desta Gold antes de fechar o desenho, para não quebrar contrato
     (`references/04-powerbi-modelagem-dax.md`).
4. Proponha antes de escrever
   - Apresente grão final, chave de agregação e regra de negócio/agregação. Espere
     confirmação.
5. Construa
   - Junção entre Silvers (quando houver mais de uma) com grão declarado e cardinalidade
     validada antes da junção (`03-datalake-core.md` seção 8, join: grão + cardinalidade).
   - Cadeia de temp views nomeadas, nunca CTE longo (seção 2).
   - Nome do arquivo: `NB_GOLD_<ENTIDADE>.ipynb`.
6. Valide
   - Quality gates da seção 7 antes do write, incluindo a checagem de multiplicação de
     linhas em cada join.
7. Documente e catalogue
   - Rode o roteiro `documentar_produto.md` sobre o notebook pronto.
8. Registre
   - Atualize `PROJETO.md` (Log) e a linha correspondente da orquestração.
```
