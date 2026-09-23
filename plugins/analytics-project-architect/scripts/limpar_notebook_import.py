"""Deixa um .ipynb seguro para reimportar no Fabric (mecanismo M2).

Dois culpados recorrentes do erro 400 no import de notebook editado fora do Fabric
(programaticamente ou em VS Code): outputs salvos (sobretudo traceback com ANSI) e
`source` de celula gravado como string unica em vez de lista de linhas. Este script
normaliza so isso, sem tocar no resto -- nbformat/nbformat_minor e o bloco metadata do
Fabric (kernelspec, microsoft, spark_compute, dependencies.lakehouse/environment) passam
direto, mesmo que o script nao reconheca alguma chave. Equivalente manual no Fabric:
"Clear all outputs" (mas isso nao resolve `source` como string unica).

Idempotente: rodar de novo sobre um notebook ja limpo nao muda nada.

Uso:
    python limpar_notebook_import.py notebook.ipynb                       # edita in-place
    python limpar_notebook_import.py notebook.ipynb --saida limpo.ipynb   # grava em outro arquivo
"""
import argparse
import json
from pathlib import Path


def limpar_notebook_para_import(nb: dict) -> dict:
    """Aplica a limpeza em todas as celulas do dict do notebook (mutacao in-place)."""
    for celula in nb.get("cells", []):
        fonte = celula.get("source")
        if isinstance(fonte, str):
            # "source" como lista de linhas e o formato nativo que o Fabric espera de
            # volta; string unica e um dos dois motivos mais comuns do 400 no import.
            celula["source"] = fonte.splitlines(keepends=True)
        if celula.get("cell_type") == "code":
            # outputs salvos (principalmente erro com traceback ANSI, \x1b[...) sao o
            # outro motivo comum -- StatementMeta/resultado de execucao nao devem ir
            # para um notebook que ainda vai ser importado.
            celula["outputs"] = []
            celula["execution_count"] = None
    return nb


def limpar_arquivo(origem: Path, destino: Path) -> dict:
    with open(origem, encoding="utf-8") as f:
        nb = json.load(f)

    limpar_notebook_para_import(nb)

    destino.parent.mkdir(parents=True, exist_ok=True)
    # UTF-8 SEM BOM (nunca utf-8-sig) e newline="\n" fixo -- este e o formato "nativo" que
    # o Fabric espera de volta, entao a escrita e deterministica (nao preserva CRLF/estilo
    # do arquivo de entrada; isso e o que torna o script idempotente).
    with open(destino, "w", encoding="utf-8", newline="\n") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
        f.write("\n")

    return nb


def main():
    parser = argparse.ArgumentParser(
        description="Limpa um .ipynb para reimport seguro no Fabric (M2: source como lista, outputs zerados).",
    )
    parser.add_argument("notebook", help="Caminho do .ipynb a limpar")
    parser.add_argument("--saida", help="Caminho de saida (default: sobrescreve o proprio arquivo, in-place)")
    args = parser.parse_args()

    origem = Path(args.notebook)
    if not origem.exists():
        raise SystemExit(f"[limpar_notebook_import] arquivo nao encontrado: {origem}")

    destino = Path(args.saida) if args.saida else origem
    nb = limpar_arquivo(origem, destino)

    print(f"[limpar_notebook_import] OK: {destino} ({len(nb.get('cells', []))} celulas)")


if __name__ == "__main__":
    main()
