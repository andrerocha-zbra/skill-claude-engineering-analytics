"""Cria a arvore-padrao "tecnologia-first" de um novo projeto de dados (kickoff).

Sucessor em Python do scaffold-projeto.example.ps1 (que so criava pastas). Alem da
arvore de pastas por banda numerada, este script gera PROJETO.md/AGENTS.md/CLAUDE.md na
raiz, o esqueleto de orquestracao de dados (CSV metadata-driven no Fabric, ou
databricks.yml no Databricks), copia os hooks do plugin para .claude/hooks/ e escreve
.claude/settings.json com eles ja wired, e roda `git init` (salvo --sem-git).

Client-agnostico: nada de nome de cliente/empresa hardcoded -- tudo vem de argumento.
Idempotente e nao-destrutivo: nenhum arquivo existente e sobrescrito (nem com --forcar --
--forcar so libera entrar numa pasta --destino que ja exista e nao esteja vazia).

Templates aqui sao versoes minimas, para o script rodar sem depender de outros arquivos.
Os templates completos (mais ricos) do plugin vivem em ../templates/ -- quem quiser usa-los
na integra pode copia-los por cima depois (eles tambem nunca sao sobrescritos por engano).

Uso:
    python scaffold_cliente.py --cliente "Nome Cliente" --cloud fabric \\
        --tecnologias powerbi,datalake,ml --dominios doadores,doacoes \\
        --destino C:/repos/NomeCliente
"""
import argparse
import json
import re
import shutil
import subprocess
import unicodedata
from datetime import date
from pathlib import Path

TECNOLOGIAS_CONHECIDAS = {"powerbi", "datalake", "ml"}

TEMPLATE_README_RARA = """# {pasta}/

Pasta rara. A maior parte do conteudo tecnico (padroes, roteiros, scripts de scaffold)
mora na skill instalada como plugin, nao em cada projeto -- isso evita duplicar a
correcao de um padrao em varios clientes quando ele muda.

Use esta pasta so quando surgir algo genuinamente especifico deste projeto, que nao faz
sentido subir para a skill generica. Detalhe: references/01-estrutura-e-nomenclatura.md,
secao "Pastas raras".
"""

COLUNAS_CSV = [
    "is_active", "execution_order", "layer", "domain", "subdomain", "ddd_type",
    "business_entity", "notebook_name", "owner", "source_system", "business_definition",
    "primary_key", "target_schema", "target_table", "load_method", "watermark_enabled",
    "watermark_column", "watermark_start_value", "watermark_lookback_days", "env",
    "timeout_minutes", "retry_count", "notebook_id",
]

DATABRICKS_YML_TEMPLATE = """# Databricks Asset Bundle minimo -- preencher antes do primeiro deploy.
# TODO: workspace host/profile e os targets conforme o ambiente real do cliente.
bundle:
  name: {cliente_slug}

# TODO: include:
#   - resources/*.yml

targets:
  dev:
    mode: development
    default: true
    # TODO: workspace:
    #   host: https://TODO.cloud.databricks.com

  prod:
    mode: production
    # TODO: workspace:
    #   host: https://TODO.cloud.databricks.com
"""

GITIGNORE_TEMPLATE = """.DS_Store
Thumbs.db
.vscode/
.idea/

__pycache__/
*.pyc
.ipynb_checkpoints/
.venv/
env/
.env
*.env

.pbi/
*.pbix
**/.pbi/localSettings.json
**/*.SemanticModel/.pbi/
**/*.Report/.pbi/

spark-warehouse/
metastore_db/
derby.log

*.parquet
*.csv.bak
/tmp/
_scratch/

*.key
*.pem
secrets.*
.databrickscfg

backup/
*_bckp/
"""


# ------------------------------------------------------------------ helpers genericos

def slug(nome: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "-", sem_acento).strip("-").lower() or "projeto"


