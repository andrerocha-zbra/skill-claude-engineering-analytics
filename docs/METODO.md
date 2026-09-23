# O método

Como um agente de IA conduz um projeto de engenharia de analytics do kickoff ao handoff: onde cada tipo de conhecimento mora, o que é obrigatório, e por que a estrutura é essa.

Use este documento de duas formas: como leitura, para entender o raciocínio por trás da skill `analytics-project-architect`; ou como referência de bootstrap, seguindo o checklist da seção final para montar um projeto novo à mão, sem a skill.

## Para que serve

Um agente produz trabalho consistente quando o repositório diz o que é obrigatório, o que já foi decidido, e como se faz cada tipo de entrega. Quando essas três coisas vivem só na cabeça de quem conduz o projeto, cada sessão recomeça do zero, cada artefato sai um pouco diferente do anterior, e uma decisão já tomada vira discussão de novo.

## Princípios

Cada um existe porque a ausência dele custa caro.

### Separar contrato estável de estado vivo

Regra que não muda de tarefa para tarefa vive em um arquivo. Decisão datada, log de execução e estado atual vivem em outro. Misturar os dois produz um arquivo que ninguém lê inteiro, porque metade é histórico e a outra metade é regra, sem marcação de qual é qual.

Teste prático: se a informação responde "como se faz aqui", é contrato. Se responde "o que aconteceu" ou "o que já decidimos", é estado.

### Padrão versionado, nunca implícito

Uma regra técnica que só existe na memória de quem conduz o projeto não sobrevive a uma sessão nova, uma máquina nova, ou outra pessoa assumindo o trabalho. Toda regra reaproveitável vira arquivo: skill, template, ou reference. O que é específico de um cliente fica isolado do que é genérico, para que a regra genérica sirva ao próximo cliente sem arrastar o anterior junto.

### Roteiro por tipo de entrega, não instrução repetida

Toda entrega recorrente tem um roteiro. Criar uma camada de ingestão segue um roteiro. Criar uma camada de consumo segue outro. Documentar e catalogar um produto pronto segue um terceiro. Sem isso, o processo é reexplicado a cada pedido, com variação a cada vez.

### Evidência declarada

Toda regra de negócio registra de onde veio e com que força. Uma capacidade descrita na documentação de um fornecedor não prova que o cliente executa o processo daquela forma. Um número tirado de um protótipo não é regra homologada. Isso pede um vocabulário fechado de estados de evidência, aplicado à base de conhecimento inteira:

| Estado | Significado |
|---|---|
| `CLIENTE_CONFIRMADO` | Registrado em reunião, nota ou requisito fornecido pelo cliente |
| `SISTEMA_DOCUMENTADO` | Capacidade descrita pelo fornecedor; precisa validação no processo real |
| `INFERIDO` | Hipótese consistente com as evidências, não confirmada pelo negócio |
| `SIMULADO` | Criado para protótipo, mock ou teste; não é dado oficial |
| `PENDENTE_VALIDACAO` | Evidência insuficiente ou decisão de negócio em aberto |

Dois eixos ortogonais completam o vocabulário: implantação (`AS_IS`, `PARCIAL`, `TO_BE`) e validação (`VALIDADO`, `PENDENTE`, `CONFLITANTE`). O que o cliente faz hoje nunca se mistura com o que ele poderia fazer — processo atual e processo desejado ficam separados e rotulados.

### Falha visível antes de default silencioso

Todo de-para, toda classificação, toda deduplicação e toda derivação declara o que acontece com o valor que não se encaixa. A ordem de preferência é: falhar visivelmente, avisar e seguir, aplicar default. Default silencioso é a última opção e exige justificativa registrada.

Esse é o princípio mais caro de ignorar porque a falha, por construção, não faz barulho. Uma junção sem correspondência e uma chave que vira nula produzem uma tabela menor sem erro nenhum. O dado some e o painel continua carregando.

### Pendência é artefato que se move, não que some

