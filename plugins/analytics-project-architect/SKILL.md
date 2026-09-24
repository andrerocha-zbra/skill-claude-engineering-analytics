---
name: analytics-project-architect
description: "Estrutura e conduz projetos de dados (BI, engenharia, ML) do kickoff ao handoff — padroniza pastas/nomenclatura, transforma reuniões→atas→specs→tasks, mantém um log vivo (PROJETO.md) e roteia a execução técnica (Fabric, Databricks, Power BI modelagem/DAX/frontend, documentação, CI/CD). Também avalia e reorganiza um projeto já existente para a mesma estrutura, sem recriar do zero. Skill guarda-chuva autocontida e agnóstica de empresa/consultoria — a identidade de marca de quem está usando a skill (se houver) mora em company-profiles/, nunca no núcleo. Carrega os guias profundos de references/ só sob demanda. Use quando: iniciar/estruturar um projeto de dados, reorganizar um projeto existente, transformar uma Ata/requisito em specs e tasks, retomar um projeto (ler o log e continuar), decidir a próxima etapa, padronizar pastas/commits/handoff, ou configurar CI/CD seletivo para Fabric/Databricks."
---

# Analytics Project Architect (kickoff → estrutura → entrega → handoff)

## Objetivo

Skill **guarda-chuva** para **projetos de engenharia de analytics** (BI, datalake, ML). Decide *o quê fazer, em que ordem e com qual técnica*, mantém a **estrutura padrão** que escala, e conduz o ciclo **reunião → ata → spec → task → execução → handoff**. É **autocontida**: funde orquestração de BI, engenharia de dados (Fabric/Databricks), frontend Power BI, documentação e CI/CD — mas mantém este arquivo **fino** e carrega os guias profundos de `references/` **só quando a fase exige** (economia de tokens).

Princípio de token: **não leia references/ que a fase atual não precisa.** Este SKILL.md basta para kickoff, estrutura, sequenciamento e roteamento.

**Agnóstica de empresa e de cliente.** Nada neste plugin cita o nome de uma consultoria ou de um cliente específico. Duas camadas ficam **fora** deste plugin, por design:
- **Perfil de empresa** (voz, identidade visual default, convenções da consultoria que está usando o harness) — se existir, mora em `company-profiles/<empresa>/` na raiz do repo-harness, um nível acima deste plugin. Esta skill consulta esse perfil só para *defaults* de comunicação/documentação client-facing, nunca para regra técnica.
- **Dados do cliente** (regras de negócio, catálogo, decisões) — moram no repo-cérebro do próprio cliente, nunca aqui.

## Quando usar / quando NÃO usar

**Usar:** começar um projeto novo; padronizar/organizar um projeto existente; virar uma Ata/requisito em contrato+regras+tasks; retomar (ler `PROJETO.md` e seguir); decidir próxima etapa; padronizar commits/handoff; configurar a pasta de sincronização com Fabric/Databricks.

**NÃO usar:** dúvida pontual de sintaxe já dentro de um notebook/visual específico — vá direto ao `references/` da técnica. Esta skill é para **fluxo e estrutura**, não para o detalhe isolado de uma peça.

---

## Princípios