def criar_dir(caminho: Path) -> None:
    if caminho.exists():
        return
    caminho.mkdir(parents=True)
    print(f"  + {caminho}/")


def escrever_se_nao_existir(caminho: Path, conteudo: str) -> bool:
    """Escreve o arquivo so se ele ainda nao existir -- nunca sobrescreve (idempotente)."""
    if caminho.exists():
        print(f"  = {caminho} (mantido)")
        return False
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(conteudo)
    print(f"  + {caminho}")
    return True


# ------------------------------------------------------------------ templates de documentacao raiz
# Versoes minimas (o script nao depende de ../templates/); o conteudo abaixo tem acentuacao
# normal em portugues -- e documentacao final para humano, diferente do .ipynb gerado por
# novo_notebook.py, que fica sem acento por exigencia de import-safe no Fabric.

def template_projeto_md(cliente: str, cloud: str, tecnologias: list, dominios: list, hoje: str) -> str:
    lista_tecnologias = ", ".join(tecnologias) if tecnologias else "TODO"
    lista_dominios = ", ".join(dominios) if dominios else "TODO"
    return f"""# Projeto -- {cliente}

> Manifesto + log vivo. Atualizar a cada trabalho relevante, sem esperar o usuario pedir.
> Template minimo gerado por `scaffold_cliente.py`; versao mais rica em `../templates/PROJETO.md`.

## Visao geral

- **Cliente:** {cliente}
- **Cloud de dados:** {cloud}
- **Tecnologias:** {lista_tecnologias}
- **Dominios/produtos:** {lista_dominios}
- **Owner:** TODO
- **Inicio:** {hoje}

## Estado por fase

| Fase | Estado | Notas |
|------|--------|-------|
| 0. Intake | | |
| 1. Dados (Silver/Gold) | | |
| 2. Modelagem | | |
| 3. DAX | | |
| 4. Frontend | | |
| 5. Doc + Handoff | | |

## Decisoes (gates)

| Data | Decisao | Motivo |
|------|---------|--------|
| | | |

## Log

<!-- Formato: - [AAAA-MM-DD HH:mm] {{Tecnologia}} {{Dominio}}: o que foi feito (refs IDs/arquivos) -->

- [{hoje}] Master {cliente}: estrutura de projeto criada (scaffold_cliente.py)
"""


def template_agents_md(cliente: str) -> str:
    return f"""# AGENTS.md

Ponto de entrada para agentes neste repositorio (projeto {cliente}). Este arquivo define
so a inicializacao; as regras estaveis ficam em `CLAUDE.md` e o estado de cada frente em
`PROJETO.md`.

## Inicializacao obrigatoria

Antes de analisar, planejar, alterar arquivos ou responder sobre este repositorio:

1. Leia `CLAUDE.md` integralmente -- e o contrato operacional estavel do projeto.
2. Leia `PROJETO.md`: secoes "Visao geral" e "Decisoes", mais as ~10 entradas mais
   recentes do "Log". Nao carregue o arquivo inteiro de saida.
3. Trate o `PROJETO.md` como fonte do estado, das decisoes e do historico vivo -- e
   atualize-o quando o trabalho mudar estrutura, camada, regra de carga, origem, destino
   ou decisao tecnica.

## Antes de agir

Pergunte ao usuario antes de: apagar dados, trocar schema de producao, mudar segredo,
mudar estrategia de carga, sobrescrever historico, ou commitar/fazer push (git so quando
o usuario pedir explicitamente).
"""


