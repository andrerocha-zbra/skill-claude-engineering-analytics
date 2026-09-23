"""Hook PreToolUse (Edit|Write): bloqueia edicao direta de arquivos .tmdl.

Regra do metodo (ate hoje so escrita em prosa no CLAUDE.md de cada projeto): "nunca
editar TMDL na mao" — modelo Power BI se altera via spec (ESPEC.md/task/02_modelagem.md)
+ powerbi-modeling-mcp, nunca editando o arquivo .tmdl diretamente (edicao manual
corrompe o projeto / gera merge hell).

Bloqueia via exit code 2 (mecanismo padrao de PreToolUse do Claude Code: exit 2 +
mensagem em stderr = tool call negada, a mensagem volta pro agente como motivo).

Escape hatch deliberado: defina a variavel de ambiente
PERMITIR_EDICAO_TMDL=1 para permitir a edicao em casos excepcionais (ex.: correcao
cirurgica orientada por suporte da Microsoft). Isso e intencional — todo hook
bloqueante deste harness precisa ter uma valvula de escape documentada.
"""
import json
import os
import sys


def caminho_do_stdin():
    try:
        evento = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None
    return evento.get("tool_input", {}).get("file_path", "")


if __name__ == "__main__":
    caminho = caminho_do_stdin() or ""

    if caminho.lower().endswith(".tmdl") and not os.environ.get("PERMITIR_EDICAO_TMDL"):
        print(
            f"[bloquear_tmdl] Edicao direta de {caminho} bloqueada.\n"
            "Modelo Power BI se altera via spec (task/02_modelagem.md) + powerbi-modeling-mcp, "
            "nunca editando .tmdl na mao (corrompe o projeto).\n"
            "Excecao deliberada: rode com PERMITIR_EDICAO_TMDL=1 se for mesmo necessario.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)
