# CI/CD seletivo: Fabric e Databricks a partir do repo-cérebro do cliente

## O problema que isso resolve

Um repo-cérebro de cliente guarda muito mais do que código de plataforma: atas, regras de negócio, specs de Power BI, identidade visual, apresentações. Nada disso deve ser visto pela plataforma de dados do cliente — só o código de datalake deve. A solução não é ter repositórios separados (perderia o "cérebro único por cliente"); é usar os mecanismos nativos que **Fabric e Databricks já têm para conectar a uma subpasta, não ao repo inteiro**.

Por isso a estrutura padrão (`01-estrutura-e-nomenclatura.md`) isola tudo que é sincronizável numa única pasta: `datalake/_tech-sync/`. Todo o resto do repo (`@client_context/`, `reunioes/`, `powerbi/`, `datalake/documentacao/`, `historico/`) fica fora — existe no git, nunca na plataforma.

## Microsoft Fabric

Git integration do Fabric conecta um **workspace** a **uma pasta específica** do repositório (não precisa ser a raiz — você digita o nome da pasta ao conectar). Workspaces diferentes (dev/test/prod) podem apontar para pastas ou branches diferentes do mesmo repo. Ao sincronizar, a estrutura do workspace é espelhada dentro dessa pasta (cada item vira uma subpasta com o formato nativo do Fabric).

**Configuração**:
1. Workspace do cliente (por ambiente) → *Git integration* → conectar ao repo-cérebro → pasta = `datalake/_tech-sync`.
2. Cada notebook/lakehouse/pipeline criado no workspace aparece como item dentro dessa pasta no git; o inverso também vale (editar localmente e sincronizar de volta).
3. Promoção dev→prod: via **Fabric Deployment Pipelines** (nativo da plataforma, não scriptável por fora do produto) — não é um passo de CI custom.
4. CI leve antes do merge: um workflow que só roda `scripts/limpar_notebook_import.py` (dry-check) + a mesma validação do hook `validar_notebook.py` (JSON válido + `ast.parse`) como gate de PR — pega notebook quebrado antes dele nunca chegar a sincronizar.

**Antes de conectar, crie a hierarquia de pastas no workspace**: o Git integration só espelha subpastas do repo em Workspace Folders que já existam no Fabric — ele não as cria sozinho. Sem isso, todo item exportado cai solto na raiz da pasta git conectada, quebrando o layout `silver/<entidade>/`, `gold/<entidade>/` de `01-estrutura-e-nomenclatura.md`. Crie as pastas aninhadas no workspace (via portal ou `mcp__fabric__create_folder`) espelhando exatamente a árvore de `_tech-sync/` antes do primeiro Commit/Update.

**Formato real do export (workspace → git) não é `.ipynb`, e o Git integration não aceita `.ipynb` de volta.** São dois pipelines de import diferentes, com requisitos diferentes, e é fácil confundir os dois:

- **REST API / `mcp__fabric__create_item`** (`definition.format="ipynb"`) aceita o `.ipynb` original em base64 — mas só cria o item diretamente no workspace via API, **não** participa do Git integration.
- **Git integration** ("Update from Git") só aceita o formato nativo como conteúdo principal de Notebook: `notebook-content.py` em percent-format. Tentar commitar um `notebook-content.ipynb` e mandar "Update from Git" falha com erro direto do backend: `System.ArgumentException: The file extension of notebook main content ID notebook-content.ipynb is not supported.`

Cada item Notebook vira uma pasta `<Nome>.Notebook/` com `notebook-content.py` + um `.platform` ao lado (`gitIntegration/platformProperties`, `config.logicalId` como GUID). Estrutura validada do `.py`:

```
# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {"name": "synapse_pyspark"},
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "<guid>",
# META       "default_lakehouse_name": "<nome>",
# META       "default_lakehouse_workspace_id": "<guid>",
# META       "known_lakehouses": [{"id": "<guid>"}]
# META     },
# META     "environment": {}
# META   }
# META }

# MARKDOWN ********************
# <cada linha do markdown prefixada com "# ">

# CELL ********************
<codigo Python cru, sem prefixo>

# PARAMETERS CELL ********************
<no lugar de "# CELL" quando a celula tem metadata.tags contendo "parameters">
```

Cada bloco (`MARKDOWN`/`CELL`/`PARAMETERS CELL`) é separado por uma linha em branco antes e depois. Na maioria dos casos não há bloco `# METADATA` por célula (só o do topo, a nível de notebook) — variação observada sem causa identificada, sem impacto no import.