TABELA_ROTEAMENTO = """## Quando fizer isso, use aquilo

| Situacao | Use |
|---|---|
| Criar notebook Silver/Gold novo | `scripts/novo_notebook.py` (ja aplica o padrao de temp views e os quality gates) |
| Duvida de padrao Spark SQL/medallion | `references/03-datalake-core.md` + overlay da nuvem (`03a`/`03b`) |
| Modelagem/medidas Power BI | `references/04-powerbi-modelagem-dax.md` |
| Visual customizado (HTML/DAX) | `references/05-powerbi-frontend.md` |
| Documentar um PBIP / gerar handoff | `references/06-doc-e-handoff.md` |
| Reorganizar algo que ja existe no projeto | `references/09-refatorar-projeto-existente.md` + `scripts/avaliar_projeto_existente.py` |
| Fechar uma entrega | Atualizar `PROJETO.md` (Log) -- nao esperar o hook lembrar, ele so avisa |
"""


def template_claude_md(cliente: str, cloud: str, tecnologias: list, dominios: list, preferencias_trabalho: str = "") -> str:
    lista_tecnologias = ", ".join(tecnologias) if tecnologias else "TODO"
    lista_dominios = ", ".join(dominios) if dominios else "TODO"
    secao_preferencias = ""
    if preferencias_trabalho.strip():
        secao_preferencias = (
            "\n## Preferencias de trabalho\n\n"
            "Herdadas de `company-profiles/<empresa>/preferencias-trabalho.md` (onboarding "
            "de empresa). Sobrescreva aqui se este projeto especifico precisar de algo diferente.\n\n"
            f"{preferencias_trabalho.strip()}\n"
        )
    return f"""# CLAUDE.md

Instrucoes locais para agentes neste repositorio (projeto {cliente}). Regras estaveis de
operacao ficam aqui; o estado e o diario de execucao ficam em `PROJETO.md`. Bootstrap de
inicializacao em `AGENTS.md`.

## Contexto

- **Cliente/projeto:** {cliente}
- **Cloud de dados:** {cloud}
- **Tecnologias:** {lista_tecnologias}
- **Dominios:** {lista_dominios}
- **Idioma padrao:** portugues brasileiro, com acentos (excecao: texto dentro de um
  notebook `.ipynb` -- codigo, comentario, celula Markdown -- que fica sem acento por
  compatibilidade de import).

## Regras invioraveis

1. PT-BR com acentos em toda documentacao/spec/texto client-facing; notebooks `.ipynb`
   ficam sem acento (import-safe).
2. Git: nunca commitar nem fazer push sem o usuario pedir explicitamente.
3. Perguntar antes de apagar dados, trocar schema de producao, mudar segredo, mudar
   estrategia de carga (FULL <-> MERGE) ou sobrescrever historico.
4. Notebooks nunca citam artefato interno (`CLAUDE.md`, `AGENTS.md`, skills, Issues) por
   nome -- o entregavel descreve o fato em si.
5. Antes de reimportar um `.ipynb` editado fora da ferramenta cloud, rodar
   `limpar_notebook_import.py` (source como lista de linhas, outputs zerados, UTF-8 sem BOM).

## Estrutura

Ver `PROJETO.md` para o estado atual de cada frente e `@client_context/` para regras de
negocio, catalogo de dados e decisoes tecnicas duraveis.

{TABELA_ROTEAMENTO}{secao_preferencias}"""


# ------------------------------------------------------------------ arvore de pastas

