"""Resincroniza a skill vendorizada de um projeto (`.claude/skills/analytics-project-architect/`)
com a versao atual do plugin instalado.

Devolve o beneficio de "corrigir uma vez, propagar para N clientes" sem sacrificar a
reprodutibilidade que a vendorizacao (`vendorizar_skill.py`) trouxe: a propagacao passa a
ser deliberada e visivel num diff, nunca invisivel via plugin instalado.

Rode a partir da copia do plugin INSTALADA (nunca a partir da copia vendorizada dentro do
projeto). Sempre mostra o diff primeiro; so escreve algo com `--confirmar`. Nunca toca em
`PROJETO.md`, `CLAUDE.md`, `prompts/` ou qualquer outro arquivo do projeto fora de
`.claude/skills/analytics-project-architect/`.

Uso:
    python atualizar_skill_vendorizada.py --projeto C:/repos/NomeCliente
    python atualizar_skill_vendorizada.py --projeto C:/repos/NomeCliente --confirmar
"""
import argparse
import filecmp
from pathlib import Path

import vendorizar_skill

NOME_SKILL = vendorizar_skill.NOME_SKILL


def _arquivos_fonte(raiz_plugin: Path) -> dict:
    """Mapa {caminho_relativo: Path} de tudo que vendorizar_skill.vendorizar() copiaria."""
    fonte = {"SKILL.md": raiz_plugin / "SKILL.md"}
    for sub in vendorizar_skill.SUBPASTAS_VENDORIZADAS:
        pasta = raiz_plugin / sub
        if not pasta.is_dir():
            continue
        for caminho in pasta.rglob("*"):
            if caminho.is_file():
                fonte[str(caminho.relative_to(raiz_plugin))] = caminho
    return fonte


def _arquivos_vendorizados(destino_skill: Path) -> dict:
    if not destino_skill.is_dir():
        return {}
    vendorizados = {}
    for caminho in destino_skill.rglob("*"):
        if caminho.is_file() and caminho.name != "VERSION":
            vendorizados[str(caminho.relative_to(destino_skill))] = caminho
    return vendorizados


def comparar(raiz_plugin: Path, destino_skill: Path) -> dict:
    fonte = _arquivos_fonte(raiz_plugin)
    vendorizados = _arquivos_vendorizados(destino_skill)

    adicionados = sorted(fonte.keys() - vendorizados.keys())
    removidos = sorted(vendorizados.keys() - fonte.keys())
    comuns = fonte.keys() & vendorizados.keys()
    alterados = sorted(
        rel for rel in comuns
        if not filecmp.cmp(fonte[rel], vendorizados[rel], shallow=False)
    )

    return {
        "adicionados": adicionados,
        "alterados": alterados,
        "removidos": removidos,
        "fonte": fonte,
        "vendorizados": vendorizados,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Compara a skill vendorizada de um projeto com o plugin instalado e, "
        "com --confirmar, resincroniza.",
    )
    parser.add_argument("--projeto", required=True, help="Pasta raiz do projeto de destino")
    parser.add_argument("--confirmar", action="store_true", help="Aplica o resync (sem isto, so mostra o diff)")
    args = parser.parse_args()

    destino_projeto = Path(args.projeto)
    if not destino_projeto.is_dir():
        raise SystemExit(f"[atualizar_skill_vendorizada] pasta nao encontrada: {destino_projeto}")

    raiz_plugin = vendorizar_skill.raiz_plugin()
    destino_skill = destino_projeto / ".claude" / "skills" / NOME_SKILL

    diff = comparar(raiz_plugin, destino_skill)
    versao_plugin = vendorizar_skill.ler_versao_plugin(raiz_plugin)
    versao_vendorizada = (destino_skill / "VERSION").read_text(encoding="utf-8").strip() if (destino_skill / "VERSION").is_file() else "nunca vendorizada"

    print(f"Skill vendorizada em {destino_skill}: {versao_vendorizada}  |  plugin instalado: {versao_plugin}\n")
    for rotulo, chave, simbolo in (("Novos", "adicionados", "+"), ("Alterados", "alterados", "~"), ("Removidos do plugin (obsoletos no projeto)", "removidos", "-")):
        itens = diff[chave]
        print(f"{rotulo} ({len(itens)}):")
        for rel in itens:
            print(f"  {simbolo} {rel}")
        if not itens:
            print("  (nenhum)")

    if not (diff["adicionados"] or diff["alterados"] or diff["removidos"]):
        print("\n[atualizar_skill_vendorizada] Nada a fazer -- skill vendorizada ja bate com o plugin.")
        return

    if not args.confirmar:
        print("\n[atualizar_skill_vendorizada] Modo somente leitura -- rode de novo com --confirmar para aplicar.")
        return

    vendorizar_skill.vendorizar(destino_projeto, forcar=True)
    for rel in diff["removidos"]:
        (destino_skill / rel).unlink()
        print(f"  - removido: {destino_skill / rel}")

    print(f"\n[atualizar_skill_vendorizada] OK: skill vendorizada atualizada para a versao {versao_plugin}.")


if __name__ == "__main__":
    main()
