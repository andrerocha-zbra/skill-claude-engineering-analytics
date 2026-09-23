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