def montar_estrutura(base: Path, cliente_slug: str, cloud: str, tecnologias: list, dominios: list) -> None:
    print("Arvore de pastas:")

    for nome in (".skills", "prompts"):
        criar_dir(base / nome)
        escrever_se_nao_existir(base / nome / "README.md", TEMPLATE_README_RARA.format(pasta=nome))

    for sub in ("processos", "design-system", "data/catalogos", "fontes-externas"):
        criar_dir(base / "@client_context" / sub)

    criar_dir(base / "apresentacoes")
    criar_dir(base / "reunioes")

    if "powerbi" in tecnologias:
        alvos = dominios or [""]
        for dominio in alvos:
            dp = (base / "powerbi" / dominio) if dominio else (base / "powerbi")
            criar_dir(dp / "docs")
            # pastas de pagina/entidade (estrutura filha) nascem sob demanda, nao aqui --
            # nao ha entidade nenhuma antes da primeira spec/pagina existir de verdade.

    if "datalake" in tecnologias:
        datalake = base / "datalake"
        for sub in ("silver", "gold", "ml", "utils"):
            criar_dir(datalake / "_tech-sync" / sub)
        criar_dir(datalake / "_tech-sync" / "tests")
        criar_dir(datalake / "documentacao")
        # pastas <camada>/<entidade>/ dentro de documentacao/ nascem junto com o primeiro
        # notebook daquela entidade (espelham o nome criado em _tech-sync/), nao aqui.

        if cloud == "fabric":
            escrever_se_nao_existir(
                datalake / "_tech-sync" / "metadata_driven" / "metadata_driven_orchestration.csv",
                ";".join(COLUNAS_CSV) + "\n",
            )
        else:
            escrever_se_nao_existir(
                datalake / "_tech-sync" / "databricks.yml",
                DATABRICKS_YML_TEMPLATE.format(cliente_slug=cliente_slug),
            )

    if "ml" in tecnologias:
        criar_dir(base / "ml")

    for tecnologia in tecnologias:
        if tecnologia not in TECNOLOGIAS_CONHECIDAS:
            print(f"  ! tecnologia desconhecida ignorada: {tecnologia}")

    criar_dir(base / "tasks")
    criar_dir(base / "historico")
    criar_dir(base / "backup")


# ------------------------------------------------------------------ hooks + settings.json

def classificar_hook_por_nome(nome_arquivo: str):
    """Fallback quando o hook nao documenta o proprio wiring (ver extrair_evento_matcher):
    heuristica por nome de arquivo. Hook de comando destrutivo vira gate PreToolUse sobre
    Bash; os demais (validacao/lembrete de notebook) viram PostToolUse sobre Edit|Write."""
    chave = nome_arquivo.lower()
    if any(termo in chave for termo in ("destrut", "comando")):
        return "PreToolUse", "Bash"
    return "PostToolUse", "Edit|Write"


PADRAO_DOCSTRING_HOOK = re.compile(r'"""Hook (\w+) \(([^)]+)\):')


def extrair_evento_matcher(caminho_hook: Path):
    """Cada hook deste plugin documenta o proprio wiring na 1a linha da docstring,
    formato '\"\"\"Hook <Evento> (<Matcher>): ...' (ex.: 'Hook PreToolUse (Bash): ...').
    Ler isso direto do arquivo e mais confiavel que adivinhar pelo nome -- so cai para a
    heuristica de nome se um hook futuro nao seguir essa convencao."""
    try:
        primeira_linha = caminho_hook.read_text(encoding="utf-8").splitlines()[0]
    except (OSError, IndexError):
        return classificar_hook_por_nome(caminho_hook.name)
    m = PADRAO_DOCSTRING_HOOK.match(primeira_linha)
    if m:
        return m.group(1), m.group(2)
    return classificar_hook_por_nome(caminho_hook.name)


def copiar_hooks(destino: Path) -> list:
    """Copia os hooks do plugin para <destino>/.claude/hooks/ e retorna uma lista de
    (nome_arquivo, evento, matcher) para montar_settings_json() usar no wiring."""
    diretorio_hooks_plugin = Path(__file__).resolve().parent.parent / "hooks"
    encontrados = sorted(diretorio_hooks_plugin.glob("*.py")) if diretorio_hooks_plugin.is_dir() else []

    print("Hooks:")
    if not encontrados:
        print(f"  ! nenhum hook .py encontrado em {diretorio_hooks_plugin}")
        print("  ! .claude/settings.json sera escrito sem hooks wired -- copie os hooks do "
              "plugin para la e ajuste settings.json manualmente quando existirem.")
        return []

    destino_hooks = destino / ".claude" / "hooks"
    destino_hooks.mkdir(parents=True, exist_ok=True)
    hooks_wiring = []
    for origem in encontrados:
        evento, matcher = extrair_evento_matcher(origem)
        alvo = destino_hooks / origem.name
        if alvo.exists():
            print(f"  = {alvo} (mantido)")
        else:
            shutil.copy2(origem, alvo)
            print(f"  + {alvo}  [{evento}/{matcher}]")
        hooks_wiring.append((origem.name, evento, matcher))
    return hooks_wiring