Isso conflita de frente com a convenção "`.ipynb` import-safe" do núcleo. A convenção do projeto continua sendo manter o `.ipynb` como fonte de verdade (é nele que se edita e revisa) e tratar o `.py` do Fabric como artefato derivado — nunca editado à mão.

**Popular o workspace a partir de `.ipynb` já existentes, em massa, via git**: não tente gerar o `.py` de conversão manualmente célula por célula, nem peça pro agente montar o payload base64 inline chamada a chamada — a API funciona bem para arquivos pequenos, mas o agente gerando o conteúdo como texto dentro da chamada de tool esbarra num teto de ~25-27 mil caracteres por chamada, bem antes do tamanho de notebook real de produção (testado até notebooks de ~300KB). O padrão validado é: converter com `scripts/converter_ipynb_fabric.py <notebook.ipynb> <pasta_saida> --nome <NB_X>` (gera `<NB_X>.Notebook/notebook-content.py` + `.platform`; roda em disco via Bash/Python, sem passar pelo limite de texto por chamada), validar contra pelo menos um exemplo real já commitado pelo próprio Fabric (diff byte a byte, ignorando só CRLF/LF) antes de confiar no lote inteiro, e então `git commit` + `push` + "Update from Git" no workspace. Ver as ressalvas de cobertura na docstring do script (células `raw`, metadata por célula, `dependencies.lakehouse` ausente na origem). Só use a API/`create_item` direta (com `definition.format="ipynb"`) para criar item pontual pequeno fora do fluxo Git — nunca como substituto do Git integration para popular o workspace em lote.

Ver `07-mecanismos-e-hooks.md` (mecanismo M4) para as pegadinhas de assincronia do `create_item`.

**Testar num workspace sandbox não isola o git.** O isolamento entre um workspace de teste e o de produção existe só no nível do workspace Fabric — se o sandbox aponta para a mesma pasta git da produção (mesmo repo, mesma pasta, ainda que branch diferente não resolva se o merge for para a mesma branch), qualquer Commit feito a partir do sandbox escreve ao lado do código real. Para testar reconexão de Git integration com segurança de verdade, aponte o sandbox para uma pasta ou repo descartável, nunca para a pasta git de produção.

## Reconectar um workspace de produção já existente (não vazio)

Cenário bem diferente do anterior: o workspace já roda em produção há tempo, sem controle de versão, com itens reais (notebooks, Lakehouse, MirroredDatabase, pipelines) — não um workspace vazio esperando a primeira conexão. Aqui o risco de perda/quebra é real, a sequência muda, e três achados concretos (validados num workspace de produção real) mudam a forma de conduzir isso.

**1. Reconciliar o inventário do Fabric contra a orquestração local antes de julgar o que é "sobra".** Um item que existe no workspace mas não no repo local não é necessariamente lixo/esquecido — pode ser o inverso: um notebook criado direto em produção que nunca foi capturado no repo (gap do repo, não do workspace). Antes de sugerir limpeza de qualquer item "estranho" (nome com `_BCKP`, pasta `dev_*`, etc.), cruze com **qualquer fonte de orquestração/config local** (o CSV metadata-driven, `databricks.yml`) — nome sozinho não é prova suficiente. O inverso também acontece: o CSV pode estar desatualizado (linha com `notebook_id` placeholder para um notebook que já existe de verdade em produção há tempo). Reconciliar esse tipo de arquivo config-como-fonte-de-verdade é um passo obrigatório antes de qualquer limpeza de workspace existente, não algo a assumir como já correto.

**2. P0 — binding de Lakehouse é GUID versionado dentro do próprio notebook.** O bloco `# META` de todo notebook (ver estrutura acima) grava `default_lakehouse`, `default_lakehouse_name` e **`default_lakehouse_workspace_id`** como GUIDs literais, e isso é commitado no git junto com o resto. Consequência séria: popular um workspace de **desenvolvimento** via `Update from Git` simples (branch-out cru) a partir do histórico de um workspace de **produção** deixa os notebooks importados, por padrão, lendo/gravando na Lakehouse de PRODUÇÃO — o binding é por GUID de workspace, não por nome. O isolamento pareceria existir e não existiria. **Git integration sozinho não reescreve esse binding.** A única correção é **Fabric Deployment Pipelines com *deployment rules*** — é o único mecanismo que reescreve o binding de Lakehouse por estágio. Nunca declare um ambiente de dev "isolado" sem validar empiricamente: leia a definição de um notebook importado e confira se o GUID de `default_lakehouse_workspace_id` de fato mudou para o do workspace novo.