Um problema conhecido vira arquivo. Um problema resolvido não é apagado: é movido para uma pasta de resolvidos, com a data e a resolução no topo. Resolver sem mover deixa o repositório mentindo sobre o que está em aberto.

### O cérebro não vaza para o entregável

Os arquivos de governança orientam quem constrói. Eles não aparecem no que é entregue. Um notebook, um relatório ou um modelo semântico nunca cita por nome o arquivo de regras, o roteiro, ou a pasta de tarefas — nem em comentário, nem em texto.

Duas razões: o cliente vê o entregável, não a documentação interna, então a referência fica quebrada do lado dele; e a explicação boa descreve o fato em si, em vez de apontar para onde ele está documentado.

### Documentação colada no artefato que ela descreve

Cada produto de dados carrega, na própria pasta, os problemas conhecidos e o documento de negócio que o descreve. Um wiki separado envelhece porque a distância entre o código e a explicação cresce a cada mudança, e ninguém percorre essa distância sob prazo.

### Rastreabilidade do trabalho, não só do código

Git conta o que mudou. Não conta o que foi decidido, o que foi descartado no caminho, e o que ficou em aberto. Isso pede um registro por tarefa, aberto quando a tarefa começa e fechado só quando confirmado.

### Nomenclatura obrigatória sem exceção

Nome de arquivo, nome de tabela e nome de chave seguem um padrão declarado, sem julgamento caso a caso. Previsibilidade vale mais que elegância pontual — o agente encontra o artefato sem busca aberta, e busca aberta é a maior fonte de desperdício de contexto numa sessão longa. Um artefato fora do padrão se corrige na próxima vez que for tocado; o antigo vai para `historico/`, nunca é apagado.

## Três camadas de trabalho

| Camada | O que guarda | Muda quando |
|---|---|---|
| Skill | O método em si: estrutura, processo, padrões técnicos, scripts, hooks | Quando uma regra de método muda para todo mundo que usa a skill |
| Perfil de empresa (opcional) | Identidade, voz e design default de quem está conduzindo os projetos | Quando a identidade da consultoria muda |
| Repositório do projeto | Dados, regras de negócio, decisões e histórico de um cliente específico | A cada entrega |

Um projeto nunca escreve na skill nem no perfil de empresa. A skill nunca guarda dado de um projeto específico. Essa separação é o que permite rodar o mesmo método em vários projetos ao mesmo tempo sem que uma correção num padrão técnico exija editar cada projeto um por um, e sem que o conhecimento de um cliente vaze para outro.

## A árvore de um repositório de projeto

```
<projeto>/
├── PROJETO.md                 # log vivo + manifesto
├── AGENTS.md / CLAUDE.md      # bootstrap fino
├── .claude/settings.json      # hooks
├── @client_context/           # fundação: regras de negócio, catálogo, design-system do cliente
├── apresentacoes/
├── reunioes/DD-MM-AA__titulo/
├── powerbi/<dominio>/
├── datalake/
│   ├── _tech-sync/            # única pasta conectada à plataforma de dados (ver CI/CD)
│   └── documentacao/
├── ml/<modelo>/
├── tasks/
├── historico/                 # decisões e arquitetura supersedidas, congeladas
└── backup/
```

Detalhe completo de nomenclatura e das regras de crescimento: `references/01-estrutura-e-nomenclatura.md`.

### `@client_context/`, `datalake/` e `historico/` — a memória por taxa de mudança

| O que muda | Onde mora | Pergunta que decide |
|---|---|---|
| Quase nunca (contrato) | `@client_context/` | Isso continuaria verdade se trocássemos de nuvem ou de ferramenta de BI? |
| A cada entrega (implementação) | `datalake/`, `powerbi/` | Isso cita um notebook, uma tabela, uma medida ou uma tela específica? |
| Nunca mais (histórico) | `historico/` | Isso foi formalmente substituído por outra coisa? |
| Contínuo (estado vivo) | `PROJETO.md` | O que aconteceu, quando, e por quê? |

