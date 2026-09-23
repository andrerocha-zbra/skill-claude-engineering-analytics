"""Avalia um projeto EXISTENTE contra a arvore-padrao do metodo (ver
references/01-estrutura-e-nomenclatura.md) e gera um relatorio de gap em Markdown.

Script SOMENTE LEITURA -- nunca escreve, move ou apaga nada dentro da pasta avaliada.
Isto e um diagnostico, nao uma migracao. A migracao em si (git mv por fatia, um commit
por banda, gates de confirmacao antes de mexer em pasta ja conectada a uma plataforma
de dados) e conduzida manualmente depois, com cada sugestao deste relatorio confirmada
pelo usuario -- ver references/09-refatorar-projeto-existente.md.

Toda deteccao de banda equivalente e de sinal de CI/CD aqui e heuristica (nome de pasta,
substring em arquivo) -- nunca um veredito. O relatorio deixa isso explicito em cada secao.

Uso:
    python avaliar_projeto_existente.py --projeto C:/repos/ProjetoExistente
    python avaliar_projeto_existente.py --projeto C:/repos/ProjetoExistente --saida C:/tmp/relatorio-gap.md
"""
import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path

BANDAS_ALVO = [
    ("@client_context", "conhecimento de negocio do cliente (regras, catalogo, glossario, fontes externas)"),
    ("reunioes", "atas e materiais de reuniao"),
    ("powerbi", "projetos Power BI (.pbip)"),
    ("datalake", "datalake -- _tech-sync/ e a unica pasta que deve ser sincronizada com a plataforma"),
    ("ml", "modelos de ML"),
    ("tasks", "rastro do trabalho, uma pasta por task"),
    ("historico", "decisoes/arquitetura supersedidas, congeladas"),
    ("backup", "arquivo/backup"),
]

# banda que nao existe com o nome exato -> (rotulo do destino sugerido, palavras-chave de busca)
HEURISTICAS_EQUIVALENTE = {
    "datalake": ("datalake/_tech-sync", ("bronze", "silver", "gold", "datalake", "lakehouse")),
    "powerbi": ("powerbi", ("powerbi", "pbip", "relatorio", "relatorios")),
    "reunioes": ("reunioes", ("reuniao", "reunioes", "ata", "atas", "minutes")),
    "@client_context": ("@client_context", ("regra", "regras", "negocio", "business", "contexto", "cliente")),
    "tasks": ("tasks", ("task", "tasks", "tarefa", "tarefas")),
}

ITENS_GOVERNANCA = ["PROJETO.md", "AGENTS.md", "CLAUDE.md", ".claude/settings.json", ".claude/hooks"]

DIRETORIOS_IGNORADOS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".ipynb_checkpoints", ".idea", ".vscode"}
PASTAS_PLATAFORMA = {".fabric"}

PADRAO_WITH = re.compile(r"\bWITH\b", re.IGNORECASE)
PADRAO_TEMP_VIEW = re.compile(r"CREATE\s+OR\s+REPLACE\s+TEMP\s+VIEW|createOrReplaceTempView", re.IGNORECASE)
PADRAO_BUNDLE_KEY = re.compile(r"^\s*bundle\s*:", re.MULTILINE)

# tabela minima p/ tirar acento sem depender de unicodedata (script fica so com os.path/re/json/argparse/datetime/pathlib)
_TABELA_SEM_ACENTO = str.maketrans(
    "áàâãäéèêëíìîïóòôõöúùûüçÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ",
    "aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC",
)


def sem_acento(texto: str) -> str:
    return texto.translate(_TABELA_SEM_ACENTO)


# ------------------------------------------------------------------ varredura (1 passada, so leitura)

def caminhar_podando(base: Path):
    """os.walk podando diretorios irrelevantes -- generator de (raiz: Path, dirs: list[str], arquivos: list[str])."""
    for raiz, dirs, arquivos in os.walk(base):
        dirs[:] = [d for d in dirs if d not in DIRETORIOS_IGNORADOS]
        yield Path(raiz), dirs, arquivos


