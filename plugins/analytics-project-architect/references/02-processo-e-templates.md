# Processo, Templates e Convenções

O ciclo do projeto: **reunião → ata → spec → task → execução → verificação → log/handoff**. Cada elo produz um artefato versionado no lugar padrão (ver `01-estrutura-e-nomenclatura.md`).

## Fluxo reunião → ata → spec → task

1. **Reunião** — criar `reunioes/DD-MM-AA__titulo/`. Jogar todo material cru em `materiais/` (transcrição, resumo, áudio, prints).
2. **Ata** (`ata.md`, template `templates/ata.md`) — estruturar a reunião: metadados (data, duração, pauta, participantes), contexto, decisões numeradas, pendências. É o registro; não é a spec.
3. **Spec** (`specs/ESPEC-*.md`, template `templates/ESPEC.md`) — converter o que a ata pediu em requisito acionável: contexto/objetivo, restrições de arquitetura, requisitos numerados (`D1`, `D2`...), critérios de aceite. Specs duráveis do domínio migram/copiam para `powerbi/<dominio>/<pagina-ou-entidade>/especificacao.md`.
4. **Task** (`tasks/TASK-NNN__slug/descricao-tarefa.md`, template `templates/task/descricao-tarefa.md`) — origem, o que fazer, o que ler antes, como entregar, decisões do usuário, referências. Ver "Ata gera task" abaixo para o fluxo automatizado de criação a partir de uma reunião.

### Ata gera task

Pedir para gerar a ata de uma reunião roda `scripts/nova_ata.py --titulo "..." --data DD-MM-AA`. O script só monta o esqueleto — o agente lê o material depois e preenche o conteúdo real:

- cria `reunioes/DD-MM-AA__slug/`, com `materiais/`, `specs/` e um `ata.md` esqueleto (versão mais rica em `templates/ata.md`, para copiar por cima quando fizer sentido);
- por padrão, cria também a task vinculada em `tasks/TASK-NNN__slug/`, com `fontes/` (materiais recebidos, como chegaram) e um `descricao-tarefa.md` esqueleto que já aponta de volta para `reunioes/DD-MM-AA__slug/ata.md`.

Use `--sem-task` quando a reunião não gera trabalho novo, só alinhamento — nenhuma task é criada nesse caso.

Depois de rodar o script: ler o material em `materiais/` e escrever o conteúdo real de `ata.md` e de `descricao-tarefa.md` — o script não infere nada do conteúdo da reunião.

`templates/task/descricao-tarefa.md` é o template geral de qualquer task (origem, o que fazer, o que ler antes, como entregar, decisões do usuário, referências) — é o padrão para toda task, não só as geradas a partir de uma ata. Os templates antigos `templates/task/00_contrato.md`, `01_datalake.md`, `02_modelagem.md`, `03_dax.md`, `04_frontend.md` continuam existindo, mas como anexos **opcionais** dentro da pasta de uma task — usados só quando ela é genuinamente multi-etapa técnica (datalake → modelagem → DAX → frontend). Não são mais o padrão obrigatório de toda task.

## Fase 0 — Intake (transformar Ata/requisito em artefatos)

Ao receber Ata/protótipo/modelo existente, produzir (em `specs/` da reunião e/ou na pasta da entidade em `powerbi/<dominio>/<pagina-ou-entidade>/`):

1. **Contrato de dados** (`00_contrato-dados.md`) — tabelas/colunas exatas que o consumo (BI/ML) espera. Marcar **colunas existentes × novas**. Fonte de verdade compartilhada.
2. **Regras de negócio** (`00_regras-negocio.md`) — definições canônicas numeradas (janelas, classificações, fórmulas em pseudocódigo, exceções). Regra transversal a vários domínios vai para `@client_context/`, nunca duplicada aqui.
3. **Task(s) em `tasks/`** — ver "Ata gera task" acima; anexar os templates de estágio (`01_datalake`, `02_modelagem`, `03_dax`, `04_frontend`) dentro da pasta da task só quando o trabalho for genuinamente multi-etapa técnica.
4. **Mapa Necessidade → Solução** — tabela requisito (D1, D2, …) → onde é resolvido (coluna/medida/visual). Prova cobertura ao cliente; vive no `PROJETO.md`.

Inferir do material: da Ata os requisitos + falas estratégicas; do protótipo os visuais/KPIs concretos; do modelo atual o que reusar. **Não recriar do zero se há base — adaptar.**

## Gates de decisão (quando perguntar)