Separar por taxa de mudança evita o problema mais comum de documentação em projeto longo: um cabeçalho desatualizado afirmando o oposto do que o sistema faz hoje, porque ninguém sabia qual dos dois documentos atualizar.

## Governança do projeto

Três arquivos na raiz, com papéis que não se sobrepõem.

| Arquivo | Muda quando | Lido como |
|---|---|---|
| `AGENTS.md` | Quase nunca | Inteiro, toda sessão |
| `CLAUDE.md` | Quando uma regra muda | Inteiro, toda sessão |
| `PROJETO.md` | A cada entrega | Seletivamente — seções fixas + últimas entradas do log |

`PROJETO.md` cresce sem limite se nada o contiver. Por isso o bootstrap lê só as últimas entradas do log, e por isso o log se rotaciona por trimestre: entradas antigas migram para `PROJETO.md.historico/AAAA-QN.md`, o arquivo principal mantém o resumo do período corrente e as entradas recentes. Fazer isso desde o primeiro trimestre custa nada; arrumar depois que o arquivo passou de cem mil caracteres custa uma tarde.

### Esqueleto de `AGENTS.md`

```markdown
# AGENTS.md

Ponto de entrada obrigatório. Define só a inicialização; regras e estado ficam nas
fontes canônicas abaixo.

## Inicialização obrigatória
1. Trabalhe em português.
2. Leia `CLAUDE.md` integralmente.
3. Leia `PROJETO.md` seletivamente: seções de estado e as 10 entradas mais recentes
   do Log. Não carregue o arquivo inteiro.

## Fontes e operação
- `PROJETO.md` é a fonte do estado e das decisões.
- Use a skill instalada para estrutura, roteiros e padrões técnicos.
- Atualize `PROJETO.md` quando o trabalho mudar estrutura, contrato ou decisão técnica.
```

### Esqueleto de `CLAUDE.md`

```markdown
# CLAUDE.md

Contrato operacional estável. Estado e decisões recentes ficam em `PROJETO.md`.

## Contexto
Cliente, objetivo, stack, idioma, responsável padrão, ambientes.

## Vocabulário de negócio
De-para entre o termo do cliente e o termo técnico.

## Sistemas de origem
Tabela com identificador numérico e nome de cada sistema; regra de prefixo de chave.

## Padrão <camada>
Uma seção por camada de dados, com regras obrigatórias e o que exige confirmação
antes de mudar.

## Regras de operação
O que sempre fazer, o que nunca fazer, o que exige perguntar antes. Inclui a regra
de que o entregável nunca cita os arquivos de governança.
```

Três regras de operação que evitam mais retrabalho que qualquer outra: perguntar antes de apagar dado, trocar ambiente de produção ou mudar estratégia de carga; registrar log no formato `- [AAAA-MM-DD HH:mm] {Tecnologia} {Domínio}: ...`; e, ao revisar um produto, conferir se a documentação técnica ainda reflete a decisão tomada, atualizando no mesmo trabalho quando não refletir.

### Esqueleto de `PROJETO.md`

```markdown
# Projeto <nome> — <objetivo em uma linha>

## Estado por fase
| Fase | Estado | Notas |

## Mapa Necessidade → Solução
| ID | Necessidade | Onde é resolvido | Status |

## Decisões
| Data | Decisão | Alternativas | Motivo |

## Log
- [AAAA-MM-DD HH:mm] {Tecnologia} {Domínio}: o que foi feito, por quê, o que ficou aberto
```

Decisões e Log respondem perguntas diferentes: Decisões é onde se procura "por que está assim"; Log é onde se procura "o que aconteceu naquela semana". Juntar as duas obriga a varrer o log inteiro para achar uma decisão. Em projetos mais estratégicos, `## Decisões` pode se dividir em `## ADR` (decisão técnica), `## BDR` (decisão de negócio ainda pendente) e `## Riscos` — o template completo em `templates/PROJETO.md` documenta quando vale essa divisão.

## Skills, na tipologia que não se sobrepõe

