"""Hook PreToolUse (Bash): bloqueia comandos destrutivos sem confirmacao explicita.

Aplica o invariante de seguranca do metodo ("scripts destrutivos: dry-run primeiro,
mostrar resultado, so entao --confirmar") como gate real, nao so como regra escrita
em CLAUDE.md.

Bloqueia via exit code 2 (PreToolUse: exit 2 + stderr = tool call negada).

Escape hatch: variavel de ambiente PERMITIR_COMANDO_DESTRUTIVO=1, ou o proprio
comando ja conter a flag --confirmar (convencao deste harness para scripts
administrativos — ver METODO.md).
"""
import json
import os
import re
import sys

PADROES_DESTRUTIVOS = [
    r"\brm\s+-rf\b",
    r"\bDROP\s+TABLE\b",
    r"\bDROP\s+DATABASE\b",
    r"\bDROP\s+SCHEMA\b",
    r"\bTRUNCATE\s+TABLE\b",
    r"\bDELETE\s+FROM\b(?!.*\bWHERE\b)",
    r"\bgit\s+push\s+.*--force\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\bdatabricks\s+bundle\s+destroy\b",
]


def comando_do_stdin():
    try:
        evento = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None
    return evento.get("tool_input", {}).get("command", "")


if __name__ == "__main__":
    comando = comando_do_stdin() or ""

    if os.environ.get("PERMITIR_COMANDO_DESTRUTIVO") or "--confirmar" in comando:
        sys.exit(0)

    for padrao in PADROES_DESTRUTIVOS:
        if re.search(padrao, comando, re.IGNORECASE):
            print(
                f"[guardar_comando_destrutivo] Comando bloqueado (padrao destrutivo: {padrao}):\n"
                f"  {comando}\n"
                "Rode em modo dry-run primeiro e adicione --confirmar quando o resultado "
                "estiver validado, ou defina PERMITIR_COMANDO_DESTRUTIVO=1 se for deliberado.",
                file=sys.stderr,
            )
            sys.exit(2)

    sys.exit(0)
