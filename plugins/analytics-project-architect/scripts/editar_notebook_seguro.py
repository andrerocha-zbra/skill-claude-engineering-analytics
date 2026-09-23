"""Modulo utilitario para editar um .ipynb preservando o formato exato do arquivo.

Generaliza a logica usada nos scripts de sessao patch_rate_limit.py / patch_raw_off.py
(Projeto de Engenharia 1): notebooks exportados por ferramentas diferentes divergem em
detalhes triviais que nao tem nada a ver com o conteudo (source de celula como lista de
linhas vs. string unica, CRLF vs LF, \\uXXXX vs caractere literal, quebra de linha final ou
nao). Um patch que ignora isso faz o arquivo inteiro "mudar" no diff so porque o
serializador escolheu outro estilo -- ou, pior, corrompe o reimport na ferramenta de
origem (ver mecanismo M2 em limpar_notebook_import.py). As funcoes aqui detectam o
formato na leitura e o repoem byte a byte na escrita, editando so o que foi pedido.

Nao e uma CLI de uso direto: importe as funcoes de outro script. Rodar este arquivo
diretamente (`python editar_notebook_seguro.py`) executa um teste manual de demonstracao.
"""
import json
import re
import uuid
from pathlib import Path

ASTRAL_RE = re.compile(r"[\U00010000-\U0010FFFF]")


def _escapar_par_substituto(m):
    # Estilo visto em alguns exports (ex.: Databricks): caractere fora do BMP (emoji) e
    # gravado como par substituto "\\uD8xx\\uDCxx" maiusculo, nao como o caractere literal.
    cp = ord(m.group(0)) - 0x10000
    return "\\u%04X\\u%04X" % (0xD800 + (cp >> 10), 0xDC00 + (cp & 0x3FF))


def detectar_formato_arquivo(raw: bytes) -> dict:
    """Detecta o formato de serializacao do ARQUIVO inteiro (nivel byte).

    Le a partir dos bytes originais (nao do dict ja parseado) porque e so no texto cru
    que da pra saber se o exportador usou CRLF, se escapou unicode como \\uXXXX, se
    emoji virou par substituto e se o arquivo termina com quebra de linha.
    """
    texto = raw.decode("utf-8")
    return {
        "crlf": "\r\n" in texto,
        "ensure_ascii": "\\u00" in texto or "\\u01" in texto,
        "astral_escape": bool(re.search(r"\\uD8[0-9A-F]{2}", texto)),
        "newline_final": texto.endswith("\n"),
    }


def serializar_arquivo(nb: dict, formato_arquivo: dict) -> bytes:
    """Serializa `nb` de volta para bytes, reproduzindo exatamente o formato detectado."""
    texto = json.dumps(nb, indent=1, ensure_ascii=formato_arquivo["ensure_ascii"])
    if formato_arquivo["astral_escape"] and not formato_arquivo["ensure_ascii"]:
        texto = ASTRAL_RE.sub(_escapar_par_substituto, texto)
    if formato_arquivo["newline_final"]:
        texto += "\n"
    if formato_arquivo["crlf"]:
        texto = texto.replace("\n", "\r\n")
    return texto.encode("utf-8")


def carregar_notebook(path) -> tuple:
    """Le um .ipynb do disco. Retorna (notebook_dict, formato_arquivo)."""
    raw = Path(path).read_bytes()
    formato_arquivo = detectar_formato_arquivo(raw)
    nb = json.loads(raw.decode("utf-8"))
    return nb, formato_arquivo


