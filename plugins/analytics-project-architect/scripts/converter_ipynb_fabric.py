"""Converte um .ipynb para o formato nativo do Fabric (notebook-content.py + .platform).

Resolve a populacao em massa de um workspace Fabric a partir de notebooks .ipynb ja
existentes, pelo caminho Git integration (ver `08-cicd-fabric-databricks.md`). O Git
integration do Fabric so aceita `notebook-content.py` em percent-format como conteudo
principal de Notebook -- commitar um `notebook-content.ipynb` e mandar "Update from Git"
falha direto no backend (`System.ArgumentException: ... is not supported`). Rodar essa
conversao em disco via Bash/Python tambem evita o teto de ~25-27 mil caracteres por
chamada que trava tentar gerar o payload base64 inline numa chamada de tool (mecanismo M4
em `07-mecanismos-e-hooks.md`).

Formato validado por diff byte a byte (ignorando so CRLF/LF) contra exemplos reais
gerados pelo proprio Fabric num Commit. Cobertura confirmada: celulas markdown/code
Python puro, sem outputs salvos (notebook ja "import-safe", ver mecanismo M2). Fora
disso, ver as ressalvas abaixo -- nao tratar como cobertura completa:

- Celulas `raw` sao logadas como aviso e ignoradas (nbformat permite; nao apareceram nos
  notebooks de origem testados).
- Nao emite bloco `# METADATA` por celula (so o do topo, a nivel de notebook). Em 4
  exemplos reais, 3 nao tinham metadata por celula e 1 tinha (com `language` explicito),
  sem causa identificada para a diferenca. Se o projeto tiver celulas de linguagem
  nao-Python misturadas (`%%sql` etc.) dentro do mesmo notebook, teste o import antes de
  confiar cegamente.
- Se o `.ipynb` de origem nao tiver `metadata.dependencies.lakehouse` populado (notebook
  nunca importado no Fabric antes), o `.py` gerado sai com `"lakehouse": {}` vazio -- o
  Fabric aceita o import, mas o notebook nao vem com lakehouse padrao anexado.
- Escreve com `\n` puro (LF), casando com a convencao "nativa" do resto da skill
  (`limpar_notebook_import.py`). Isso so bateu 100% com o output real do Fabric porque o
  git do ambiente testado tinha `core.autocrlf` convertendo para CRLF no commit. Se seu
  ambiente nao fizer essa conversao automatica, valide com um diff contra um notebook
  real ja commitado pelo Fabric antes de confiar no byte a byte.

Uso:
    python converter_ipynb_fabric.py notebook.ipynb pasta_saida
    python converter_ipynb_fabric.py notebook.ipynb pasta_saida --nome NB_SILVER_DOADORES

Gera `pasta_saida/<nome>.Notebook/notebook-content.py` + `.platform`.
"""
import argparse
import json
import uuid
from pathlib import Path


def _linhas_da_celula(celula: dict) -> list[str]:
    fonte = celula.get("source", [])
    texto = "".join(fonte) if isinstance(fonte, list) else fonte
    linhas = texto.split("\n")
    # "".join(source).split("\n") deixa um "" residual no fim quando o texto original
    # termina em quebra de linha (comum em source de nbformat) -- descarta so esse.
    if linhas and linhas[-1] == "":
        linhas = linhas[:-1]
    return linhas


def converter_notebook(nb: dict) -> str:
    """Gera o conteudo de notebook-content.py a partir do dict do .ipynb carregado."""
    lakehouse = nb.get("metadata", {}).get("dependencies", {}).get("lakehouse", {})

    linhas = ["# Fabric notebook source", "", "# METADATA ********************", ""]

    meta_obj = {
        "kernel_info": {"name": "synapse_pyspark"},
        "dependencies": {"lakehouse": lakehouse, "environment": {}},
    }
    for linha in json.dumps(meta_obj, indent=2).split("\n"):
        linhas.append(f"# META {linha}" if linha else "# META")

    for celula in nb["cells"]:
        linhas.append("")
        tipo = celula.get("cell_type")
        src_linhas = _linhas_da_celula(celula)

        if tipo == "markdown":
            linhas.append("# MARKDOWN ********************")
            linhas.append("")
            linhas.extend(f"# {sl}" for sl in src_linhas)
        elif tipo == "code":
            tags = celula.get("metadata", {}).get("tags", [])
            marcador = (
                "# PARAMETERS CELL ********************"
                if "parameters" in tags
                else "# CELL ********************"
            )
            linhas.append(marcador)
            linhas.append("")
            linhas.extend(src_linhas)
        else:
            print(f"[converter_ipynb_fabric] aviso: celula tipo '{tipo}' ignorada (sem equivalente no formato nativo)")
            linhas.pop()  # desfaz a linha em branco desta celula, que nao gerou conteudo

    return "\n".join(linhas) + "\n"


def converter_arquivo(origem: Path, pasta_saida: Path, nome: str) -> dict:
    with open(origem, encoding="utf-8") as f:
        nb = json.load(f)

    conteudo = converter_notebook(nb)

    pasta_item = pasta_saida / f"{nome}.Notebook"
    pasta_item.mkdir(parents=True, exist_ok=True)

    with open(pasta_item / "notebook-content.py", "w", encoding="utf-8", newline="\n") as f:
        f.write(conteudo)

    platform_obj = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Notebook", "displayName": nome},
        "config": {"version": "2.0", "logicalId": str(uuid.uuid4())},
    }
    with open(pasta_item / ".platform", "w", encoding="utf-8", newline="\n") as f:
        json.dump(platform_obj, f, indent=2)
        f.write("\n")

    return nb


def main():
    parser = argparse.ArgumentParser(
        description="Converte um .ipynb para notebook-content.py + .platform (formato nativo do Fabric, para Git integration).",
    )
    parser.add_argument("notebook", help="Caminho do .ipynb de origem")
    parser.add_argument("pasta_saida", help="Pasta onde criar <nome>.Notebook/")
    parser.add_argument("--nome", help="displayName do item no Fabric (default: nome do arquivo sem .ipynb)")
    args = parser.parse_args()

    origem = Path(args.notebook)
    if not origem.exists():
        raise SystemExit(f"[converter_ipynb_fabric] arquivo nao encontrado: {origem}")

    nome = args.nome or origem.stem
    nb = converter_arquivo(origem, Path(args.pasta_saida), nome)

    print(f"[converter_ipynb_fabric] OK: {Path(args.pasta_saida) / (nome + '.Notebook')} ({len(nb.get('cells', []))} celulas)")


if __name__ == "__main__":
    main()
