# Getting started

Uma skill do Claude Code que estrutura um projeto de engenharia de analytics — BI, datalake, ML — do kickoff ao handoff, com pastas padrão, um log vivo, hooks e scripts reais. Serve tanto para começar um projeto do zero quanto para reorganizar um projeto que já existe.

## Como as peças se encaixam

```mermaid
flowchart LR
    S[Skill<br/>analytics-project-architect] --> P[Perfil de empresa<br/>opcional]
    P --> R[Repositório do projeto<br/>1 por cliente]
    R --> T[_tech-sync/]
    T --> D[(Fabric ou Databricks)]
```

A skill é genérica e não muda entre projetos. O perfil de empresa (`company-profiles/`) é opcional e guarda só identidade — voz, design default — de quem está conduzindo os projetos. Cada cliente tem seu próprio repositório. Dentro dele, uma única pasta (`_tech-sync/`) se conecta à plataforma de dados; o resto do repositório — atas, regras de negócio, documentação — nunca é visto por ela.

## Duas jornadas

### Projeto novo

```mermaid
flowchart LR
    A[Kickoff:<br/>cliente, nuvem,<br/>tecnologias, domínios] --> B[scaffold_cliente.py]
    B --> C[Repositório criado:<br/>pastas, hooks, PROJETO.md]
    C --> D[Conectar _tech-sync/<br/>ao Fabric ou Databricks]
    D --> E[novo_notebook.py<br/>primeira entrega]
```

```bash
python plugins/analytics-project-architect/scripts/scaffold_cliente.py \
  --cliente nome-do-cliente --cloud fabric \
  --tecnologias powerbi,datalake --dominios dominio1,dominio2 \
  --destino ../nome-do-cliente-brain
```

Isso cria o repositório completo: árvore de pastas, `.claude/settings.json` com os hooks já configurados, `PROJETO.md`/`AGENTS.md`/`CLAUDE.md` preenchidos, e `datalake/_tech-sync/` pronto para a nuvem escolhida.

### Projeto existente

```mermaid
flowchart LR
    A[avaliar_projeto_existente.py] --> B[Relatório de gaps]
    B --> C[Adicionar governança<br/>sem mover nada]
    C --> D[Migrar em fatias<br/>git mv, 1 banda por vez]
    D --> E{Já conectado a<br/>uma plataforma?}
    E -->|Sim| F[Reconectar<br/>deliberadamente]
    E -->|Não| G[Conectar _tech-sync/]
```

```bash
python plugins/analytics-project-architect/scripts/avaliar_projeto_existente.py \
  --projeto /caminho/do/projeto/existente --saida relatorio-gap.md
```

O script só lê — nunca move ou apaga nada no projeto avaliado. O relatório mapeia o que já existe contra a estrutura padrão e sugere próximos passos; qualquer migração de pasta é uma decisão deliberada, nunca automática. Detalhe do processo: `plugins/analytics-project-architect/references/09-refatorar-projeto-existente.md`.

## A estrutura de um projeto

```
<projeto>/
├── PROJETO.md                 # log vivo + manifesto
├── AGENTS.md / CLAUDE.md      # bootstrap
├── .claude/settings.json      # hooks
├── @client_context/           # regras de negócio, catálogo, design-system do cliente
├── apresentacoes/
├── reunioes/
├── powerbi/<dominio>/
├── datalake/
│   ├── _tech-sync/            # única pasta conectada à plataforma de dados
│   └── documentacao/
├── ml/
├── tasks/
├── historico/                 # decisões e arquitetura supersedidas
└── backup/
```

Detalhe completo, incluindo regras de crescimento: `plugins/analytics-project-architect/references/01-estrutura-e-nomenclatura.md`.

## Onde cada coisa mora neste repositório

| Pasta | Conteúdo |
|---|---|
| `plugins/analytics-project-architect/` | A skill — `SKILL.md`, `references/`, `templates/`, `scripts/`, `hooks/` |
| `company-profiles/` | Identidade opcional de quem conduz os projetos |
| `docs/METODO.md` | O método por trás da skill, em prosa |

## Próximo passo

Para usar a skill: instale com `/plugin marketplace add` (ver `README.md`) e peça para iniciar ou avaliar um projeto — a skill pergunta o que faltar.

Para entender o método a fundo antes de usar: `docs/METODO.md`, depois `plugins/analytics-project-architect/SKILL.md`.
