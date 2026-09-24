# Vendorização da skill e atualização

## O problema que isso resolve

Um projeto criado por `scaffold_cliente.py` só continuava funcionando enquanto o plugin
`analytics-project-architect` ficasse instalado na máquina de quem trabalhasse nele — `SKILL.md`,
`references/`, `templates/` e `scripts/` nunca eram copiados para dentro do repositório do
cliente, só os hooks. Clonar o repo numa máquina sem o plugin instalado, ou revisitá-lo
depois de desinstalar o plugin, perdia acesso ao método inteiro.

A solução é o modelo das gerações anteriores do método: a skill vive **dentro do
repositório do cliente**, versionada no git, não só instalada globalmente. O plugin continua
sendo a **fábrica central** (onde um bug é corrigido uma vez, um overlay novo nasce), mas
todo projeto novo recebe um snapshot completo dela.

## Vendorização na criação

`scripts/scaffold_cliente.py` chama `scripts/vendorizar_skill.py` automaticamente: copia
`SKILL.md` + `references/` + `templates/` + `scripts/` do plugin para
`<projeto>/.claude/skills/analytics-project-architect/` — é o caminho que o Claude Code
carrega automaticamente como skill de projeto (não `.skills/`, sem o `.claude/`, que não é
descoberto). A versão vendorizada fica registrada em
`.claude/skills/analytics-project-architect/VERSION`, lida de `.claude-plugin/plugin.json`
no momento da vendorização.

Rodar `vendorizar_skill.py --projeto <caminho>` isolado (fora do scaffold) também funciona,
para adicionar a skill vendorizada a um projeto que já existia antes desta mudança.

## Atualização deliberada

Corrigir algo na fábrica (este plugin) não propaga sozinho para os projetos já criados —
isso é intencional: a propagação é um passo visível, revisável num diff/commit, nunca um
efeito colateral silencioso de reabrir o projeto.

Para propagar uma correção:

```
python atualizar_skill_vendorizada.py --projeto C:/repos/NomeCliente
python atualizar_skill_vendorizada.py --projeto C:/repos/NomeCliente --confirmar
```

Sem `--confirmar`, o script só mostra o diff (arquivos novos, alterados, removidos do
plugin) entre o plugin instalado e a skill vendorizada do projeto — nada é escrito. Com
`--confirmar`, aplica o resync. Nunca toca em `PROJETO.md`, `CLAUDE.md`, `prompts/` ou
qualquer outro arquivo do projeto fora de `.claude/skills/analytics-project-architect/`.

Rode os dois scripts a partir da cópia do plugin **instalada**, nunca a partir da cópia já
vendorizada dentro de um projeto — essa cópia serve só para o Claude Code carregar a skill
naquele projeto, não para vendorizar de novo a partir dela.

## Ver também

- `01-estrutura-e-nomenclatura.md` — onde `.claude/skills/analytics-project-architect/` entra
  na árvore do projeto.
- `08-cicd-fabric-databricks.md` — a outra fronteira de sincronização do projeto
  (`datalake/_tech-sync/`), não confundir as duas: uma sincroniza com a plataforma de dados,
  esta sincroniza a skill com o plugin.
