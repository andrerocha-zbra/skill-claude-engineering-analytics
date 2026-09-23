"""Hook PostToolUse (Edit|Write): valida .ipynb editado — JSON valido + ast.parse por celula.

Nunca bloqueia (sempre sys.exit(0)); so avisa em stderr.
"""
import ast
import json
import sys


def validar(caminho):
    try:
        with open(caminho, encoding="utf-8") as f:
            nb = json.load(f)
    except FileNotFoundError:
        return
    except json.JSONDecodeError as e:
        print(f"[validar_notebook] JSON invalido em {caminho}: {e}", file=sys.stderr)
        return

    erros = []
    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source", "")
        codigo = "".join(source) if isinstance(source, list) else source
        try:
            ast.parse(codigo)
        except SyntaxError as e:
            erros.append(f"celula {i}: {e}")

    if erros:
        print(f"[validar_notebook] {caminho} tem {len(erros)} celula(s) com erro de sintaxe:", file=sys.stderr)
        for erro in erros:
            print(f"  - {erro}", file=sys.stderr)
    else:
        print(f"[validar_notebook] OK: {caminho} ({len(nb.get('cells', []))} celulas, JSON valido, sem erro de sintaxe)")


def caminho_do_stdin():
    try:
        evento = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None
    return evento.get("tool_input", {}).get("file_path")


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else caminho_do_stdin()
    if caminho and caminho.lower().endswith(".ipynb"):
        validar(caminho)
    sys.exit(0)