def gravar_notebook(path, nb: dict, formato_arquivo: dict) -> None:
    """Grava `nb` no disco preservando o formato detectado por carregar_notebook."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(serializar_arquivo(nb, formato_arquivo))


def detectar_formato(celula: dict) -> dict:
    """Detecta o formato de UMA CELULA: `source` como lista de linhas ou string unica."""
    return {"lista": isinstance(celula.get("source"), list)}


def texto_da_celula(celula: dict) -> str:
    """Concatena `source` (lista ou string) num texto unico, para leitura/regex/patch."""
    fonte = celula.get("source", "")
    return "".join(fonte) if isinstance(fonte, list) else fonte


def serializar(celula: dict, linhas, formato: dict) -> None:
    """Grava `linhas` de volta em `celula['source']`, no formato dado por detectar_formato.

    `linhas` aceita lista de linhas ou string unica -- o formato de SAIDA sempre segue
    `formato['lista']` (o formato original da celula), nao o tipo do argumento `linhas`.
    """
    texto = "".join(linhas) if isinstance(linhas, list) else linhas
    celula["source"] = texto.splitlines(keepends=True) if formato["lista"] else texto


def substituir_bloco(nb_path, indice_celula: int, texto_antigo: str, texto_novo: str, *, ocorrencias: int = 1) -> None:
    """Patch cirurgico: troca `texto_antigo` por `texto_novo` dentro de UMA celula (por
    indice), preservando o formato do arquivo inteiro e o formato daquela celula.

    Este e o caso de uso real que motivou o modulo: corrigir um notebook de producao sem
    reescrever o arquivo inteiro e sem gerar um diff gigante por causa de reformatacao.

    `ocorrencias` limita quantas substituicoes fazer dentro do texto da celula (default 1,
    so a primeira ocorrencia) -- mesma semantica de `str.replace(old, new, count)`.
    Levanta ValueError se `indice_celula` estiver fora do range ou se `texto_antigo` nao
    for encontrado (falha visivel, nunca um patch parcial silencioso).
    """
    path = Path(nb_path)
    nb, formato_arquivo = carregar_notebook(path)
    celulas = nb.get("cells", [])
    if not (0 <= indice_celula < len(celulas)):
        raise ValueError(f"indice_celula {indice_celula} fora do range (0..{len(celulas) - 1})")

    celula = celulas[indice_celula]
    formato_celula = detectar_formato(celula)
    texto = texto_da_celula(celula)
    if texto_antigo not in texto:
        raise ValueError(f"texto ancora nao encontrado na celula {indice_celula}: {texto_antigo!r}")

    novo_texto = texto.replace(texto_antigo, texto_novo, ocorrencias)
    serializar(celula, novo_texto, formato_celula)
    gravar_notebook(path, nb, formato_arquivo)


if __name__ == "__main__":
    # Teste manual: cria um notebook temporario com CRLF + source como lista de linhas,
    # aplica substituir_bloco numa celula e confere que so ela mudou -- o resto do
    # arquivo (indentacao, CRLF, quebra final, a outra celula) fica byte a byte igual.
    import tempfile

    nb_teste = {
        "cells": [
            {"cell_type": "markdown", "id": str(uuid.uuid4()), "metadata": {}, "source": ["# Teste\n"]},
            {
                "cell_type": "code",
                "id": str(uuid.uuid4()),
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": ["x = 1\n", "print(x)"],
            },
        ],
        "metadata": {"kernelspec": {"name": "python3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    texto_original = json.dumps(nb_teste, indent=1, ensure_ascii=False)
    texto_original = texto_original.replace("\n", "\r\n")  # simula export com CRLF

    with tempfile.TemporaryDirectory() as tmp:
        caminho = Path(tmp) / "teste.ipynb"
        caminho.write_bytes(texto_original.encode("utf-8"))
        bytes_antes = caminho.read_bytes()

        substituir_bloco(caminho, indice_celula=1, texto_antigo="x = 1", texto_novo="x = 2")

        nb_depois, formato_depois = carregar_notebook(caminho)
        print("source da celula 1 apos o patch:", nb_depois["cells"][1]["source"])
        print("continua lista de linhas?", isinstance(nb_depois["cells"][1]["source"], list))
        print("continua CRLF?", formato_depois["crlf"])
        print("celula 0 (markdown) intocada:", nb_depois["cells"][0]["source"])

        # roundtrip: reserializar sem nenhuma edicao deve reproduzir o arquivo exatamente
        nb_check, fmt_check = carregar_notebook(caminho)
        print("roundtrip identico (sem edicao)?", serializar_arquivo(nb_check, fmt_check) == caminho.read_bytes())
        print("arquivo original tinha", len(bytes_antes), "bytes")
