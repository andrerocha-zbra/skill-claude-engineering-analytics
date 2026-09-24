# Prompt — criar (ou revisar) uma Silver

## Como usar

Copie o bloco de "Prompt" abaixo e cole como pedido para o agente, trocando `<ENTIDADE>` e
`<BRONZE_OU_ORIGEM>` pelos valores reais. Não é preciso reexplicar as regras do projeto:
este roteiro já referencia a skill e os arquivos de governança como fonte de verdade.

Se já souber os artefatos de referência (uma Silver irmã já pronta, a spec da entidade),
informe o caminho ao colar — evita busca aberta no repositório.

Prefira colar este prompt no início de uma conversa nova.

---

## Prompt

```
Preciso criar (ou revisar) a Silver de `<ENTIDADE>`, a partir de `<BRONZE_OU_ORIGEM>`,
seguindo a skill `analytics-project-architect` vendorizada em
`.claude/skills/analytics-project-architect/` e os arquivos de governança do projeto
(`CLAUDE.md`, `PROJETO.md`, `@client_context/`).

Regra de execução: faça as leituras você mesmo, nesta mesma conversa. Não delegue a um
subagente a menos que uma busca direta falhe ou volte ambígua — este é um roteiro fechado,
com locais previsíveis.

Regra de conteúdo: o notebook gerado nunca cita, por nome, `CLAUDE.md`, `PROJETO.md`, a
skill, um hook ou `tasks/` — nem em comentário nem em célula Markdown. Descreva a regra ou
o fato em si, sem narrar o processo de investigação que levou à decisão.

1. Contexto do projeto
   - Leia `references/03-datalake-core.md` (núcleo Spark SQL-first, cloud-agnóstico) e o
     overlay da nuvem deste projeto ({{OVERLAY_NUVEM}}).
   - Leia `@client_context/` relevante (regras de negócio, glossário) para `<ENTIDADE>`.
2. Entenda a origem
   - Leia `<BRONZE_OU_ORIGEM>` inteira. Liste os campos, os tipos e o que é chave.
3. Confira o padrão
   - Se já existir uma Silver irmã pronta no projeto, leia-a e siga o mesmo layout
     (estrutura de 11 seções, ver `03-datalake-core.md` seção 12).
4. Proponha antes de escrever
   - Apresente grão, chave, regras de deduplicação (seção 5, nunca silenciosa) e
     validações (seção 7 — quality gates Tier 1/Tier 2). Espere confirmação antes de
     construir.
5. Construa
   - Cadeia de temp views nomeadas (seção 2), nunca CTE longo.
   - Todo de-para/classificação declara o que acontece com o valor que não se encaixa
     (`unhandled_case_explicit`, seção 6).
   - Nome do arquivo: `NB_SILVER_<ENTIDADE>.ipynb` (`01-estrutura-e-nomenclatura.md`).
6. Valide
   - Rode os quality gates da seção 7 antes do write. Contagens reconciliam entre origem e
     Silver.
7. Documente e catalogue
   - Rode o roteiro `documentar_produto.md` sobre o notebook pronto.
8. Registre
   - Atualize `PROJETO.md` (Log) e a linha correspondente da orquestração
     (CSV metadata-driven no Fabric, ou `databricks.yml`/`resources/` no Databricks).
```
