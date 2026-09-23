"""Hook PostToolUse (Edit|Write): avisa quando um notebook editado parece nao seguir o
padrao Spark-SQL-first de temp views nomeadas (references/03-datalake-core.md).

Heuristica leve, nao uma auditoria: conta ocorrencias de `WITH ` (CTE) contra
`CREATE OR REPLACE TEMP VIEW` / `createOrReplaceTempView` no conteudo das celulas de
codigo. Se CTE predominar, avisa -- e indicio, nao veredito (a mesma heuristica que
avaliar_projeto_existente.py usa para notebooks de um projeto inteiro, aqui aplicada a
um unico notebook logo apos a edicao).

Nunca bloqueia (sempre sys.exit(0)); so avisa em stderr.
"""
import json
import re
import sys

PADRAO_CTE = re.compile(r"\bWITH\b", re.IGNORECASE)
PADRAO_TEMP_VIEW = re.compile(r"createOrReplaceTempView|CREATE\s+OR\s+REPLACE\s+TEMP\s+VIEW", re.IGNORECASE)


def avaliar(caminho):
    try:
        with open(caminho, encoding="utf-8") as f:
            nb = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    codigo = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source", "")
        codigo.append("".join(source) if isinstance(source, list) else source)
    texto = "\n".join(codigo)

    ctes = len(PADRAO_CTE.findall(texto))
    temp_views = len(PADRAO_TEMP_VIEW.findall(texto))

    if ctes > temp_views and ctes > 0:
        print(
            f"[lembrete_padrao_sparksql] {caminho}: {ctes} ocorrencia(s) de WITH (CTE) contra "
            f"{temp_views} de CREATE OR REPLACE TEMP VIEW. Isso e so um indicio, nao um erro -- "
            "confira se o notebook deveria seguir o padrao de cadeia de temp views nomeadas, "
            "uma por celula, descrito em references/03-datalake-core.md.",
            file=sys.stderr,
        )


def caminho_do_stdin():
    try:
        evento = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None
    return evento.get("tool_input", {}).get("file_path")


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else caminho_do_stdin()
    if caminho and caminho.lower().endswith(".ipynb"):
        avaliar(caminho)
    sys.exit(0)