**3. Deployment Pipelines e Git integration são mecanismos independentes que podem conflitar silenciosamente.** Os dois podem coexistir no mesmo workspace (padrão recomendado pela própria Microsoft — branch por estágio), mas "Deploy" (promoção via pipeline) e "Commit/Update from Git" são caminhos de mudança de estado totalmente independentes um do outro. Sem uma regra explícita de qual é o caminho oficial de promoção, alguém pode usar o botão *Deploy* para levar algo a produção **contornando completamente** o gate de PR/CI configurado do lado Git. Defina e documente em `PROJETO.md`/`CLAUDE.md` qual mecanismo é a via oficial — recomendado: **merge de PR no Git é o único caminho oficial para promover código**; *Deploy* fica reservado só para rebind de conexão via deployment rules (achado 2 acima), nunca como atalho de promoção.

**O que cada tipo de item realmente suporta em Git integration** (verificado na documentação oficial do Fabric):

| Item | Git integration | Nível |
|---|---|---|
| Notebook | `.py` percent-format + `.platform`, binding de Lakehouse por GUID junto (achado 2) | GA |
| Lakehouse | Só metadata/shortcuts/DAR — tabelas e arquivos **nunca** são tocados (dado sempre preservado) | GA |
| MirroredDatabase | Só o item; SQL endpoint e filhos não são rastreados | GA (recente) |
| DataAgent | Estrutura própria (`files/config/draft`, `published`) | Preview |
| DataPipeline, CopyJob | Suportado em Deployment Pipelines; Git integration direto nesses dois ainda não verificado | Não verificado |

**Prazo real, não hipotético:** a partir de **1º de dezembro de 2026**, usuários sem permissão read-write nos itens do workspace perdem acesso ao Git integration daquele workspace. Vale um lembrete em qualquer checklist de kickoff/reconexão feito a partir de agora.

**Bootstrap do zero (sem workspace de produção prévio) não tem nada disso.** Sem bagunça pra reconciliar (achado 1) e sem binding de produção pra proteger (achado 2), o fluxo é o das seções "Configuração" acima: criar Deployment Pipeline com deployment rules desde o início (sem precisar reescrever nada depois), criar o workspace vazio, conectar direto, popular via `converter_ipynb_fabric.py`/`create_item` ou autoria no portal. Os três achados desta seção só se aplicam ao caminho "workspace já existe e está sujo".

## Databricks

Git folders do Databricks (Repos) suportam **sparse checkout por "cone pattern"**: você lista explicitamente as subpastas a clonar. A própria Databricks recomenda isso para monorepos — sem sparse checkout, um repo grande pode estourar limites de memória/disco do Git folder e deixar as operações lentas.

**Configuração**:
1. No Git folder do workspace do cliente, ativar sparse checkout no momento da criação, com cone pattern = `datalake/_tech-sync`.
2. Sparse checkout **não pode ser desativado depois de ativado** (só o cone pattern pode mudar) — configure certo desde o início.
3. Deploy real via **Databricks Asset Bundles**: `datalake/_tech-sync/databricks.yml` na raiz da pasta sincronizada define o bundle (jobs, pipelines, targets `dev`/`prod`).
4. CI: workflow (GitHub Actions ou Azure Pipelines — template em `templates/ci-cd/`) que roda em push tocando `datalake/_tech-sync/`:
   - `databricks bundle validate`
   - a mesma validação do hook `validar_notebook.py` como gate
   - `databricks bundle deploy -t dev` em push para uma branch de desenvolvimento
   - `databricks bundle deploy -t prod` em merge para `main`, atrás de aprovação manual do ambiente

## Escolha de nuvem por projeto

A skill pergunta isso no kickoff (`02-processo-e-templates.md`) e o `scaffold_cliente.py` já cria só a estrutura relevante dentro de `_tech-sync/` (CSV de orquestração para Fabric, ou `databricks.yml`+`resources/` para Databricks) — não gera as duas ao mesmo tempo, para não confundir qual é a fonte de verdade real do projeto.

## Templates de pipeline

Ver `templates/ci-cd/databricks-deploy.yml` (GitHub Actions) e `templates/ci-cd/fabric-validate.yml` (GitHub Actions). Para Azure DevOps, a tradução é direta: os mesmos passos (`databricks bundle validate/deploy`, ou a validação Python) viram `steps:` de um `azure-pipelines.yml` com um `trigger: paths: include: [datalake/_tech-sync/*]`.
