# Prompt — documentar e catalogar um produto pronto

## Como usar

Passo final obrigatório depois de `criar_silver.md` ou `criar_gold.md` (ou de publicar um
modelo/relatório Power BI). Copie o bloco de "Prompt" abaixo, trocando `<PRODUTO>` pelo
notebook, tabela ou artefato Power BI que acabou de ficar pronto.

Um produto de dados só está completo quando o significado dele está legível fora do
repositório (no catálogo da plataforma, ou no modelo semântico) — este roteiro não é
opcional.

---

## Prompt

```
`<PRODUTO>` acabou de ficar pronto. Preciso documentá-lo e catalogá-lo seguindo a skill
`analytics-project-architect` vendorizada em `.claude/skills/analytics-project-architect/`.

Regra de conteúdo: o texto gravado no catálogo (comentário de tabela/coluna, ou descrição
de medida/coluna no modelo semântico) usa linguagem de negócio, sem jargão técnico, e nunca
cita artefato interno do repositório (`CLAUDE.md`, `PROJETO.md`, a skill, `tasks/`).

Se `<PRODUTO>` é um notebook (Silver/Gold):
1. Siga `references/03-datalake-core.md` seção 13 (Catalogação — sempre a etapa final):
   comentário de tabela + um comentário por coluna, gravados depois do write, nunca
   levantando exceção (a carga já aconteceu; falta de permissão para documentar não pode
   desfazê-la).
2. Crie/atualize, na pasta de `datalake/documentacao/<camada>/<entidade>/` correspondente
   (nunca dentro de `_tech-sync/`):
   - `catalogo.md` — o que o produto significa para o negócio.
   - `modelagem/consideracoes.md` — por que o desenho ficou assim, alternativas
     descartadas.
   - `problemas/problemas-identificadas.md` — o que pode dar errado e o que já deu (item
     resolvido migra para `problemas/resolvido/`, nunca é apagado).

Se `<PRODUTO>` é um modelo semântico ou relatório Power BI:
1. Siga `references/06-doc-e-handoff.md` para a documentação econômica do PBIP.
2. Descrição de medida e de coluna dentro do próprio modelo (via MCP de modelagem, M1 em
   `references/07-mecanismos-e-hooks.md`), mais o documento de negócio do produto na pasta
   `powerbi/<dominio>/<pagina-ou-entidade>/`.

Depois, em qualquer um dos dois casos:
3. Registre em `PROJETO.md` (Log) que o produto foi documentado/catalogado, com o caminho
   do artefato.
```