| Tipo | Responde | Onde vive nesta skill |
|---|---|---|
| Arquiteto do projeto | Qual é o fluxo obrigatório e quais são as fontes de verdade | `SKILL.md` |
| Padrões da stack | Como se constrói tecnicamente | `references/03-datalake-core.md` + overlays, `04`, `05` |
| Modelo do artefato | Qual é a forma do entregável | `templates/` |
| Formato de saída | Como reportar | `references/02-processo-e-templates.md` (convenção de commit) |

## Roteiros

Um roteiro é um arquivo com duas partes: instruções para quem vai usá-lo e um bloco colável para o agente. As duas partes ficam separadas porque a primeira tem avisos operacionais que não precisam entrar no contexto do agente.

Regra de execução, repetida em todo roteiro: fazer as leituras e buscas na própria conversa, sem delegar a um subagente a menos que uma busca direta falhe ou volte ambígua — um roteiro fechado, com locais previsíveis, não exige exploração aberta do repositório.

Regra de conteúdo, também repetida: o artefato gerado nunca cita, por nome, os arquivos de governança, nem em comentário nem em texto.

## Rastreabilidade

### Tarefa

Uma pasta por tarefa, com o pedido como chegou e os insumos como chegaram. Um insumo recebido pode estar desatualizado — conferir contra o repositório e contra qualquer evidência de execução real custa dois minutos e evita construir sobre premissa errada.

### Tempo

Um registro único e acumulado, não um arquivo por tarefa. Uma seção por tarefa, aberta no início com o fim em branco, fechada só depois de confirmação. Três campos de commit no fechamento — mensagem técnica objetiva, notas pessoais de débito técnico, e síntese de valor entregue — porque o mesmo trabalho é contado de três formas para três públicos, e escrever as três com o contexto fresco é mais barato que reconstruir depois.

## Guardrails em código, não só em prompt

Para cada regra escrita em `CLAUDE.md` ou numa skill, vale perguntar: o que acontece se o agente ignorar isso por engano? Se a resposta for "dado errado gravado" ou "artefato corrompido", a regra não deve depender só de o agente lembrar — ela vira validação que bloqueia (quality gate no notebook, ver `references/03-datalake-core.md`) ou hook que impede a ação (ver `references/07-mecanismos-e-hooks.md`). Prompt é probabilístico; código é determinístico. A regra "nunca editar TMDL na mão" e a regra "scripts destrutivos pedem confirmação explícita" são os dois exemplos que esta skill já resolve em hook, não em prosa.

## Ingestão de API paginada

Transversal a qualquer stack, então fica aqui em vez de num reference específico de nuvem.

O resultado bruto vai para a camada de ingestão sem transformação, com todo campo como texto — isso deixa a API livre para mudar o formato de um campo sem quebrar a ingestão.

Antes de publicar, valida-se:

- Paginação real, com parada pelo total informado na resposta e um limite de segurança contra laço infinito quando o total não vier.
- Guarda de resposta vazia: nunca sobrescrever a tabela quando a API devolver zero registros. Pular a escrita, preservar o histórico, avisar no log — sem essa guarda, uma instabilidade da origem apaga a base inteira.
- Limite de requisições respeitado num único ponto de passagem. Toda chamada passa por uma função que controla o intervalo mínimo desde a chamada anterior, repete quando a API recusa por excesso esperando o tempo indicado, e repete com espera crescente em erro de servidor — nunca uma chamada direta fora dessa função.
- Corte incremental é opcional por entidade, nunca automático, e só faz sentido quando o endpoint documenta um filtro confiável e a camada seguinte já deduplica pela chave de negócio. Quando houver corte incremental, o ponto de partida se calcula a partir do maior valor já gravado menos uma janela de folga — sem a folga, um registro com data retroativa nunca mais é buscado.

Trocar o endpoint de uma ingestão existente é mudança de contrato, não ajuste de configuração — um endpoint "mais leve" do mesmo fornecedor pode devolver uma fração dos campos, e tudo que consome aquela entidade quebra em silêncio. Antes de trocar, listar quem consome e quais campos.