def montar_settings_json(hooks_wiring: list) -> dict:
    grupos = {}
    for nome, evento, matcher in hooks_wiring:
        grupos.setdefault((evento, matcher), []).append(nome)

    hooks = {}
    for (evento, matcher), nomes in sorted(grupos.items()):
        # "|| true" so faz sentido em hook NAO bloqueante (PostToolUse): garante que um
        # bug no hook nunca derruba o agente. Em PreToolUse os hooks bloqueiam de proposito
        # via exit code 2 (ver bloquear_tmdl.py/guardar_comando_destrutivo.py) -- "|| true"
        # ali engoliria esse exit code e desligaria o bloqueio sem avisar ninguem.
        sufixo = "" if evento == "PreToolUse" else " || true"
        entrada = {
            "matcher": matcher,
            "hooks": [
                {
                    "type": "command",
                    # ${{CLAUDE_PROJECT_DIR}} e resolvido pelo Claude Code em runtime, ja
                    # apontando para a raiz DESTE repo (nao do plugin) -- por isso os
                    # hooks precisam ter sido copiados para ca por copiar_hooks() acima.
                    "command": f'python "${{CLAUDE_PROJECT_DIR}}/.claude/hooks/{nome}"{sufixo}',
                    "timeout": 20,
                    "statusMessage": f"Rodando hook: {nome}",
                }
                for nome in nomes
            ],
        }
        hooks.setdefault(evento, []).append(entrada)

    return {"hooks": hooks}


# ------------------------------------------------------------------ perfil de empresa

def detectar_pasta_empresa(nome_empresa: str = None):
    """Localiza company-profiles/<empresa>/ neste repositorio-harness (um nivel acima de
    plugins/), para herdar preferencias de trabalho ao gerar o CLAUDE.md do projeto novo.
    Nao falha se nao achar -- so significa que o CLAUDE.md gerado fica sem essa secao."""
    raiz_harness = Path(__file__).resolve().parents[3]
    company_profiles = raiz_harness / "company-profiles"
    if not company_profiles.is_dir():
        return None
    if nome_empresa:
        candidata = company_profiles / nome_empresa
        return candidata if candidata.is_dir() else None
    pastas = [p for p in company_profiles.iterdir() if p.is_dir()]
    return pastas[0] if len(pastas) == 1 else None


def carregar_preferencias_trabalho(pasta_empresa) -> str:
    if not pasta_empresa:
        return ""
    arquivo = pasta_empresa / "preferencias-trabalho.md"
    return arquivo.read_text(encoding="utf-8") if arquivo.is_file() else ""


# ------------------------------------------------------------------ git

def rodar_git_init(destino: Path) -> None:
    try:
        resultado = subprocess.run(
            ["git", "init"], cwd=destino, capture_output=True, text=True, check=False,
        )
        if resultado.returncode == 0:
            print(f"  + git init OK em {destino}")
        else:
            print(f"  ! git init falhou (codigo {resultado.returncode}): {resultado.stderr.strip()}")
    except FileNotFoundError:
        print("  ! git nao encontrado no PATH -- pulei git init (rode manualmente depois)")


# ------------------------------------------------------------------ CLI