def coletar_arquivos(base: Path):
    """Uma unica varredura -- retorna (yamls, notebooks, readmes, pastas_plataforma), todos Path."""
    yamls, notebooks, readmes, pastas_plataforma = [], [], [], []
    for raiz, dirs, arquivos in caminhar_podando(base):
        for nome in dirs:
            if nome.lower() in PASTAS_PLATAFORMA:
                pastas_plataforma.append(raiz / nome)
        for nome in arquivos:
            baixo = nome.lower()
            caminho = raiz / nome
            if baixo.endswith((".yml", ".yaml")):
                yamls.append(caminho)
            if baixo.endswith(".ipynb"):
                notebooks.append(caminho)
            if baixo.startswith("readme") and baixo.endswith(".md"):
                readmes.append(caminho)
    return yamls, notebooks, readmes, pastas_plataforma


def coletar_pastas_nivel_1_2(base: Path):
    """Pastas de 1o e 2o nivel do projeto avaliado, ignorando ocultas -- usadas so pela
    heuristica de equivalencia de banda (item 3 do relatorio)."""
    encontradas = []
    try:
        nivel1 = [p for p in base.iterdir() if p.is_dir() and not p.name.startswith(".")]
    except OSError:
        return encontradas
    for p in nivel1:
        encontradas.append(p)
        try:
            encontradas.extend(s for s in p.iterdir() if s.is_dir() and not s.name.startswith("."))
        except OSError:
            continue
    return encontradas


# ------------------------------------------------------------------ deteccao de risco de CI/CD

def detectar_sinais_cicd(base: Path, yamls: list, readmes: list, pastas_plataforma: list) -> list:
    """Heuristica de sinal de integracao Git de plataforma de dados ja ativa. Qualquer sinal
    encontrado vira aviso no topo do relatorio -- ver montar_relatorio()."""
    sinais = []

    for caminho in yamls:
        rel = caminho.relative_to(base)
        if caminho.name.lower() == "databricks.yml":
            sinais.append(f"arquivo `{rel}` (nome padrao de Databricks Asset Bundle)")
            continue
        try:
            conteudo = caminho.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "databricks bundle" in conteudo.lower() or PADRAO_BUNDLE_KEY.search(conteudo):
            sinais.append(f"arquivo `{rel}` menciona 'databricks bundle' ou tem chave `bundle:`")

    for pasta in pastas_plataforma:
        sinais.append(f"pasta `{pasta.relative_to(base)}` (nome sugere Git folder de plataforma ja configurado)")

    for readme in readmes:
        try:
            conteudo = readme.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "git integration" in conteudo.lower():
            sinais.append(f"`{readme.relative_to(base)}` menciona 'Git integration'")

    return sinais


# ------------------------------------------------------------------ bandas padrao

def avaliar_bandas(base: Path) -> list:
    pastas = coletar_pastas_nivel_1_2(base)
    linhas = []
    for banda, descricao in BANDAS_ALVO:
        caminho_exato = base / banda
        if caminho_exato.is_dir():
            linha = f"- `{banda}/` -- **existe** ({descricao})"
            if banda == "datalake":
                if (caminho_exato / "_tech-sync").is_dir():
                    linha += "; `_tech-sync/` -- **existe**"
                else:
                    linha += (
                        "; `_tech-sync/` -- **nao existe** (ver `references/01-estrutura-e-nomenclatura.md` "
                        "antes de criar -- e a unica pasta que a plataforma de dados deve enxergar)"
                    )
            linhas.append(linha)
            continue

        destino = HEURISTICAS_EQUIVALENTE.get(banda)
        candidatas = []
        if destino:
            rotulo_destino, palavras_chave = destino
            for pasta in pastas:
                nome_normalizado = sem_acento(pasta.name).lower()
                if any(chave in nome_normalizado for chave in palavras_chave):
                    candidatas.append(pasta)

        if candidatas:
            lista = ", ".join(f"`{p.relative_to(base)}`" for p in candidatas)
            linhas.append(
                f"- `{banda}/` -- nao existe com este nome. Possivel equivalente (confirme antes de "
                f"mover, isto NAO e um veredito) para virar `{rotulo_destino}/`: {lista}"
            )
        else:
            linhas.append(f"- `{banda}/` -- nao existe, nenhuma candidata equivalente encontrada")
    return linhas