Usar `AskUserQuestion` (não adivinhar) quando: destino/nome de tabela diverge entre o que existe e o contrato; regra de negócio com mais de uma interpretação defensável; definição de KPI que muda o número exibido; ação consequente/irreversível (apagar medidas/tabelas, repontar gravação de produção, enviar algo ao cliente).

## Convenção de commits

Formato: **`{Tecnologia} {Domínio}: {descrição em PT}`**. Sem `feat`/`fix`/`type()`. Descrição no passado ou imperativo, objetiva. Referenciar IDs de spec/regra quando houver: `(R6)`, `(DL-06)`, `(D3)`.

Uma mudança:
```
Datalake Doadores: Mapeado genero e motivo de inativacao no Silver (DL-06)
```

Várias mudanças no mesmo commit → **uma linha por mudança, bem identada** (linha em branco após a primeira):
```
Datalake Doadores: Ajustes no cadastro Silver

  Datalake Doadores: Mapeado genero (codigo_genero + genero) (DL-06)
  Datalake Doadores: Preenchido motivo de inativacao e renomeado para descricao (R6)
  Power BI Doadores: Repontado sourceColumn e visual de motivos de saida
```

Tecnologias usadas como rótulo: `Datalake`, `Power BI`, `ML`, `Master`, `Docs`. Domínio em seguida (`Doadores`, `Doacoes`, `Payments`). Casing consistente (`Power BI`, nunca `powerbi`/`power bi`).

## Log vivo (`PROJETO.md`) — atualização automática

O `PROJETO.md` (template `templates/PROJETO.md`) fica na raiz e é o **diário do projeto**. **Regra:** ao concluir qualquer trabalho relevante — sem o usuário pedir — anexar na seção `## Log`:

```
- [AAAA-MM-DD] {Tecnologia} {Domínio}: o que foi feito (refs de IDs/arquivos)
```

E manter no cabeçalho: estado por fase (Intake/Dados/Modelagem/DAX/Frontend/Doc) e o mapa Necessidade→Solução. Gatilhos de log: spec criada, notebook editado/rodado, medida publicada, fase concluída, decisão de gate tomada, entrega ao cliente.

### Rotação do log

O `## Log` do `PROJETO.md` cresce indefinidamente ao longo do projeto — sem rotação, um projeto de 2+ anos acumula centenas de entradas e o arquivo vira caro de ler (justamente o arquivo que a skill relê no início de toda sessão para retomar o contexto).

**Convenção:** a cada **fechamento de trimestre**, as entradas mais antigas do `## Log` migram para `PROJETO.md.historico/AAAA-QN.md` (ex.: `PROJETO.md.historico/2026-Q1.md`), e o `PROJETO.md` fica só com:
- um **resumo do trimestre encerrado** (3-6 linhas: principais entregas, decisões e mudanças de rumo daquele período — não uma lista de todas as entradas, uma síntese);
- as **~10 entradas mais recentes** do log corrente, sem rotação ainda.

Essa rotação é executada por `scripts/rotacionar_log.py` — aqui documenta-se apenas a **convenção de formato e destino** (nome de pasta `PROJETO.md.historico/`, nome de arquivo `AAAA-QN.md`, o que fica resumido vs. o que fica literal). Não implementar a rotação manualmente entrada por entrada; sempre rodar o script.

## Handoff (ao pausar)

Gerar/atualizar `HANDOFF.md` (template `templates/HANDOFF.md`) na pasta `docs/` do domínio/tecnologia que pausou (`powerbi/<dominio>/docs/HANDOFF.md`, ou `datalake/documentacao/HANDOFF.md` para uma frente de datalake). Seções: a ideia, arquitetura/restrições, o que foi feito (por etapa), mapa Necessidade→Solução, o que falta, análises/insights, mecanismos usados, arquivos de referência, estado por etapa. É o "leia isto primeiro ao retomar".

## Templates disponíveis (`templates/`)

- `PROJETO.md` · `ata.md` · `ESPEC.md` · `00_contrato-dados.md` · `00_regras-negocio.md`
- `task/descricao-tarefa.md` — template geral de qualquer task.
- `task/00_contrato.md` · `task/01_datalake.md` · `task/02_modelagem.md` · `task/03_dax.md` · `task/04_frontend.md` — anexos opcionais, só para task genuinamente multi-etapa técnica.
- `HANDOFF.md` · `README-dominio.md` · `.gitignore`
- `doc/` — templates de documentação Power BI (ver `06-doc-e-handoff.md`).
