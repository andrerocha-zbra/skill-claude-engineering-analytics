# Reorganizar um projeto existente para o padrão

Caminho para quando já existe um projeto — com dados reais fluindo, histórico de commits, gente trabalhando nele — e o objetivo é trazê-lo para a árvore padrão (`references/01-estrutura-e-nomenclatura.md`) sem recomeçar do zero.

## Quando usar este caminho em vez de `scaffold_cliente.py`

`scripts/scaffold_cliente.py` cria a árvore a partir do nada: assume que não há conflito de nomes, não há histórico de git para preservar, não há ninguém mais commitando na pasta ao mesmo tempo. Isso é correto para kickoff, mas errado para um projeto que já roda.

Use o caminho deste documento quando o projeto avaliado tiver qualquer um destes sinais:

- Já existem tabelas/notebooks/relatórios com dado real de produção, não só esqueleto.
- Há histórico de git que vale preservar por arquivo (quem mudou o quê, quando) — recriar do zero e copiar os arquivos por cima perde esse histórico; mover com `git mv` preserva.
- Existe uma pasta hoje conectada a uma plataforma de dados (Fabric ou Databricks) via integração Git — mover ou renomear essa pasta sem cuidado quebra a sincronização (ver `references/08-cicd-fabric-databricks.md`).
- Outras pessoas dependem da estrutura atual no dia a dia — uma recriação integral interrompe o trabalho delas no meio.

Se nenhum desses sinais está presente — pasta vazia, projeto ainda não iniciado, sem dado real — use `scaffold_cliente.py` diretamente; reorganizar em fatias só adiciona passos sem necessidade.

## Passo 1 — diagnóstico com `avaliar_projeto_existente.py`

```
python scripts/avaliar_projeto_existente.py --projeto CAMINHO
python scripts/avaliar_projeto_existente.py --projeto CAMINHO --saida relatorio-gap.md
```

O script é **somente leitura** — nunca move, edita ou apaga nada dentro da pasta avaliada. Sem `--saida`, imprime o relatório no terminal; com `--saida`, grava o Markdown no caminho indicado, que deve ficar fora da pasta avaliada (o script recusa gravar lá dentro).

O relatório tem, nesta ordem: aviso de risco de CI/CD (só se algum sinal aparecer), o estado de cada banda-alvo (existe, não existe, ou há pasta parecida que pode ser equivalente), presença de governança (`PROJETO.md`, `AGENTS.md`, `CLAUDE.md`, `.claude/`), notebooks encontrados com uma classificação textual simples, e uma lista fixa de próximos passos.

Como ler o relatório:

- O aviso de CI/CD, quando aparece, é o dado mais importante da leitura inteira — ver seção própria abaixo.
- As "candidatas equivalentes" de banda são heurística por palavra-chave no nome da pasta (`bronze`/`silver`/`gold` sugerindo datalake, `powerbi`/`pbip` sugerindo Power BI, e assim por diante). É um chute informado, não uma constatação — o relatório mesmo já rotula cada uma como "confirme antes de mover".
- A classificação de notebook (temp views vs. CTE) é contagem de substring no código-fonte, não uma leitura do notebook. Serve para decidir por onde começar a olhar, não para decidir uma migração.
- Ausência de `PROJETO.md`/`AGENTS.md`/`CLAUDE.md` não é urgente de resolver com migração — é o primeiro próximo passo listado no relatório, e não depende de mexer em pasta nenhuma.

## Gate obrigatório: nenhum `git mv` sem confirmação explícita

O script sugere equivalências; ele não decide nada. Antes de qualquer `git mv` baseado numa candidata do relatório, confirmar com o usuário via `AskUserQuestion` — qual pasta atual vira qual pasta-alvo, e em que ordem. Isso vale mesmo quando a heurística parece óbvia (uma pasta chamada `powerbi-reports` quase certamente vira `powerbi/`): a confirmação é sobre o usuário validar o mapeamento antes da mudança acontecer, não sobre a skill estar em dúvida.

Isso segue a mesma regra de gates já estabelecida em `references/02-processo-e-templates.md`: ação consequente e difícil de reverter sem aviso pede pergunta, não suposição. Reorganizar a estrutura de um projeto com dado e histórico reais se qualifica.

## Pasta conectada a uma plataforma de dados: nunca mexer sem confirmar a reconexão

Quando o diagnóstico aponta sinal de CI/CD (arquivo `databricks.yml`, YAML mencionando `databricks bundle`/`bundle:`, pasta `.fabric/`, README citando "Git integration"), a pasta correspondente já pode estar com sincronização ativa com Fabric ou Databricks. Mover ou renomear essa pasta com `git mv`, por si só, não avisa a plataforma — a integração continua apontando para o caminho antigo, e a sincronização para de funcionar sem erro visível na hora.

Por isso, mexer nessa pasta nunca é um efeito colateral de "organizar a estrutura" — é sempre uma ação deliberada, separada, decidida com o usuário: quando reconectar, quem tem acesso ao workspace/administração da plataforma para refazer a configuração, e se algum pipeline em execução pode ser interrompido durante a troca. Reconectar significa apontar a integração Git da plataforma para o novo caminho de `_tech-sync/` (`references/08-cicd-fabric-databricks.md` descreve a configuração para Fabric e Databricks) — e isso só acontece depois que a migração daquela banda já está concluída do lado do git, nunca antes.

## Migrar em fatias, não de uma vez

Cada banda migra em uma fatia própria, com commit próprio, usando `git mv` (preserva o histórico do arquivo em vez de apagar e recriar):

```
git mv relatorios-powerbi powerbi
git commit -m "Master: Movido relatorios-powerbi para powerbi/ (reorganizacao)"
```

Uma fatia por vez, em vez de uma reorganização única com tudo junto, por dois motivos práticos: cada commit fica pequeno o bastante para revisar de verdade (conferir que nada sumiu, que os caminhos batem) e, se alguma coisa quebrar depois de uma fatia — um pipeline que referenciava o caminho antigo, por exemplo — reverter aquele commit específico não desfaz o resto do trabalho já validado.

Ordem sugerida: começar pelas bandas sem sinal de CI/CD (menor risco), deixar a banda que toca `_tech-sync/` por último, já que essa é a única que exige a reconexão deliberada descrita acima.

## Depois que a estrutura básica existe

Com as bandas migradas (ou pelo menos a fundação e as bandas de maior prioridade), os passos seguintes já não são específicos deste fluxo:

- Árvore-alvo completa, growth rules e o que fica em `historico/` vs. `backup/`: `references/01-estrutura-e-nomenclatura.md`.
- Inicializar `PROJETO.md` a partir de `templates/PROJETO.md`, registrar a primeira entrada de log marcando a reorganização como concluída, e seguir a convenção de commits e a regra de log vivo: `references/02-processo-e-templates.md`.