1. **Negócio↔Técnico explícito.** Todo artefato técnico rastreia a uma necessidade. Manter o mapa **Necessidade → Solução** em `PROJETO.md`.
2. **Spec é fonte de verdade.** Documentar antes de construir; preferir **especificação** a editar artefatos sensíveis na mão (ex.: TMDL — e o hook `bloquear_tmdl.py` garante isso). A spec sobrevive ao refactor.
3. **Estrutura padrão sagrada.** Pastas seguem `references/01`. Nova tecnologia ganha nova pasta de topo, nomeada pela tecnologia — não se re-arquiteta. `datalake/_tech-sync/` é a única pasta que a plataforma de dados do cliente enxerga (ver `references/08`).
4. **Gates de decisão.** Em forks consequentes (destino de tabela, regra ambígua, definição de KPI, ação irreversível) → `AskUserQuestion`. Não adivinhar.
5. **Verificação faz parte da entrega.** Nenhuma fase fecha sem sanity-check (ver `references/07`, M3).
6. **Log vivo, sempre.** Atualizar `PROJETO.md` automaticamente (ver "Log vivo"); o hook `lembrete_log_vivo.py` avisa nos pontos de checkpoint. Rotacionar com `scripts/rotacionar_log.py` quando crescer demais.
7. **Client-agnóstica e empresa-agnóstica.** Specifics do cliente (schemas, regras, lakehouse) moram em `@client_context/` do projeto. Specifics da consultoria (marca, voz) moram em `company-profiles/`. Nunca hardcoded neste plugin.
8. **Guardrails em código, não só em prompt.** Regra que, se ignorada, resulta em dado errado ou artefato corrompido vira hook (`references/07`) ou quality gate (`references/03-datalake-core.md`) — não fica só escrita em `CLAUDE.md`.
9. **Skill vendorizada no repositório do cliente.** O scaffold copia esta skill inteira para `.claude/skills/analytics-project-architect/` de cada projeto novo — reprodutível por qualquer pessoa que clone o repo, mesmo sem o plugin instalado. Correção nasce na fábrica (este plugin) e se propaga deliberadamente via `scripts/atualizar_skill_vendorizada.py --confirmar`, nunca silenciosamente (`references/10`).
10. **Roteiro por tipo de entrega, não instrução repetida.** Toda entrega recorrente (Silver, Gold, documentar produto) tem um roteiro pronto pra colar em `prompts/`, escaffoldado por padrão — o pedido vira uma linha, o roteiro carrega o resto.
11. **O cérebro não vaza para o entregável.** Notebook, relatório, medida ou comentário nunca cita por nome `CLAUDE.md`, `PROJETO.md`, a skill, um hook ou `tasks/` — o entregável descreve o fato em si, não o processo interno que levou a ele.
12. **Pendência é artefato que se move, não que some.** Problema resolvido nunca é apagado — vai para `problemas/resolvido/` com data e o que mudou no topo. Resolver sem mover deixa o repositório mentindo sobre o que está em aberto.

---

## Kickoff

Antes de tudo, uma checagem única: se `company-profiles/` não existe ou está vazio (primeira vez que esta skill roda neste ambiente), ofereça a entrevista de `references/00-onboarding-empresa.md` antes de seguir. Sessões seguintes não veem isso de novo — é checagem de existência de pasta, não um passo repetido.

Primeira pergunta, sempre: **projeto novo ou já existente?**

- **Existente** (já tem código, dado real, histórico de git): rodar `scripts/avaliar_projeto_existente.py`, seguir `references/09-refatorar-projeto-existente.md`. Nunca usar `scaffold_cliente.py` direto — ele assume pasta vazia.
- **Novo**: seguir o kickoff abaixo.

### Kickoff de projeto novo

Perguntar o mínimo (`AskUserQuestion`) e então montar a estrutura:

1. **Cliente/repo** (nome) — vira o nome do repositório (`<cliente>-brain`).
2. **Cloud de dados:** Microsoft Fabric **ou** Databricks (define o overlay técnico — `03a` vs `03b` — e o conteúdo de `_tech-sync/`).
3. **Tecnologias no escopo:** Power BI? Datalake? ML? (cria só as bandas necessárias).
4. **Domínios/produtos** iniciais (ex.: doadores, doações).
5. **Há material de origem?** (Ata, protótipo, modelo existente) → alimenta Fase 0.

Depois: rodar `scripts/scaffold_cliente.py` (cria a árvore completa, `git init`, `.claude/settings.json` com os hooks já wired, `_tech-sync/` já com o esqueleto certo pra nuvem escolhida, workflow de CI/CD, **vendoriza esta skill inteira** em `.claude/skills/analytics-project-architect/`, copia os roteiros por camada para `prompts/` e o `.mcp.json` — fabric + powerbi-modeling-mcp — para a raiz do projeto), inicializar `PROJETO.md` a partir de `templates/PROJETO.md` (registrando a versão da skill vendorizada), e registrar a primeira entrada de log.