## Modelo semântico e BI

O modelo semântico (medidas, hierarquias, relacionamentos) é uma camada de dados como outra qualquer, com o mesmo tratamento de padrão e revisão — não "só a visualização". Detalhe técnico completo: `references/04-powerbi-modelagem-dax.md` (modelagem e DAX) e `references/05-powerbi-frontend.md` (visuais customizados).

Validação antes de publicar: cada medida conferida contra a consulta equivalente na camada analítica que a alimenta. Um total que não bate é o defeito mais comum e o mais difícil de perceber tarde.

O que versiona é a definição extraída em texto (medidas, consultas, metadados do modelo), nunca o binário — binário versiona mal e não gera diff legível.

## Machine learning

O modelo treinado e o conjunto de atributos que o alimenta são dois artefatos com ciclos de vida diferentes; tratá-los como um só é a origem mais comum de confusão nesta camada. A camada de atributos fica entre a analítica e o modelo, reutilizável entre modelos; o experimento é descartável por natureza e não deve poluir o caminho de produção.

Antes de publicar: métrica de avaliação contra uma linha de base declarada, verificação de vazamento de informação do futuro para o passado, comparação da distribuição dos atributos entre treino e inferência.

O cartão do modelo — finalidade, dados de treino, métricas, limitações conhecidas, população para a qual ele não vale — é o equivalente ao documento de negócio de um produto de dados, e a parte de limitações é a que mais evita uso indevido.

O que nunca versiona: o binário do modelo e o dado de treino dentro do repositório de código — vivem num registro próprio, referenciado por versão.

## Armadilhas conhecidas

Sinais concretos de que algo precisa de atenção, escritos como orientação direta:

- **Log sem rotação cresce sem limite.** Arquive por trimestre desde o primeiro, não quando o arquivo já estiver grande demais para ler.
- **Padrão aplicado a uma camada e esquecido na outra** vira inconsistência que confunde tanto o agente quanto quem entra no projeto depois. Quando um padrão novo nasce, decidir na hora se ele vale para todas as camadas e, se valer, migrar de uma vez — migração "na próxima vez que tocar" convive mal com prazo.
- **Validação descrita no padrão e ausente no artefato** é um defeito silencioso: o padrão diz uma coisa, o código faz outra, nada acusa. Vale testar que as etapas declaradas existem de fato.
- **Insumo recebido pode ser cópia desatingida.** Conferir contra o repositório e contra evidência de execução real é passo fixo do roteiro, não bom senso de quem estiver conduzindo.
- **Camada mantida por outra equipe, sem contrato**, quebra em silêncio quando a estrutura de origem muda. Uma verificação de contrato no início do artefato, que confere se as colunas esperadas existem e falha com mensagem clara, custa poucas linhas.

## Checklist de bootstrap

Ordem para montar um projeto novo, via `scripts/scaffold_cliente.py` ou à mão seguindo os esqueletos acima.

**Antes de escrever qualquer código**
1. `AGENTS.md` e `CLAUDE.md` com contexto, idioma, nomenclatura obrigatória e sistemas de origem.
2. `PROJETO.md` com estado por fase, ainda que vazio.
3. `.claude/settings.json` com os hooks instalados.

**Com o primeiro artefato em mãos**
4. Construir o primeiro notebook ou medida com capricho e tratá-lo como referência.
5. Registrar a primeira entrada de log.

**Antes da primeira entrega**
6. Base de regras de negócio em `@client_context/`, com a regra de evidência aplicada.
7. `historico/` criado, mesmo vazio, para o dia em que algo for supersedido.

## Sinais de que o método está funcionando

- Um pedido de entrega nova cabe numa linha, porque o roteiro carrega o resto.
- A pergunta "por que está assim" se responde abrindo um arquivo, não a memória de alguém.
- Duas entregas da mesma camada, feitas com semanas de distância, saem com o mesmo formato.
- A lista de pendências do projeto é uma pasta, não uma conversa.
