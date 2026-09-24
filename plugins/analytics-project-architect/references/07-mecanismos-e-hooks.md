# Mecanismos operacionais e hooks

## Por que isso não depende de invocar a skill a cada ação

Três mecanismos trabalham juntos, nenhum deles exige nomear a skill de novo a cada pedido:

| Mecanismo | Quando age | O que garante |
|---|---|---|
| Casamento pelo `description` da skill | A cada pedido do usuário | O Claude Code reconhece que o pedido é da área desta skill ("crie um notebook", "documenta esse PBI") e carrega `SKILL.md` sozinho |
| Hooks (`.claude/settings.json`) | Toda chamada de ferramenta que casar com o matcher, em qualquer sessão, mesmo se a skill nunca foi mencionada | Validação/aviso/bloqueio determinístico, sem depender do modelo lembrar |
| `AGENTS.md`/`CLAUDE.md` do projeto | Início de toda sessão | Regra explícita e permanente ("notebooks seguem `references/03`", "log sempre atualizado") — inclusive uma tabela direta "quando fizer X, use Y" no `CLAUDE.md` gerado por `scripts/scaffold_cliente.py` |

Hooks não têm juízo: eles detectam "isto é um `.ipynb`" ou "isto é um comando destrutivo" por padrão de texto, não "este notebook está correto". Por isso os hooks de padrão técnico (`lembrete_padrao_sparksql.py`, `lembrete_mudanca_estrutural.py`) são avisos heurísticos, nunca bloqueio — quem decide se o aviso procede é sempre o agente ou a pessoa, lendo o que o hook sinalizou.

Duas categorias de automação:

- **Mecanismos (M1-M4)**: playbooks que o próprio agente segue manualmente quando uma ferramenta externa tem uma limitação que não dá pra contornar por hook (ex.: um servidor MCP que exige confirmação interativa humana). Continuam sendo prosa que o agente segue, mas cada um tem um motivo técnico concreto documentado abaixo.
- **Hooks**: automação real, declarada em `.claude/settings.json`, que roda sem depender do agente lembrar. É o que faz regras como "nunca editar TMDL na mão" ou "sempre atualizar o `PROJETO.md`" valerem sempre, em vez de existirem só como frase em `CLAUDE.md`.

---

## Mecanismos (M1-M4)

### M1 — Aplicar mudanças no modelo semântico via MCP

Fato técnico: em servidores MCP de modelagem tabular (ex.: `powerbi-modeling-mcp`), operações de **escrita** (`Create`/`Update`/`Rename`/`Delete`) e execução de DAX **exigem confirmação interativa** e **auto-recusam** em sessão SDK/headless (`claude -p`) — mesmo com `--dangerously-skip-permissions`. A recusa vem do **servidor MCP**, não do Claude Code.

Consequência prática:
- **Leitura** (`List`/`Get`) roda normalmente na sessão de trabalho — use para inspeção/verificação.
- **Escrita/DAX** exige que o usuário abra o `claude` CLI interativo (com `--mcp-config` apontando pro servidor) e aprove manualmente os prompts.
- O agente não dirige essa janela interativa — só **prepara um prompt determinístico** (ex.: `run1_criar_medida.txt`) com os passos e JSON exatos a executar: conectar na instância local aberta → operações CRUD na ordem certa → validar por leitura + `dax_query` de sanity-check.
- DAX longo vai num arquivo `.dax` separado (evita problema de escaping ao colar no CLI).
- Pré-requisito: a ferramenta desktop do modelo (ex.: Power BI Desktop) precisa estar aberta com o projeto carregado.
- `powerbi-modeling-mcp` já vem bundled no `.mcp.json` deste plugin/skill vendorizada, mas o executável local (extensão VS Code `analysis-services.powerbi-modeling-mcp`) é específico da máquina — rode `scripts/detectar_powerbi_modeling_mcp.py` uma vez por máquina para resolver `POWERBI_MODELING_MCP_PATH` (`references/10-vendorizacao-e-atualizacao.md`). O MCP `fabric` (HTTP+OAuth) não precisa desse passo.

### M2 — Import de notebook editado fora da plataforma

`.ipynb` editado fora da UI web/nativa da plataforma (Fabric, Databricks) pode falhar ao reimportar (ex.: `400 Bad Request` no Fabric). Dois culpados recorrentes: outputs salvos (especialmente erro com traceback ANSI) e `source` serializado como string única em vez de lista de linhas.

Rode `scripts/limpar_notebook_import.py CAMINHO.ipynb` antes de reimportar. O script zera outputs/execution_count, normaliza `source` para lista de linhas, grava UTF-8 sem BOM, preserva toda a metadata da plataforma (`kernelspec`, `microsoft`, `spark_compute`, `dependencies`).

### M3 — Verificação (sanity-check de entrega)

Checklist antes de fechar qualquer fase:
- Contagens reconciliam entre camadas (origem → Silver → Gold).
- Domínios/enums válidos (valor ∈ conjunto esperado — ver `unhandled_case_explicit` em `03-datalake-core.md`).
- Nenhuma data no futuro.
- Ordem de grandeza confere com o material de origem (Ata/requisito) — divergência grande é **insight a investigar**, não necessariamente bug.
- Pós-rename/retipagem: checar downstream (medidas, visuais, notebooks consumidores) antes de considerar fechado.

### M4 — Criação/leitura de itens no Fabric via MCP é assíncrona sem tool de polling