---

## Estrutura padrão (resumo — detalhe em `references/01`)

Eixo **tecnologia-first**, pastas de topo nomeadas pelo conteúdo, sem prefixo numérico:

```
<cliente>-brain/
  PROJETO.md                 # log vivo + manifesto (versão da skill vendorizada pinada aqui)
  AGENTS.md / CLAUDE.md      # bootstrap fino
  .claude/settings.json      # hooks já wired
  .claude/skills/analytics-project-architect/  # skill vendorizada — reproduzível sem o plugin instalado (references/10)
  .mcp.json                  # MCPs fabric (HTTP+OAuth) e powerbi-modeling-mcp (stdio)
  prompts/                    # roteiros por camada, prontos pra colar (criar_silver.md, criar_gold.md, documentar_produto.md)
  @client_context/           # conhecimento de negócio do cliente: regras, catálogo, design-system, fontes externas
  apresentacoes/             # decks e entregas ao cliente
  reunioes/DD-MM-AA__titulo/ # materiais/ · ata.md · specs/
  powerbi/<dominio>/         # <pagina-ou-entidade>/ · <proj>.pbip · docs/
  datalake/
    _tech-sync/              # ⬅ única pasta conectada ao Fabric Git integration / Databricks Git folder
    documentacao/            # espelha as entidades de _tech-sync/, fora dela, nunca sincroniza
  ml/<modelo>/                # notebooks · cartao-modelo.md · experimentos/
  tasks/                      # único, top-level — tempo-de-trabalho.md · TASK-NNN__slug/
  historico/                  # snapshots congelados, nunca editados
  backup/
```

Pastas de topo nomeadas pelo conteúdo, sem prefixo numérico; nova tecnologia = nova pasta de topo. Trabalho não-entregável = prefixo `_` (ex.: `_tech-sync/`). Task = `TASK-NNN__slug/`, número sequencial de 3 dígitos, sem buracos. **Regras completas, growth rules e o caso 1-vs-N domínios: `references/01`.**

---

## Pipeline (fases, dependências, gates)

```
0. Intake      Ata/requisito → contrato de dados + regras + tasks + mapa Necessidade→Solução   [references/02]
     │ (gate: confirmar destinos de tabela e regras ambíguas)
1. Dados       Silver/Gold em _tech-sync/ · rodar na plataforma   [references/03-datalake-core.md + overlay 03a ou 03b]
     │ (destrava 2; precisa das colunas existirem fisicamente)
2. Modelagem   colunas calculadas, relacionamentos, tipos/format   [references/04]
     │ (destrava 3)
3. DAX         medidas por página + Regras de Negócio + Geral   [references/04]
     │ (destrava bind do 4)
4. Frontend    páginas/visuais; nativo onde basta, HTML onde agrega   [references/05]
     │
5. Doc+Handoff  documentação do projeto + CI/CD + limpeza + continuidade   [references/06, references/07, references/08]
```

**Sequência:** a Fase 1 só fecha após **rodar na plataforma** e o refresh trazer as colunas; Modelagem/DAX não começam antes. Frontend pode começar em paralelo no que não depende de dado (layout), mas o bind final espera a Fase 3. Limpeza destrutiva fica para **depois** do frontend. **Fatia vertical primeiro:** entregar uma página/entidade completa antes de replicar.

---

## Roteamento sob demanda (leia só o que a fase pede)

