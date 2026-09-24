"""Detecta o executavel local do MCP `powerbi-modeling-mcp` e grava o caminho na variavel
de ambiente que o `.mcp.json` deste plugin espera (`POWERBI_MODELING_MCP_PATH`).

Esse MCP roda como um processo local (stdio) que vem da extensao do VS Code
`analysis-services.powerbi-modeling-mcp`, instalada em
`~/.vscode/extensions/analysis-services.powerbi-modeling-mcp-<versao>-<plataforma>/server/`.
O caminho inclui a versao da extensao e e especifico da maquina/usuario -- nunca pode ser
commitado literal num `.mcp.json` compartilhado (ver `.mcp.json` deste plugin, que referencia
`${POWERBI_MODELING_MCP_PATH}` em vez do caminho absoluto). Este script roda uma vez por
maquina para resolver isso.

O MCP `fabric` (HTTP + OAuth) nao precisa de nenhum setup local -- autentica sozinho no
primeiro uso.

Idempotente: rodar de novo so atualiza o valor se o caminho detectado mudar (ex.: apos
atualizar a extensao); nunca mexe em outras chaves do `env` ja existentes.

Uso:
    python detectar_powerbi_modeling_mcp.py --projeto C:/repos/NomeCliente
    python detectar_powerbi_modeling_mcp.py --global
"""
import argparse
import json
from pathlib import Path

NOME_EXTENSAO = "analysis-services.powerbi-modeling-mcp"
NOME_EXECUTAVEL_CANDIDATOS = ("powerbi-modeling-mcp.exe", "powerbi-modeling-mcp")
VARIAVEL_ENV = "POWERBI_MODELING_MCP_PATH"


def _versao_da_pasta(pasta: Path) -> tuple:
    """Extrai a versao do nome da pasta (ex. '...-0.4.0-win32-x64' -> (0, 4, 0)) para
    comparar instalacoes quando houver mais de uma. Nao-numerico cai para (0,), sempre a
    mais antiga na ordenacao."""
    resto = pasta.name[len(NOME_EXTENSAO) + 1:]  # remove "analysis-services.powerbi-modeling-mcp-"
    partes = resto.split("-")[0].split(".")
    try:
        return tuple(int(p) for p in partes)
    except ValueError:
        return (0,)


def localizar_executavel(pasta_extensoes: Path):
    candidatas = sorted(
        (p for p in pasta_extensoes.glob(f"{NOME_EXTENSAO}-*") if p.is_dir()),
        key=_versao_da_pasta,
    )
    for pasta in reversed(candidatas):  # mais recente primeiro
        for nome_exe in NOME_EXECUTAVEL_CANDIDATOS:
            exe = pasta / "server" / nome_exe
            if exe.is_file():
                return exe
    return None


def gravar_variavel(arquivo_settings: Path, caminho_exe: Path) -> None:
    dados = {}
    if arquivo_settings.is_file():
        try:
            dados = json.loads(arquivo_settings.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raise SystemExit(f"[detectar_powerbi_modeling_mcp] {arquivo_settings} tem JSON invalido -- corrija a mao antes de rodar de novo")

    env = dados.setdefault("env", {})
    valor_novo = str(caminho_exe)
    valor_atual = env.get(VARIAVEL_ENV)

    if valor_atual == valor_novo:
        print(f"  = {VARIAVEL_ENV} ja aponta para {valor_novo} em {arquivo_settings}")
        return

    if valor_atual:
        print(f"  ~ {VARIAVEL_ENV}: {valor_atual} -> {valor_novo} (em {arquivo_settings})")
    else:
        print(f"  + {VARIAVEL_ENV} = {valor_novo} (em {arquivo_settings})")

    env[VARIAVEL_ENV] = valor_novo
    arquivo_settings.parent.mkdir(parents=True, exist_ok=True)
    with open(arquivo_settings, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Detecta o powerbi-modeling-mcp.exe instalado via extensao do VS Code "
        "e grava POWERBI_MODELING_MCP_PATH em .claude/settings.local.json.",
    )
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--projeto", default=".", help="Projeto de destino (default: pasta atual)")
    grupo.add_argument("--global", dest="global_", action="store_true", help="Grava em ~/.claude/settings.json (todos os projetos) em vez de um projeto especifico")
    args = parser.parse_args()

    exe = localizar_executavel(Path.home() / ".vscode" / "extensions")
    if not exe:
        raise SystemExit(
            f"[detectar_powerbi_modeling_mcp] extensao '{NOME_EXTENSAO}' nao encontrada em "
            f"{Path.home() / '.vscode' / 'extensions'}. Instale a extensao 'PowerBI Modeling MCP' "
            "no VS Code e rode este script de novo."
        )

    print(f"  detectado: {exe}")

    if args.global_:
        arquivo_settings = Path.home() / ".claude" / "settings.json"
    else:
        arquivo_settings = Path(args.projeto) / ".claude" / "settings.local.json"

    gravar_variavel(arquivo_settings, exe)


if __name__ == "__main__":
    main()
