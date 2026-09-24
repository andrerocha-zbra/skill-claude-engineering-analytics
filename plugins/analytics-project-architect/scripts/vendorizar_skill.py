"""Vendoriza um snapshot desta skill para dentro de um projeto, em
`.claude/skills/analytics-project-architect/`.

Resolve a diferenca entre "skill instalada como plugin" (o que este repositorio e hoje) e
"skill versionada no repositorio do cliente" (o modelo de todas as geracoes anteriores do
metodo). Sem isso, o repositorio de um cliente so funciona enquanto o plugin continuar
instalado na maquina de quem trabalha nele -- clonar o repo em outra maquina, ou dali a um
ano, perde acesso a SKILL.md/references/templates/scripts inteiros.

Rode a partir da copia do plugin INSTALADA (nunca a partir da copia ja vendorizada dentro
de um projeto -- essa copia serve so para o Claude Code carregar a skill naquele projeto,
nao para vendorizar de novo a partir dela).

Nunca sobrescreve por padrao (mesmo idioma idempotente de escrever_se_nao_existir() em
scaffold_cliente.py). `--forcar` e o modo usado por atualizar_skill_vendorizada.py para
resync deliberado.

Uso:
    python vendorizar_skill.py --projeto C:/repos/NomeCliente
    python vendorizar_skill.py --projeto C:/repos/NomeCliente --forcar
"""
import argparse
import json
import shutil
from pathlib import Path

NOME_SKILL = "analytics-project-architect"
SUBPASTAS_VENDORIZADAS = ("references", "templates", "scripts")


def raiz_plugin() -> Path:
    """A raiz deste plugin (um nivel acima de scripts/), de onde tudo e copiado."""
    return Path(__file__).resolve().parent.parent


def ler_versao_plugin(raiz: Path) -> str:
    manifesto = raiz / ".claude-plugin" / "plugin.json"
    if not manifesto.is_file():
        return "desconhecida"
    try:
        return json.loads(manifesto.read_text(encoding="utf-8")).get("version", "desconhecida")
    except (OSError, json.JSONDecodeError):
        return "desconhecida"


def _copiar_arquivo(origem: Path, destino: Path, forcar: bool) -> str:
    existia = destino.exists()
    if existia and not forcar:
        return "mantido"
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, destino)
    return "atualizado" if existia else "copiado"


def _copiar_pasta(origem: Path, destino: Path, forcar: bool, resumo: dict) -> None:
    if not origem.is_dir():
        return
    for caminho in sorted(origem.rglob("*")):
        if caminho.is_dir():
            continue
        relativo = caminho.relative_to(origem)
        alvo = destino / relativo
        status = _copiar_arquivo(caminho, alvo, forcar)
        resumo.setdefault(status, []).append(str(alvo))


def vendorizar(destino_projeto: Path, forcar: bool = False) -> dict:
    """Copia SKILL.md + references/ + templates/ + scripts/ do plugin instalado para
    <destino_projeto>/.claude/skills/analytics-project-architect/, e grava a versao
    vendorizada em VERSION. Retorna um resumo {status: [caminhos]} para quem chamou
    reportar (scaffold_cliente.py na criacao, atualizar_skill_vendorizada.py no resync)."""
    raiz = raiz_plugin()
    destino_skill = destino_projeto / ".claude" / "skills" / NOME_SKILL
    resumo: dict = {}

    status = _copiar_arquivo(raiz / "SKILL.md", destino_skill / "SKILL.md", forcar)
    resumo.setdefault(status, []).append(str(destino_skill / "SKILL.md"))

    for sub in SUBPASTAS_VENDORIZADAS:
        _copiar_pasta(raiz / sub, destino_skill / sub, forcar, resumo)

    versao = ler_versao_plugin(raiz)
    arquivo_versao = destino_skill / "VERSION"
    arquivo_versao.parent.mkdir(parents=True, exist_ok=True)
    with open(arquivo_versao, "w", encoding="utf-8", newline="\n") as f:
        f.write(versao + "\n")
    resumo.setdefault("versao", []).append(f"{arquivo_versao} -> {versao}")

    return resumo


def main():
    parser = argparse.ArgumentParser(
        description="Vendoriza esta skill (SKILL.md/references/templates/scripts) para "
        "<projeto>/.claude/skills/analytics-project-architect/.",
    )
    parser.add_argument("--projeto", required=True, help="Pasta raiz do projeto de destino")
    parser.add_argument("--forcar", action="store_true", help="Sobrescreve arquivos ja vendorizados (resync)")
    args = parser.parse_args()

    destino = Path(args.projeto)
    if not destino.is_dir():
        raise SystemExit(f"[vendorizar_skill] pasta nao encontrada: {destino}")

    resumo = vendorizar(destino, forcar=args.forcar)

    for status in ("copiado", "atualizado", "mantido", "versao"):
        for caminho in resumo.get(status, []):
            simbolo = {"copiado": "+", "atualizado": "~", "mantido": "=", "versao": "*"}[status]
            print(f"  {simbolo} {caminho}")

    total_novos = len(resumo.get("copiado", [])) + len(resumo.get("atualizado", []))
    print(f"[vendorizar_skill] OK: {total_novos} arquivo(s) escrito(s) em "
          f"{destino / '.claude' / 'skills' / NOME_SKILL}")


if __name__ == "__main__":
    main()