def main():
    parser = argparse.ArgumentParser(description="Cria a arvore-padrao de um novo projeto de dados (kickoff).")
    parser.add_argument("--cliente", required=True, help="Nome do cliente/projeto")
    parser.add_argument("--cloud", choices=["fabric", "databricks"], default="fabric")
    parser.add_argument("--tecnologias", default="powerbi,datalake", help="Lista separada por virgula (powerbi,datalake,ml)")
    parser.add_argument("--dominios", default="", help="Lista separada por virgula (ex.: doadores,doacoes)")
    parser.add_argument("--destino", required=True, help="Pasta onde o projeto sera criado")
    parser.add_argument("--empresa", default=None, help="Pasta em company-profiles/ para herdar preferencias de trabalho (opcional -- auto-detecta se houver so uma)")
    parser.add_argument("--sem-git", action="store_true", help="Nao roda git init")
    parser.add_argument("--forcar", action="store_true", help="Permite usar uma pasta --destino ja existente e nao vazia")
    args = parser.parse_args()

    tecnologias = [t.strip().lower() for t in args.tecnologias.split(",") if t.strip()]
    dominios = [d.strip().lower() for d in args.dominios.split(",") if d.strip()]

    base = Path(args.destino)
    if base.exists() and any(base.iterdir()) and not args.forcar:
        raise SystemExit(
            f"[scaffold_cliente] {base} ja existe e nao esta vazia. Use --forcar para "
            "continuar (nenhum arquivo existente sera sobrescrito de qualquer forma)."
        )

    cliente_slug = slug(args.cliente)
    hoje = date.today().strftime("%Y-%m-%d")

    print(f"Scaffold '{args.cliente}' em: {base}  (cloud={args.cloud})\n")
    base.mkdir(parents=True, exist_ok=True)

    montar_estrutura(base, cliente_slug, args.cloud, tecnologias, dominios)

    print("Documentacao raiz:")
    escrever_se_nao_existir(base / "PROJETO.md", template_projeto_md(args.cliente, args.cloud, tecnologias, dominios, hoje))
    escrever_se_nao_existir(base / "AGENTS.md", template_agents_md(args.cliente))
    pasta_empresa = detectar_pasta_empresa(args.empresa)
    preferencias_trabalho = carregar_preferencias_trabalho(pasta_empresa)
    if args.empresa and not pasta_empresa:
        print(f"  ! --empresa {args.empresa!r} nao encontrada em company-profiles/ -- CLAUDE.md sai sem preferencias herdadas")
    escrever_se_nao_existir(base / "CLAUDE.md", template_claude_md(args.cliente, args.cloud, tecnologias, dominios, preferencias_trabalho))
    escrever_se_nao_existir(base / ".gitignore", GITIGNORE_TEMPLATE)

    hooks_wiring = copiar_hooks(base)
    print(".claude/settings.json:")
    escrever_se_nao_existir(base / ".claude" / "settings.json", json.dumps(montar_settings_json(hooks_wiring), indent=2, ensure_ascii=False) + "\n")

    print("Git:")
    if args.sem_git:
        print("  = git init pulado (--sem-git)")
    else:
        rodar_git_init(base)

    print(f"\nOK. Estrutura criada em {base}.\n")
    print("Proximos passos:")
    print("  1. Revise PROJETO.md/AGENTS.md/CLAUDE.md e preencha os TODOs.")
    if "datalake" in tecnologias:
        if args.cloud == "fabric":
            print("  2. Configure o Git integration do Fabric apontando para datalake/_tech-sync/.")
        else:
            print("  2. Preencha datalake/_tech-sync/databricks.yml (workspace host/profile) e rode `databricks bundle validate`.")
    else:
        print("  2. Adicione a(s) banda(s) de tecnologia que faltarem quando o escopo crescer.")
    print("  3. Gere o primeiro notebook com novo_notebook.py, se o escopo incluir datalake.")
    if not hooks_wiring:
        print("  4. Copie os hooks do plugin para .claude/hooks/ e rode este script de novo (ou edite .claude/settings.json manualmente).")


if __name__ == "__main__":
    main()
