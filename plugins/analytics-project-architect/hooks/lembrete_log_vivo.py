"""Hook PostToolUse (Edit|Write): lembra de registrar entrada no PROJETO.md quando um
artefato de "checkpoint de entrega" e criado/editado.

Diferente de lembrete_orquestracao.py (que dispara em QUALQUER edicao de notebook
Silver/Gold), este hook so dispara em pontos de checkpoint de baixo ruido, para nao
avisar a cada edicao intermediaria:
  - especificacao fechada (powerbi/*/especificacao.md)
  - regra de negocio ou outro conteudo de contexto do cliente (@client_context/*)
  - entidade de datalake documentada (datalake/documentacao/*)

Nunca bloqueia; so avisa em stderr.
"""
import json
import sys

GATILHOS = (
    "/especificacao.md",
    "@client_context/",
    "/datalake/documentacao/",
)


def main():
    try:
        evento = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    caminho = evento.get("tool_input", {}).get("file_path", "")
    caminho_norm = caminho.replace("\\", "/").lower()

    if "/historico/" in caminho_norm or caminho_norm.endswith("projeto.md"):
        return

    if any(g in caminho_norm for g in GATILHOS):
        print(
            f"[lembrete_log_vivo] {caminho} parece um checkpoint de entrega. "
            "Se isso fechar algo relevante, adicione uma linha em PROJETO.md > ## Log "
            "(formato: - [AAAA-MM-DD HH:mm] {Tecnologia} {Dominio}: o que foi feito).",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
    sys.exit(0)
