"""Hook PostToolUse (Edit|Write): lembra de atualizar a fonte de orquestracao quando um
notebook Silver/Gold muda. Cobre as duas nuvens:
- Fabric: metadata_driven/metadata_driven_orchestration.csv
- Databricks: databricks.yml / resources/*.yml (Asset Bundle)

Nunca bloqueia; so avisa em stderr.
"""
import json
import sys

PASTAS_GATILHO = ("silver", "gold")


def detectar_cloud(caminho_norm):
    # Heuristica leve: se o repo tem metadata_driven/ na arvore, e Fabric;
    # se tem databricks.yml na raiz de _tech-sync/, e Databricks. Sem acesso
    # ao filesystem aqui (hook deve ser rapido), so avisamos os dois caminhos
    # possiveis e deixamos quem le decidir qual se aplica ao projeto.
    return None


def main():
    try:
        evento = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    caminho = evento.get("tool_input", {}).get("file_path", "")
    caminho_norm = caminho.replace("\\", "/").lower()

    if caminho_norm.endswith(".ipynb") and any(f"/{p}/" in caminho_norm for p in PASTAS_GATILHO):
        print(
            f"[lembrete_orquestracao] {caminho} mudou (Silver/Gold). Confira:\n"
            "  - Fabric: metadata_driven/metadata_driven_orchestration.csv tem a linha certa?\n"
            "  - Databricks: databricks.yml/resources/*.yml referencia este notebook?\n"
            "  - PROJETO.md: log vivo atualizado com esta entrega?",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
    sys.exit(0)
