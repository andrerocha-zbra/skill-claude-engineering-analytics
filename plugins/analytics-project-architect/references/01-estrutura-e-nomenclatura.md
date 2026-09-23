# Estrutura de pastas e nomenclatura

## Árvore de um projeto

```
<projeto>/
├── PROJETO.md                       # log vivo + manifesto
├── AGENTS.md / CLAUDE.md            # bootstrap
├── .claude/settings.json            # hooks
│
├── .skills/                         # raro -- skill especifica deste projeto (ver secao "Pastas raras")
├── prompts/                         # raro -- roteiro especifico deste projeto (ver secao "Pastas raras")
│
├── @client_context/                 # conhecimento de negocio do cliente
│   ├── README.md                    # regra de evidencia, contratos de ID, navegabilidade
│   ├── visao-geral.md
│   ├── glossario.md
│   ├── processos/                   # um arquivo por processo, com ID proprio (PROC-*)
│   ├── design-system/               # tokens visuais do cliente (paleta, tipografia, logos)
│   ├── data/
│   │   ├── arquitetura-informacao.md
│   │   ├── perguntas-abertas.md
│   │   └── catalogos/*.csv          # interface estruturada -- mesmos IDs dos arquivos .md
│   └── fontes-externas/
│       └── <sistema>/
│           ├── FONTE.md             # de onde vem, com que frequencia atualiza, o que e permitido editar a mao
│           ├── manifesto-download.csv
│           ├── catalogo-api.md      # indice navegavel dos endpoints
│           └── referencia/*.md      # um arquivo por endpoint
│
├── apresentacoes/                   # decks e entregas ao cliente
├── reunioes/
│   └── DD-MM-AA__titulo/
│       ├── materiais/               # transcricoes, gravacoes, resumos, notas cruas
│       ├── ata.md
│       └── specs/                   # specs derivadas desta reuniao
│
├── powerbi/
│   └── <dominio>/
│       ├── <pagina-ou-entidade>/    # estrutura filha -- ver secao "Estrutura filha" abaixo
│       │   ├── especificacao.md
│       │   └── problemas/
│       ├── <projeto>.pbip
│       └── docs/
│
├── datalake/
│   ├── _tech-sync/                  # UNICA pasta conectada a plataforma de dados -- ver secao "A fronteira de sincronizacao"
│   │   ├── silver/<entidade>/NB_SILVER_<ENTIDADE>.ipynb
│   │   ├── gold/<entidade>/NB_GOLD_<ENTIDADE>.ipynb
│   │   ├── ml/
│   │   ├── utils/
│   │   ├── metadata_driven/metadata_driven_orchestration.csv   # se Fabric
│   │   ├── databricks.yml + resources/                          # se Databricks (Asset Bundle)
│   │   └── tests/                   # pytest so para helpers compartilhados, nunca para notebook
│   └── documentacao/                # espelha os MESMOS nomes de entidade de _tech-sync/, nunca sincroniza
│       └── <camada>/<entidade>/
│           ├── catalogo.md          # documento de negocio do produto
│           ├── problemas/
│           │   ├── problemas-identificadas.md
│           │   ├── critico/
│           │   └── resolvido/
│           ├── modelagem/
│           │   └── consideracoes.md
│           └── obsoleto/            # versao anterior do notebook, arquivada aqui (fora de _tech-sync/)
│
├── ml/
│   └── <modelo>/
│       ├── notebooks/
│       ├── cartao-modelo.md
│       └── experimentos/
│
├── tasks/                           # unico, top-level
│   ├── tempo-de-trabalho.md         # registro acumulado, uma secao por task
│   └── TASK-NNN__<slug>/
│       ├── descricao-tarefa.md      # ver templates/task/descricao-tarefa.md
│       └── fontes/                  # insumos recebidos, como chegaram
│
├── historico/                       # arquitetura/decisao supersedida -- congelada, nunca editada
└── backup/
```

Sem prefixo numérico em nenhuma pasta de topo. Nome descreve o conteúdo; ordem na árvore não importa para navegação (o agente sempre lê pelo nome, não por posição).

## A fronteira de sincronização

