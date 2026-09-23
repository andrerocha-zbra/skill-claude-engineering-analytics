"""Cria a pasta de uma reuniao nova (materiais/, specs/, ata.md) e, por padrao, a task
vinculada em tasks/ -- ja com fontes/ e descricao-tarefa.md apontando de volta pra ata.

O script so monta o esqueleto. Quem le a transcricao/notas em materiais/ e escreve o
conteudo real da ata e da task e o agente, depois -- mesmo padrao de novo_notebook.py
(script monta estrutura, agente preenche conteudo).

Templates minimos aqui (nao dependem de ../templates/); a versao mais rica de ata fica em
../templates/ata.md, para quem quiser copiar por cima.

Uso:
    python nova_ata.py --titulo "Kickoff Financeiro" --data 15-03-26
    python nova_ata.py --titulo "Alinhamento interno" --data 20-03-26 --sem-task
"""
import argparse
import re
import unicodedata
from pathlib import Path


def slug(nome: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "-", sem_acento).strip("-").lower() or "reuniao"


def criar_dir(caminho: Path) -> None:
    if caminho.exists():
        return
    caminho.mkdir(parents=True)
    print(f"  + {caminho}/")


def escrever_se_nao_existir(caminho: Path, conteudo: str) -> bool:
    if caminho.exists():
        print(f"  = {caminho} (mantido)")
        return False
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(conteudo)
    print(f"  + {caminho}")
    return True


TEMPLATE_ATA = """# Ata -- {titulo}

> Template minimo gerado por `nova_ata.py`; versao mais rica em `../templates/ata.md`.

| Campo | Valor |
|---|---|
| Data | {data} |
| Duracao | TODO |
| Participantes (cliente) | TODO |
| Participantes (nos) | TODO |
| Materiais | ver `materiais/` |

> TODO: contexto da reuniao em 1-2 frases.

## 1. Temas discutidos

TODO

## 2. Decisoes

| # | Decisao | Dono |
|---|---|---|
| | | |

## 3. Pendencias e proximos passos

- [ ] TODO -- responsavel: TODO -- prazo: TODO

## 4. Specs geradas

Ver `specs/`.
"""

TEMPLATE_DESCRICAO_TAREFA = """# TASK-{numero:03d} -- {titulo}

## Origem

Reuniao "{titulo}" em {data} (ver `reunioes/{pasta_reuniao}/ata.md`).

## O que fazer

TODO -- preencher depois de ler a ata.

## O que ler antes

- `reunioes/{pasta_reuniao}/ata.md`
- `reunioes/{pasta_reuniao}/materiais/`

(Ver tambem `fontes/` nesta pasta, com os materiais recebidos como chegaram.)

## Como entregar

TODO

## Decisoes do usuario

TODO -- preenchido ao longo da conversa, conforme as escolhas forem feitas.

## Referencias

TODO
"""


def proxima_task_numero(pasta_tasks: Path) -> int:
    """Escaneia tasks/TASK-NNN__* existentes e retorna o proximo numero livre."""
    maior = 0
    if pasta_tasks.is_dir():
        for item in pasta_tasks.iterdir():
            m = re.match(r"TASK-(\d+)__", item.name)
            if m:
                maior = max(maior, int(m.group(1)))
    return maior + 1


def main():
    parser = argparse.ArgumentParser(
        description="Cria a pasta de uma reuniao nova (materiais/specs/ata.md) e, por "
        "padrao, a task vinculada em tasks/."
    )
    parser.add_argument("--titulo", required=True, help="Titulo da reuniao")
    parser.add_argument("--data", required=True, help="Data no formato DD-MM-AA")
    parser.add_argument("--projeto", default=".", help="Raiz do projeto (default: pasta atual)")
    parser.add_argument("--sem-task", action="store_true", help="Nao cria a task vinculada")
    args = parser.parse_args()

    base = Path(args.projeto)
    slug_titulo = slug(args.titulo)
    pasta_reuniao_nome = f"{args.data}__{slug_titulo}"
    pasta_reuniao = base / "reunioes" / pasta_reuniao_nome

    print(f"Reuniao '{args.titulo}' em {pasta_reuniao}\n")
    criar_dir(pasta_reuniao / "materiais")
    criar_dir(pasta_reuniao / "specs")
    escrever_se_nao_existir(pasta_reuniao / "ata.md", TEMPLATE_ATA.format(titulo=args.titulo, data=args.data))

    if not args.sem_task:
        pasta_tasks = base / "tasks"
        numero = proxima_task_numero(pasta_tasks)
        pasta_task = pasta_tasks / f"TASK-{numero:03d}__{slug_titulo}"
        print(f"\nTask vinculada: {pasta_task}\n")
        criar_dir(pasta_task / "fontes")
        escrever_se_nao_existir(
            pasta_task / "descricao-tarefa.md",
            TEMPLATE_DESCRICAO_TAREFA.format(
                numero=numero, titulo=args.titulo, data=args.data, pasta_reuniao=pasta_reuniao_nome
            ),
        )

    print("\nProximo passo: leia o material em materiais/ e preencha ata.md (e a task, se criada).")


if __name__ == "__main__":
    main()