# ------------------------------------------------------------------ governanca

def avaliar_governanca(base: Path) -> list:
    linhas = []
    for item in ITENS_GOVERNANCA:
        existe = (base / item).exists()
        linhas.append(f"- `{item}` -- {'presente' if existe else 'ausente'}")
    return linhas


# ------------------------------------------------------------------ notebooks (heuristica textual)

def classificar_notebook(caminho: Path):
    """Heuristica textual simples -- NAO e auditoria de qualidade, e so um indicio de estilo.
    Conta 'WITH' (CTE) vs CREATE OR REPLACE TEMP VIEW / createOrReplaceTempView nas celulas de
    codigo. Predomina temp view -> parece seguir o padrao SQL-first com temp views nomeadas.
    Predomina WITH (ou nenhum dos dois padroes some claramente) -> tratado como sinal de que o
    notebook NAO segue esse padrao (rotulado 'parece PySpark encadeado') -- e uma aproximacao,
    confirmar sempre lendo o notebook.

    Retorna (n_with, n_temp_view, rotulo). Em erro de leitura retorna (None, None, motivo).
    """
    try:
        with open(caminho, encoding="utf-8") as f:
            nb = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return None, None, f"nao deu para ler o notebook ({e})"

    pedacos_codigo = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source", "")
        pedacos_codigo.append("".join(source) if isinstance(source, list) else source)
    texto = "\n".join(pedacos_codigo)

    n_with = len(PADRAO_WITH.findall(texto))
    n_temp_view = len(PADRAO_TEMP_VIEW.findall(texto))

    if n_with == 0 and n_temp_view == 0:
        rotulo = "nao deu para classificar"
    elif n_temp_view >= n_with:
        rotulo = "parece Spark SQL com temp views"
    else:
        rotulo = "parece PySpark encadeado"

    return n_with, n_temp_view, rotulo


# ------------------------------------------------------------------ relatorio

