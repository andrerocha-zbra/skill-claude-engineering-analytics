"""Hook PostToolUse (Bash): avisa quando um comando parece reorganizar a arvore de pastas
do projeto (mkdir, mv, git mv, rmdir), para lembrar de refletir a mudanca em
@client_context/ e, se for decisao de arquitetura, em PROJETO.md (Decisoes).

Heuristica por padrao de comando, nao uma auditoria semantica -- comandos dentro de
historico/ sao ignorados de proposito (mudanca lá dentro nao é reorganizacao viva, é
congelamento de algo ja supersedido).

Nunca bloqueia (sempre sys.exit(0)); so avisa em stderr.
"""
import json
import re
import sys

PADRAO_COMANDO = re.compile(r"\b(mkdir|rmdir|git\s+mv|mv)\b", re.IGNORECASE)


def comando_do_stdin():
    try:
        evento = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None
    return evento.get("tool_input", {}).get("command", "")


if __name__ == "__main__":
    comando = comando_do_stdin() or ""

    if "historico/" not in comando.replace("\\", "/") and PADRAO_COMANDO.search(comando):
        print(
            "[lembrete_mudanca_estrutural] Comando parece reorganizar pastas:\n"
            f"  {comando}\n"
            "Se isso mudou a arquitetura do projeto, atualize @client_context/ "
            "e, se for decisao relevante, registre em PROJETO.md (Decisoes).",
            file=sys.stderr,
        )

    sys.exit(0)