`datalake/_tech-sync/` é a única pasta que o Git integration do Microsoft Fabric ou o Git folder (sparse checkout) do Databricks devem enxergar. As duas plataformas sincronizam a pasta inteira que apontam — não escolhem arquivo por arquivo. Por isso `_tech-sync/` guarda só o que precisa rodar na plataforma: notebooks, configuração de orquestração, bundle. Documentação, atas, regras de negócio, especificação de Power BI — tudo isso convive no mesmo repositório mas fora de `_tech-sync/`, para nunca vazar para dentro do workspace do cliente.

Essa regra é o motivo de `datalake/documentacao/<camada>/<entidade>/` existir como pasta irmã de `datalake/_tech-sync/<camada>/<entidade>/`, em vez de a documentação morar dentro da pasta do notebook: os dois lados usam o mesmo nome de entidade — quem procura tudo sobre `doadores` sabe onde olhar dos dois lados — sem que a documentação cruce para dentro do que é sincronizado.

Detalhe de configuração de cada plataforma: `references/08-cicd-fabric-databricks.md`.

## Estrutura filha

Cada entidade (um notebook, uma página de Power BI, um modelo de ML) ganha sua própria pasta, nomeada pela entidade, contendo o que é dela: notebook (ou spec), documento de negócio, problemas conhecidos, considerações de modelagem. Achar tudo sobre uma entidade específica é abrir uma pasta, não procurar o nome dela espalhado em três lugares diferentes (uma pasta de código, uma pasta de documentação geral, uma pasta de issues).

Isso vale em `datalake/` (respeitando a fronteira de sincronização acima), em `powerbi/<dominio>/<pagina-ou-entidade>/`, e no espírito, em `ml/<modelo>/`.

Quando um notebook é substituído por uma versão nova com desenho diferente, a versão antiga vai para `datalake/documentacao/<camada>/<entidade>/obsoleto/` — nunca fica em `_tech-sync/`, porque não roda mais na plataforma.

## Regras de crescimento

- Novo domínio numa tecnologia existente → nova subpasta dentro da banda (`powerbi/<novo-dominio>/`).
- Nova tecnologia → nova pasta de topo, nomeada pela tecnologia (sem precisar de número reservado — o nome já diz o que é).
- Nova reunião → nova pasta cronológica em `reunioes/`.
- Regra transversal a vários domínios → vai para `@client_context/`, nunca duplicada em cada domínio.
- Projeto de 1 produto só pode enxugar a subpasta de domínio (ex.: `powerbi/` sem subpasta extra, se só existe um domínio); projeto com N domínios simultâneos mantém a árvore cheia, com `PROJETO.md` rastreando o estado de cada frente.

## Pastas raras: `.skills/` e `prompts/`

A maior parte do conteúdo técnico — padrões, roteiros, scripts de scaffold — mora na skill instalada como plugin, não em cada repositório de projeto; isso evita duplicar a correção de um padrão em N clientes quando ele muda. `.skills/` e `prompts/` existem no projeto só para o caso raro de um roteiro ou uma skill genuinamente específica deste cliente, que não faz sentido subir para a skill genérica. Ficam vazias por padrão, com um `README.md` de uma linha explicando isso — usadas só quando surgir a necessidade real.

## Convenção de nomes

- Pasta e arquivo em minúsculo, hífen como separador (`consideracoes-modelagem.md`, não `consideracoes_modelagem.md`), sem acento em nome de arquivo/pasta (acento é permitido no conteúdo).
- Data de reunião: `DD-MM-AA__titulo-curto`.
- Task: `TASK-NNN__slug`, número sequencial de 3 dígitos, sem buracos.
- Notebook: `NB_<CAMADA>_<ENTIDADE>.ipynb`, caixa alta, mesma convenção usada dentro do conteúdo do notebook (ver `references/03-datalake-core.md`).
- Trabalho não-entregável (o que não deveria ir para o cliente) usa prefixo `_` — é o caso de `_tech-sync/`, que existe para marcar a fronteira de sincronização, não para indicar "privado" em geral.
- IDs estáveis quando existirem: `PROC-*` (processos), `DOM-*` (domínios de dados), `SRC-*` (fontes/evidências), `DP-*` (produtos de dados) — citados em `@client_context/` e referenciados em specs e commits, nunca redefinidos localmente.
