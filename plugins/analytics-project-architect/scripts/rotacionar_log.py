"""Arquiva as entradas antigas da secao "## Log" de um PROJETO.md, por trimestre civil.

PROJETO.md cresce para sempre (regra do metodo: atualizar o log a cada trabalho
relevante). Sem rotacao, a secao "## Log" acaba dominando o arquivo e a leitura seletiva
de inicializacao (ver AGENTS.md gerado por scaffold_cliente.py, que so le "as ~10 entradas
mais recentes") fica cada vez mais cara. Este script move as entradas antigas para
PROJETO.md.historico/AAAA-QN.md (uma por trimestre civil, agrupadas pela data de cada
entrada) e deixa so as recentes no PROJETO.md, com uma linha apontando para onde o resto
foi parar.

Formato de entrada aceito (uma entrada por linha, dentro de "## Log"):
    - [AAAA-MM-DD HH:mm] {Tecnologia} {Dominio}: texto...
    - [AAAA-MM-DD] {Tecnologia} {Dominio}: texto...

Nao-destrutivo por padrao: grava PROJETO.md.bak antes de reescrever o original (a menos
que --sem-backup seja passado).

Uso:
    python rotacionar_log.py PROJETO.md                        # mantem as 10 mais recentes
    python rotacionar_log.py PROJETO.md --manter-recentes 20
    python rotacionar_log.py PROJETO.md --trimestre 2026-Q1    # arquiva tudo antes deste trimestre
"""
import argparse
import re
import shutil
from datetime import date
from pathlib import Path

CABECALHO_LOG = "## Log"
PADRAO_DATA_ENTRADA = re.compile(r"^-\s*\[(\d{4})-(\d{2})-(\d{2})(?:[ T]\d{2}:\d{2})?\]")


def trimestre_da_data(ano: int, mes: int) -> str:
    q = (mes - 1) // 3 + 1
    return f"{ano}-Q{q}"


def trimestre_para_chave(trimestre: str):
    """Converte 'AAAA-QN' numa chave comparavel (ano, trimestre) para ordenar/comparar."""
    m = re.match(r"^(\d{4})-Q([1-4])$", trimestre)
    if not m:
        raise ValueError(f"--trimestre invalido: {trimestre!r} (formato esperado AAAA-QN, ex.: 2026-Q1)")
    return int(m.group(1)), int(m.group(2))


def localizar_secao_log(linhas: list):
    """Acha o range [inicio, fim) da secao '## Log' dentro das linhas do PROJETO.md.
    `inicio` e o indice da linha do cabecalho; `fim` e o indice da proxima secao de
    mesmo nivel (`## `) ou o fim do arquivo. Levanta ValueError se a secao nao existir."""
    inicio = None
    for i, linha in enumerate(linhas):
        if linha.strip() == CABECALHO_LOG:
            inicio = i
            break
    if inicio is None:
        raise ValueError(f'secao "{CABECALHO_LOG}" nao encontrada no arquivo')

    fim = len(linhas)
    for i in range(inicio + 1, len(linhas)):
        if linhas[i].startswith("## "):
            fim = i
            break
    return inicio, fim


def extrair_entradas(linhas_secao: list) -> list:
    """Separa a secao de Log em entradas. Cada entrada comeca numa linha '- [data...]' e
    inclui as linhas de continuacao (sem esse padrao) ate a proxima entrada. Linhas soltas
    antes da primeira entrada (o cabecalho, avisos de arquivamento anteriores, linhas em
    branco) sao mantidas de fora e devolvidas junto, para nao se perderem."""
    entradas = []
    preambulo = []
    atual = None

    for linha in linhas_secao:
        m = PADRAO_DATA_ENTRADA.match(linha)
        if m:
            if atual is not None:
                entradas.append(atual)
            ano, mes, dia = int(m.group(1)), int(m.group(2)), int(m.group(3))
            atual = {"data": date(ano, mes, dia), "linhas": [linha]}
        elif atual is not None:
            atual["linhas"].append(linha)
        else:
            preambulo.append(linha)

    if atual is not None:
        entradas.append(atual)

    return preambulo, entradas


