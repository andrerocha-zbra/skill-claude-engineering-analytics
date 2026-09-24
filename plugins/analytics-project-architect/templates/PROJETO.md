# Projeto — {{CLIENTE}}

> Manifesto + **log vivo**. Atualizado automaticamente pela skill `analytics-project-architect` a cada trabalho relevante — não esperar o usuário pedir.

## Visão geral

- **Cliente:** {{CLIENTE}}
- **Cloud de dados:** {{FABRIC|DATABRICKS}}
- **Tecnologias:** {{Power BI - Datalake - ML - ...}}
- **Domínios/produtos:** {{doadores, doacoes, ...}}
- **Owner:** {{NOME}}
- **Início:** {{AAAA-MM-DD}}
- **Skill vendorizada:** analytics-project-architect v{{VERSAO}} (`.claude/skills/analytics-project-architect/`) — atualizar com `scripts/atualizar_skill_vendorizada.py`

## Escopo

> **Opcional** — usar quando o projeto tem múltiplas frentes/domínios e vale deixar explícito o que este `PROJETO.md` cobre (e o que fica fora, ex.: um domínio documentado em `PROJETO.md` próprio). Em projeto de 1 produto só, pode omitir esta seção.

- {{o que este PROJETO.md cobre e o que fica fora — 3-5 linhas}}

## Estado

| Fase | Estado | Notas |
|------|--------|-------|
| 0. Intake | ⬜ / 🟡 / ✅ | |
| 1. Dados (Silver/Gold) | ⬜ | |
| 2. Modelagem | ⬜ | |
| 3. DAX | ⬜ | |
| 4. Frontend | ⬜ | |
| 5. Doc + Handoff | ⬜ | |

> Domínios de engenharia/dados costumam renomear esta seção para **Estado da documentação** e adicionar uma seção **Estrutura** própria (ex.: notebooks e tabelas reais) logo depois — ambas as variantes são válidas, o nome muda pra refletir o que o projeto de fato rastreia.

## Estrutura

> **Opcional** — usar quando o mapa de pastas/artefatos do domínio não cabe só na Visão geral (ex.: datalake com várias tabelas/notebooks reais que vale listar aqui para orientação rápida). Em projeto pequeno/recém-iniciado, pode omitir.

- {{mapa da estrutura de pastas/artefatos deste domínio, se não couber só na Visão geral}}

## Mapa Necessidade → Solução

| ID | Necessidade (requisito) | Onde é resolvido (coluna/medida/visual) | Status |
|----|-------------------------|------------------------------------------|--------|
| D1 | | | |

## Decisões (gates)

| Data | Decisão | Alternativas | Motivo |
|------|---------|--------------|--------|
| | | | |

> **Opcional** para projetos de natureza mais estratégica (não puramente técnica): em vez de uma única tabela de "Decisões (gates)", pode-se dividir em três seções — **ADR — Decisões de arquitetura** (técnicas, já tomadas), **BDR — Decisões de negócio pendentes** (aguardando o cliente/PO) e **Riscos** (o que pode dar errado, mitigação) — quando o volume e a natureza das decisões justificar a separação. Não force a divisão em projetos pequenos; a tabela única de "Decisões (gates)" cobre a maioria dos casos.
>
> Quando uma decisão registrada aqui é **substituída** por uma nova (não apenas complementada), a entrada antiga migra para `historico/` (ver `01-estrutura-e-nomenclatura.md`) — não apagar a linha, trocar o texto por uma referência ao histórico + à decisão vigente.

## Log

<!-- Formato: - [AAAA-MM-DD] {Tecnologia} {Domínio}: o que foi feito (refs IDs/arquivos) -->
<!-- Rotação: a cada fechamento de trimestre, entradas antigas migram para PROJETO.md.historico/AAAA-QN.md,
     mantendo aqui só o resumo do trimestre + as ~10 entradas mais recentes (ver "Rotação do log" em 02-processo-e-templates.md) -->

- [{{AAAA-MM-DD}}] Master {{CLIENTE}}: Estrutura de projeto criada (kickoff)
