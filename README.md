# analytics-engineering-harness

Marketplace do Claude Code com uma skill, `analytics-project-architect`, e os scripts e hooks que ela usa. A skill estrutura projetos de engenharia de analytics — BI, datalake, ML — do kickoff ao handoff, e também sabe reorganizar um projeto existente para essa mesma estrutura.

Primeira vez aqui? Comece por [`GETTING_STARTED.md`](GETTING_STARTED.md).

Este repositório não guarda nenhum projeto de cliente. Cada projeto tem o próprio repositório, gerado pelos scripts da skill.

## Estrutura

```
.claude-plugin/marketplace.json        # manifesto do marketplace — instala com /plugin marketplace add
plugins/analytics-project-architect/   # a skill: fonte de verdade, versionada
  SKILL.md
  .mcp.json           # MCPs bundled: fabric (HTTP+OAuth) e powerbi-modeling-mcp (stdio)
  references/        # guias técnicos, carregados sob demanda
  templates/          # PROJETO.md, ESPEC.md, HANDOFF.md, ata.md, task/*, doc/*, ci-cd/*, prompts/*
  scripts/            # scaffold_cliente.py, novo_notebook.py, avaliar_projeto_existente.py, vendorizar_skill.py, ...
  hooks/              # hooks do settings.json
company-profiles/      # opcional: identidade/voz/design de quem está usando o harness
docs/METODO.md          # o método por trás da skill
```

## Instalar a skill (uma vez por máquina, global)

```
/plugin marketplace add andrerocha-zbra/skill-claude-engineering-analytics
/plugin install analytics-project-architect@analytics-engineering-harness --scope user
```

`--scope user` é o que garante que o plugin fica disponível em **qualquer** projeto aberto depois nessa máquina — inclusive na extensão do Claude Code do VS Code, sem precisar reinstalar por projeto. Se o Claude Code perguntar o escopo interativamente (quando `--scope` não é passado), escolha "user"/"global", nunca "project". Passo a passo completo, com verificação e os MCPs bundled: [`GETTING_STARTED.md`](GETTING_STARTED.md).

## Publicando uma atualização

A skill é consumida como plugin instalado a partir deste repositório. Depois de editar `plugins/analytics-project-architect/`: bump a `version` em `plugins/analytics-project-architect/.claude-plugin/plugin.json`, faça commit e push. Quem tiver instalado via `/plugin marketplace add` recebe a atualização rodando `/plugin marketplace update analytics-engineering-harness`. Instalação via marketplace git não exige empacotamento.

## Nome de repositório de cliente

`<cliente>-brain` — ver `company-profiles/<empresa>/convencoes.md` quando houver um perfil de empresa configurado.