def montar_relatorio(base: Path) -> str:
    agora = datetime.now().strftime("%Y-%m-%d %H:%M")
    yamls, notebooks, readmes, pastas_plataforma = coletar_arquivos(base)
    sinais_cicd = detectar_sinais_cicd(base, yamls, readmes, pastas_plataforma)

    linhas = [
        "# Relatorio de avaliacao -- projeto existente",
        "",
        f"- **Pasta avaliada:** `{base}`",
        f"- **Gerado em:** {agora}",
        "",
    ]

    if sinais_cicd:
        linhas += [
            "## ATENCAO -- risco de CI/CD",
            "",
            "Sinais de que esta pasta (ou uma subpasta) ja pode estar conectada a uma plataforma "
            "de dados via Git. Nao mova nem renomeie nada aqui antes de confirmar como reconectar "
            "essa integracao -- um `git mv` por baixo dela pode quebrar a sincronizacao.",
            "",
        ]
        linhas += [f"- {sinal}" for sinal in sinais_cicd]
        linhas.append("")

    linhas += [
        "## Bandas padrao",
        "",
        "Para cada banda-alvo: existe com este nome, nao existe, ou ha pasta(s) com nome parecido "
        "(possivel equivalente -- confirme com o usuario antes de mover, isto nao e um veredito).",
        "",
    ]
    linhas += avaliar_bandas(base)
    linhas.append("")

    linhas += ["## Governanca", ""]
    linhas += avaliar_governanca(base)
    linhas.append("")

    linhas += ["## Notebooks encontrados", ""]
    if not notebooks:
        linhas.append("Nenhum arquivo `.ipynb` encontrado.")
    else:
        linhas += [
            "Heuristica textual simples (NAO e auditoria de qualidade) -- so um indicio de estilo "
            "de escrita; confirmar sempre lendo o notebook antes de decidir qualquer coisa a partir "
            "disto.",
            "",
        ]
        for caminho in sorted(notebooks):
            rel = caminho.relative_to(base)
            n_with, n_temp_view, rotulo = classificar_notebook(caminho)
            if n_with is None:
                linhas.append(f"- `{rel}` -- {rotulo}")
            else:
                linhas.append(f"- `{rel}` -- WITH: {n_with}, TEMP VIEW: {n_temp_view} -> {rotulo}")
    linhas.append("")

    linhas += ["## Proximos passos sugeridos", ""]
    linhas.append(
        "1. Adicionar governanca sem mover nada: criar `PROJETO.md`/`AGENTS.md`/`CLAUDE.md`/"
        "`.claude/hooks/` a partir dos templates da skill, sem tocar em nenhuma pasta existente."
    )
    linhas.append(
        "2. Migrar a estrutura em fatias, uma banda por vez, cada fatia com o proprio commit "
        "usando `git mv` (preserva o historico do arquivo)."
    )
    if sinais_cicd:
        linhas.append(
            "3. So depois de tudo migrado: reconectar a integracao Git da plataforma de dados "
            "apontando para o novo caminho de `_tech-sync/` -- nunca antes (este relatorio "
            "detectou sinal de CI/CD acima)."
        )
    else:
        linhas.append(
            "3. Se, ao migrar, aparecer alguma integracao Git de plataforma de dados que este "
            "relatorio nao detectou, reconectar essa integracao so depois de tudo migrado -- "
            "nunca antes."
        )
    linhas.append("")

    return "\n".join(linhas)


# ------------------------------------------------------------------ CLI

def main():
    parser = argparse.ArgumentParser(
        description="Avalia um projeto existente contra a arvore-padrao e gera um relatorio de "
        "gap em Markdown. Somente leitura -- nunca escreve/move/apaga nada na pasta avaliada."
    )
    parser.add_argument("--projeto", required=True, help="Caminho do projeto existente a avaliar")
    parser.add_argument(
        "--saida", default="",
        help="Caminho do relatorio .md a escrever, fora da pasta avaliada. Sem isto, imprime no stdout.",
    )
    args = parser.parse_args()

    base = Path(args.projeto)
    if not base.exists():
        raise SystemExit(f"[avaliar_projeto_existente] pasta nao encontrada: {base}")
    if not base.is_dir():
        raise SystemExit(f"[avaliar_projeto_existente] {base} nao e uma pasta")
    try:
        base = base.resolve()
        list(base.iterdir())
    except PermissionError:
        raise SystemExit(f"[avaliar_projeto_existente] sem permissao de leitura em {base}")
    except OSError as e:
        raise SystemExit(f"[avaliar_projeto_existente] erro ao ler {base}: {e}")

    relatorio = montar_relatorio(base)

    if not args.saida:
        print(relatorio)
        return

    caminho_saida = Path(args.saida).resolve()
    dentro_da_pasta_avaliada = True
    try:
        caminho_saida.relative_to(base)
    except ValueError:
        dentro_da_pasta_avaliada = False
    if dentro_da_pasta_avaliada:
        raise SystemExit(
            f"[avaliar_projeto_existente] --saida ({caminho_saida}) fica dentro da pasta avaliada "
            f"({base}). Este script e somente leitura e nunca escreve dentro do projeto avaliado -- "
            "escolha um caminho de saida fora dela."
        )

    try:
        caminho_saida.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho_saida, "w", encoding="utf-8", newline="\n") as f:
            f.write(relatorio)
    except OSError as e:
        raise SystemExit(f"[avaliar_projeto_existente] erro ao escrever {caminho_saida}: {e}")

    print(f"  + {caminho_saida}")


if __name__ == "__main__":
    main()