Fato técnico observado no MCP `mcp__fabric__*`: `get_item_definition` retorna sempre uma operação pendente (corpo `null`, `Retry-After: 20`, `operation-id` novo a cada chamada) e não existe tool de polling exposto — na prática, ler a definição de um item por esse MCP não funciona hoje. `create_item` também responde de forma assíncrona (o retorno da própria chamada pode vir vazio/`null`) mas a criação **completa no servidor**.

Consequência prática:
- Não trate o retorno vazio de `create_item` como falha. Espere ~15-20s e confirme via `mcp__fabric__list_items` (ou `get_item`) — nunca confie no corpo de retorno da própria chamada assíncrona.
- Se ainda assim usar `create_item` para N itens (ex.: itens pequenos fora do fluxo Git — ver `08-cicd-fabric-databricks.md`), desenhe o loop para ser **idempotente e retomável**: antes de criar, cheque se o item já existe (por nome, via `list_items`); se um subagente ou processo em background for interrompido no meio (limite de tempo/turnos é um cenário real, não hipotético), a retomada deve pular o que já foi criado em vez de assumir uma execução linear sem interrupção.
- **Teto real de escala do `create_item` com payload gerado inline**: pedir para o próprio agente montar o base64 do conteúdo dentro da chamada de tool esbarra num limite de ~25-27 mil caracteres de texto gerado por chamada — trava antes de valer a pena para notebooks reais de produção (um notebook de ~300KB nem chega perto de caber). Para popular o workspace em massa a partir de `.ipynb` existentes, não é caso de uso do `create_item` via agente: use o caminho Git (script de conversão determinístico + commit/push + "Update from Git" descrito em `08-cicd-fabric-databricks.md`), que roda em disco via Bash/Python sem esse teto.

---

## Hooks (`.claude/settings.json`)

Todos leves (rodam em milissegundos, sem chamada de rede/LLM) e a maioria **não-bloqueante por padrão** — avisam, nunca abortam a operação. Ficam em `hooks/` deste plugin; `scripts/scaffold_cliente.py` já copia os arquivos para `.claude/hooks/` do projeto novo e escreve o `settings.json` com o wiring abaixo, lendo o evento/matcher direto da docstring de cada hook (ver `templates/settings.json.example`).

| Hook | Evento | Bloqueia? | O que faz |
|---|---|---|---|
| `validar_notebook.py` | `PostToolUse`, `Edit\|Write` | Não | JSON válido + `ast.parse` por célula de código de um `.ipynb` editado |
| `lembrete_orquestracao.py` | `PostToolUse`, `Edit\|Write` | Não | Se o arquivo é notebook em `datalake/_tech-sync/silver/`\|`gold/`, lembra de conferir o CSV de orquestração (Fabric) ou `databricks.yml`/`resources/` (Databricks) e o `PROJETO.md` |
| `lembrete_log_vivo.py` | `PostToolUse`, `Edit\|Write` | Não | Se o arquivo é um checkpoint de entrega (`especificacao.md`, `@client_context/`, `datalake/documentacao/`), lembra de registrar no `PROJETO.md` |
| `lembrete_padrao_sparksql.py` | `PostToolUse`, `Edit\|Write` | Não | Conta `WITH` (CTE) contra `CREATE OR REPLACE TEMP VIEW` num `.ipynb` editado; se CTE predominar, avisa que o notebook pode não seguir o padrão de temp views de `references/03-datalake-core.md` |
| `lembrete_mudanca_estrutural.py` | `PostToolUse`, `Bash` | Não | Se o comando parece reorganizar pastas (`mkdir`, `mv`, `git mv`, `rmdir`, fora de `historico/`), lembra de refletir a mudança em `@client_context/` e em `PROJETO.md` (Decisões) |
| `bloquear_tmdl.py` | `PreToolUse`, `Edit\|Write` | **Sim** (exit 2) | Impede edição direta de `.tmdl`. Escape hatch: `PERMITIR_EDICAO_TMDL=1` |
| `guardar_comando_destrutivo.py` | `PreToolUse`, `Bash` | **Sim** (exit 2) | Impede `rm -rf`, `DROP TABLE/DATABASE/SCHEMA`, `TRUNCATE`, `DELETE FROM` sem `WHERE`, `git push --force`, `git reset --hard`, `databricks bundle destroy` sem `--confirmar`. Escape hatch: `PERMITIR_COMANDO_DESTRUTIVO=1` ou incluir `--confirmar` no próprio comando |

**Mecanismo de bloqueio**: um `PreToolUse` que termina com `sys.exit(2)` nega a chamada da ferramenta; a mensagem impressa em `stderr` volta para o agente como motivo da recusa. Um `PostToolUse` nunca bloqueia (a ferramenta já rodou) — serve só para avisar; por isso os hooks não-bloqueantes são sempre encadeados com `|| true` no `command` do `settings.json`, para nunca derrubar o fluxo mesmo se o script falhar por outro motivo.

**Toda regra bloqueante deste harness tem uma válvula de escape documentada** (variável de ambiente). Isso é deliberado: um hook que trava o agente sem saída força a pessoa a desabilitar o hook inteiro (ou pior, a pular `--dangerously-skip-permissions`) na primeira exceção legítima — a válvula de escape mantém o gate útil no dia a dia comum sem virar um bloqueio absoluto.

**Interpretador Python**: o `settings.json.example` assume `python` disponível no `PATH`. Se isso não resolver no seu ambiente (comum em Windows com múltiplas instalações), troque o `command` de cada hook para o caminho absoluto do interpretador (ex.: `C:/Python314/python.exe .claude/hooks/validar_notebook.py`).