| Preciso de… | Leia |
|---|---|
| **Onboarding de empresa** (primeira execução, antes do primeiro kickoff) | `references/00-onboarding-empresa.md` |
| Estrutura de pastas, numeração, nomes, growth rules, `_tech-sync/` | `references/01-estrutura-e-nomenclatura.md` |
| Processo (reunião→ata→spec→task), templates, commits, regra do log, rotação | `references/02-processo-e-templates.md` |
| Núcleo Spark SQL/medallion cloud-agnóstico (quality gates, dedup, nomenclatura) | `references/03-datalake-core.md` |
| Diferenças específicas do **Microsoft Fabric** | `references/03a-fabric-overlay.md` |
| Diferenças específicas do **Databricks** | `references/03b-databricks-overlay.md` |
| Modelagem + medidas **DAX** (via Power BI MCP) | `references/04-powerbi-modelagem-dax.md` |
| Visuais customizados **HTML/CSS/SVG/JS via DAX** | `references/05-powerbi-frontend.md` |
| **Documentar** um projeto Power BI (PBIP) de forma econômica + handoff | `references/06-doc-e-handoff.md` |
| **Mecanismos e hooks**: M1-M4 + os hooks reais de `.claude/settings.json` | `references/07-mecanismos-e-hooks.md` |
| **CI/CD**: conectar `_tech-sync/` ao Fabric/Databricks, pipelines | `references/08-cicd-fabric-databricks.md` |
| **Refatorar um projeto existente** para a estrutura padrão | `references/09-refatorar-projeto-existente.md` |
| **Vendorizar/atualizar a skill** dentro de um projeto, MCPs `fabric`/`powerbi-modeling-mcp` | `references/10-vendorizacao-e-atualizacao.md` |
| Gerar notebook novo, limpar notebook pra reimportar, rodar scaffold, avaliar projeto existente, rotacionar log, vendorizar/atualizar skill, detectar MCP local | `scripts/` (ver docstring de cada script) |

Regra: abra **uma** reference por vez, conforme a fase. Não pré-carregue o conjunto.

---

## Convenção de commits

Formato: `{Tecnologia} {Domínio}: {descrição em PT no passado/imperativo}`. Sem `feat`/`fix`. Múltiplas mudanças = **uma linha por mudança**, bem identadas. Referenciar IDs de spec/regra quando houver (ex.: `(R6)`, `(DL-06)`).

```
Datalake Doadores: Mapeado genero e motivo de inativacao no Silver (DL-06)
Power BI Doacoes: Adicionado campo tipo_doacao ao modelo e ao visual de barras
```

Detalhe e mais exemplos: `references/02`.

---

## Log vivo (`PROJETO.md`) — automático

**Regra:** ao concluir qualquer trabalho relevante (spec criada, notebook editado, medida publicada, fase concluída, decisão de gate), **anexar sem o usuário pedir** uma entrada na seção `## Log` de `PROJETO.md`:

```
- [AAAA-MM-DD] {Tecnologia} {Domínio}: o que foi feito (refs de IDs/arquivos)
```

E manter atualizados, no cabeçalho do `PROJETO.md`, o **estado por fase** e o **mapa Necessidade→Solução**. Ao pausar sessão, gerar/atualizar HANDOFF (ver `templates/HANDOFF.md`). Template do log: `templates/PROJETO.md`. Quando o log crescer muito, rodar `scripts/rotacionar_log.py`.

---

## Fluxo de uso resumido

1. **Projeto novo ou existente?** → Novo: kickoff (perguntas mínimas) → `scripts/scaffold_cliente.py` → `PROJETO.md`. Existente: `scripts/avaliar_projeto_existente.py` → `references/09` → migração em fatias.
2. **Recebeu Ata/requisito?** → Fase 0 (`references/02`): contrato + regras + tasks + mapa; confirmar gates.
3. **Dados?** → `references/03-datalake-core.md` + overlay da nuvem; gerar notebook com `scripts/novo_notebook.py`; rodar na plataforma (M2/`scripts/limpar_notebook_import.py`).
4. **Modelo/medidas?** → `references/04`; aplicar via CLI interativo (M1 em `references/07`); verificar por leitura (M3).
5. **Visuais?** → fatia vertical primeiro; `references/05`; nativo onde basta.
6. **Documentar/entregar?** → `references/06` (econômico); handoff.
7. **CI/CD?** → `references/08`; copiar template de `templates/ci-cd/`.
8. **Sempre:** atualizar `PROJETO.md` (log vivo).