def selecionar_antigas(entradas: list, manter_recentes: int, trimestre_corte: str):
    """Decide quais entradas vao para o arquivo historico. Duas estrategias mutuamente
    exclusivas: por contagem (todas exceto as N mais recentes) ou por corte de trimestre
    (todas as entradas de trimestre estritamente anterior ao informado)."""
    if trimestre_corte:
        chave_corte = trimestre_para_chave(trimestre_corte)
        antigas, recentes = [], []
        for e in entradas:
            chave_entrada = (e["data"].year, (e["data"].month - 1) // 3 + 1)
            (antigas if chave_entrada < chave_corte else recentes).append(e)
        return antigas, recentes

    # Por contagem: entradas array esta na ordem em que aparecem no arquivo (mais antiga
    # primeiro, convencao observada no PROJETO.md real); as N ULTIMAS sao as mais recentes.
    if manter_recentes <= 0:
        return list(entradas), []
    if len(entradas) <= manter_recentes:
        return [], list(entradas)
    corte = len(entradas) - manter_recentes
    return entradas[:corte], entradas[corte:]


def agrupar_por_trimestre(entradas: list) -> dict:
    grupos = {}
    for e in entradas:
        trimestre = trimestre_da_data(e["data"].year, e["data"].month)
        grupos.setdefault(trimestre, []).append(e)
    return grupos


def gravar_arquivo_historico(pasta_historico: Path, trimestre: str, entradas: list) -> Path:
    caminho = pasta_historico / f"{trimestre}.md"
    pasta_historico.mkdir(parents=True, exist_ok=True)

    linhas_novas = []
    for e in entradas:
        linhas_novas.extend(e["linhas"])

    if caminho.exists():
        # Arquivo do trimestre ja existe (rotacoes anteriores tambem cairam nele) --
        # acrescenta ao final em vez de sobrescrever, sem duplicar cabecalho.
        with open(caminho, "a", encoding="utf-8", newline="\n") as f:
            f.writelines(linhas_novas)
    else:
        with open(caminho, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"# Log arquivado -- {trimestre}\n\n")
            f.writelines(linhas_novas)

    return caminho


def main():
    parser = argparse.ArgumentParser(description='Arquiva entradas antigas da secao "## Log" de um PROJETO.md, por trimestre.')
    parser.add_argument("projeto_md", help="Caminho do PROJETO.md")
    parser.add_argument("--manter-recentes", type=int, default=10, help="Quantas entradas recentes manter no PROJETO.md (default: 10)")
    parser.add_argument("--trimestre", help="Arquiva tudo ANTES deste trimestre (formato AAAA-QN, ex.: 2026-Q1); sobrepoe --manter-recentes")
    parser.add_argument("--sem-backup", action="store_true", help="Nao grava PROJETO.md.bak antes de reescrever")
    args = parser.parse_args()

    caminho_projeto = Path(args.projeto_md)
    if not caminho_projeto.exists():
        raise SystemExit(f"[rotacionar_log] arquivo nao encontrado: {caminho_projeto}")

    texto_original = caminho_projeto.read_text(encoding="utf-8")
    linhas = texto_original.splitlines(keepends=True)

    inicio, fim = localizar_secao_log(linhas)
    preambulo, entradas = extrair_entradas(linhas[inicio + 1: fim])

    if not entradas:
        print("[rotacionar_log] nenhuma entrada de log encontrada -- nada para arquivar.")
        return

    antigas, recentes = selecionar_antigas(entradas, args.manter_recentes, args.trimestre)
    if not antigas:
        print(f"[rotacionar_log] nada para arquivar ({len(entradas)} entrada(s), todas dentro do criterio de retencao).")
        return

    pasta_historico = caminho_projeto.parent / f"{caminho_projeto.name}.historico"
    grupos = agrupar_por_trimestre(antigas)
    arquivos_gerados = []
    for trimestre in sorted(grupos):
        caminho_gerado = gravar_arquivo_historico(pasta_historico, trimestre, grupos[trimestre])
        arquivos_gerados.append((trimestre, caminho_gerado, len(grupos[trimestre])))

    ultimo_trimestre = sorted(grupos)[-1]
    data_corte = max(e["data"] for e in antigas)
    aviso = (
        f"> Entradas anteriores a {data_corte.isoformat()} arquivadas em "
        f"{pasta_historico.name}/{ultimo_trimestre}.md\n\n"
    )

    linhas_recentes = []
    for e in recentes:
        linhas_recentes.extend(e["linhas"])

    # preambulo ja inclui a linha em branco/comentario originais logo apos o cabecalho
    # (ver extrair_entradas); nao acrescentar mais uma quebra aqui, senao dobra o espaco.
    novo_conteudo_secao = [CABECALHO_LOG + "\n"] + preambulo + [aviso] + linhas_recentes
    novas_linhas = linhas[:inicio] + novo_conteudo_secao + linhas[fim:]
    texto_novo = "".join(novas_linhas)

    if not args.sem_backup:
        caminho_bak = caminho_projeto.with_name(caminho_projeto.name + ".bak")
        shutil.copy2(caminho_projeto, caminho_bak)
        print(f"[rotacionar_log] backup gravado: {caminho_bak}")

    caminho_projeto.write_text(texto_novo, encoding="utf-8", newline="\n")

    print(f"[rotacionar_log] {len(antigas)} entrada(s) arquivada(s), {len(recentes)} mantida(s) em {caminho_projeto}:")
    for trimestre, caminho_gerado, qtd in arquivos_gerados:
        print(f"  - {trimestre}: {qtd} entrada(s) -> {caminho_gerado}")


if __name__ == "__main__":
    main()
