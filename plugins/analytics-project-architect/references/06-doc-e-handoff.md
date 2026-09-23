# Documentação de Projeto Power BI (PBIP) e Handoff

Gera documentação descritiva de um modelo Power BI (formato PBIP) em duas formas complementares:
- **Markdown** versionável em Git — 5 arquivos (`00-overview` … `04-dependencias`).
- **HTML standalone** navegável — mini-site com sidebar fixa, busca client-side e syntax highlight de DAX.

A doc descreve **o que existe** no modelo (tabelas, colunas tipadas, medidas + DAX explicado em PT, relacionamentos, grafo de dependências). **Não audita qualidade.**

## Requisitos de execução (LER PRIMEIRO)

1. **Rodar em `claude` CLI interativo, com permissões no máximo.** A geração lê metadados do modelo e escreve arquivos em `_docs/` — precisa aprovação de tools.
2. **Projeto em formato PBIP** (pasta com `.SemanticModel/` e `.Report/`). Se só houver `.pbix`, instruir conversão antes e encerrar: *"Salva como Power BI Project: File → Save as → Power BI Project (.pbip). Avisa quando converter."*
3. **Instância viva do Power BI Desktop** com o modelo aberto, para o `powerbi-modeling-mcp` ler os metadados via conexão local.
4. **Regra de ouro de custo:** para cada informação necessária, escolha entre MCP e leitura de arquivo pelo que **gastar menos tokens**. Nunca varredura cega do PBIP.

## Procedimento token-eficiente (o coração desta reference)

O erro caro é ler todos os `.tmdl` de uma vez. Faça leitura dirigida.

### 1. Inventário via MCP (preferencial)

Use `powerbi-modeling-mcp` com chamadas alvo — `List` para enumerar, `Get` para detalhar, `ExportTMDL` só quando precisar do texto DAX/M cru:

- `model_operations` / `database_operations` → culture, compatibility level, autoDateTime, nome.
- `table_operations` (List) → nomes, tipos, contagem de colunas/medidas. **Excluir** `LocalDateTable_*` e `DateTableTemplate_*`.
- `column_operations` (por tabela, sob demanda) → tipo, papel, oculta/calculada.
- `measure_operations` → nome, expressão DAX, displayFolder, formatString, description.
- `relationship_operations` → from/to, cardinalidade, direção, ativo.
- `partition_operations` → resumo da fonte M (identificar Excel/SQL/Web/Sharepoint + paths pessoais).
- `dax_query_operations` → se precisar contagens agregadas (ex.: nº de linhas de um fato).

Puxe **só o que cada seção do output exige**. Ex.: para o overview basta `List` de tabelas/medidas/relacionamentos + config; não baixe DAX ainda.

### 2. Leitura seletiva de arquivos (fallback)

Se o MCP estiver indisponível, ou se um dado específico sair mais barato do disco, leia **apenas o `.tmdl`/`.json` exato** — nunca um sweep. Ex.: `SemanticModel/definition/tables/<Tabela>.tmdl` para uma tabela, ou `relationships.tmdl` para o mapa. Sempre absoluto, sempre pontual.

### 3. Derivar dependências

Cruze as expressões DAX (do passo 1) para montar: quem usa quem, medidas-raiz, lista reverse (impacto) e top tabelas referenciadas. Trabalhe sobre o inventário já em memória — não releia.

## Seções do output

| Arquivo / seção | Conteúdo |
|---|---|
| `00-overview` | Tagline do propósito (inferida), métricas-resumo (N tabelas/medidas/rel/colunas/tamanho), inventário 1-linha-por-tabela, fontes de dados (sinalizar paths pessoais), config do modelo. |
| `01-tabelas` | Por tabela: tagline, tipo (Fato/Dim/Medidas/Aux), origem, descrição, granularidade, colunas tipadas (Coluna/Tipo/Papel/Notas), source M resumido. Ordem: fato → dim → aux. |
| `02-medidas` | Agrupadas por displayFolder. Por medida: "O que faz" (business), DAX completo, "Como funciona" (técnico), Usa / É usada por. Ordem alfabética no grupo. |
| `03-relacionamentos` | Diagrama ASCII (simplificar se >10 tabelas), tabela detalhada (#/from/to/cardinalidade/direção/ativo/notas), 1 parágrafo descritivo. |
| `04-dependencias` | Árvore por medida-raiz, lista reverse (impacto de mudança), top 5 tabelas mais referenciadas. |
| `index.html` | Mini-site com todas as seções numa página navegável. |

Saída em `<raiz-PBIP>/_docs/`. Idempotente. Somente leitura sobre `.SemanticModel/` e `.Report/`; não commita nada.

## O que vai em cada arquivo (fonte da verdade de campos)

### `00-overview.md` — Sumário do modelo

**Propósito**: leitor abre, entende o modelo em 30 segundos.

**Conteúdo**:
1. **Cabeçalho**
   - Nome do projeto (`.pbip`)
   - Data/hora geração
   - Tagline 1-linha do propósito (inferido a partir das tabelas: "modelo de vendas com análise temporal YoY", "modelo financeiro com DRE consolidado", etc.)

2. **Métricas-resumo**
   - N tabelas reais (excluindo auto-date)
   - N medidas
   - N relacionamentos
   - N colunas totais
   - Tamanho do .pbip (estimado pela soma dos .tmdl)

3. **Inventário de tabelas** (1 linha por tabela)
   - Tabela | Tipo (Fato / Dimensão / Medidas / Aux) | N colunas | N medidas hospedadas | Source resumido

4. **Fontes de dados** (parsing das partições M)
   - Lista única de fontes (Excel, SQL, Web, Sharepoint, etc.)
   - Path/conexão resumida
   - **Sinalizar paths pessoais** (Google Drive, OneDrive, C:\Users\) com aviso visual

5. **Configurações relevantes do modelo**
   - Auto Date/Time (on/off)
   - Culture (pt-BR/en-US/...)
   - Compatibility level
   - Outras flags importantes

### `01-tabelas.md` — Catálogo de tabelas

**Propósito**: pra cada tabela do modelo, descreve papel + colunas tipadas.

**Conteúdo (por tabela)**:

```markdown
## {Nome da tabela}

> {Tagline em 1 linha — papel da tabela no modelo, granularidade}
> Tipo: {Fato | Dimensão | Tabela de medidas | Auxiliar}
> Origem: {fonte resumida — ex: Vendas.xlsx (PlanilhaVendas) via Excel.Workbook}

### Descrição
{1-2 parágrafos. Se a tabela tem `description:` declarado no TMDL, usar. Senão, inferir do nome + colunas + uso em medidas.}

### Granularidade
{1 linha = ?  — ex: "1 linha por item de NFe", "1 linha por dia"}

### Colunas

| Coluna | Tipo | Papel | Notas |
|---|---|---|---|
| `cdProduto` | int64 | Chave estrangeira → FotoProduto | — |
| `Data` | dateTime | Data da venda | — |
| ... |

**Papel** = um de: Chave primária / Chave estrangeira / Atributo / Métrica / Calculada
**Notas** = sinalizar coisas relevantes: oculta, calculada, com formato especial, etc.

### Medidas hospedadas (se for "tabela de medidas")
- {Lista linkada pras medidas em 02-medidas.md, agrupadas por displayFolder}

### Source M (resumo)
```m
let Fonte = ...
in #"...":
```
{Não copiar o M inteiro se for >15 linhas — resumir os passos relevantes}
```

**Ordem**: tabelas-fato primeiro, depois dimensões, depois auxiliares (parameter tables, measure tables).

### `02-medidas.md` — Catálogo de medidas

**Propósito**: pra cada medida, mostra DAX original + explicação PT.

**Estrutura**: agrupar por **displayFolder** (que existe no TMDL). Se medida não tem displayFolder, agrupar em "Sem pasta".

**Conteúdo (por medida)**:

```markdown
### {Nome da medida}

`{tabela host}.{medida}` · {formatString se relevante} · {displayFolder}

**O que faz:**
{1-3 frases em PT explicando o resultado da medida sem entrar em DAX. Foco no business meaning.}

**DAX:**
\`\`\`dax
{DAX original, formatado, sem comentários originais alterados}
\`\`\`

**Como funciona:**
{Explicação técnica em PT da lógica DAX. Se medida usa outras medidas, listar quais. Se usa funções time intelligence, explicar o contexto. Se tem CALCULATE, explicar o filter modifier.}

**Usa:** {lista de outras medidas/colunas referenciadas}
**É usada por:** {lista de medidas que dependem desta — preencher após processar todas}
```

**Ordem dentro de cada displayFolder**: alfabética.

**Tom**: explicação em PT deve ser **didática mas não condescendente**. Pra analista que sabe DAX, mas pode não conhecer o modelo específico.

### `03-relacionamentos.md` — Mapa de relacionamentos

**Propósito**: visualizar quem se relaciona com quem, com que cardinalidade.

**Conteúdo**:

#### Diagrama ASCII (texto)
```
                    ┌─────────────┐
                    │ dCalendario │
                    └──────┬──────┘
                           │ 1:N
                           ▼
       ┌──────────────┐  N  ┌─────────┐  N  ┌──────────────┐
       │ FotoVendedor │◄────│ fVendas │────►│ FotoProduto  │
       └──────────────┘     └─────────┘     └──────────────┘
                                    (bi-direcional ⚠)
```

(Se modelo tem >10 tabelas, simplificar pra showing só fato + dims principais.)

#### Tabela detalhada de relacionamentos

| # | From | To | Cardinalidade | Direção | Ativo | Notas |
|---|---|---|---|---|---|---|
| 1 | fVendas.cdProduto | FotoProduto.'Cod Produto' | N:1 | **Bothdirections** | ✓ | Bi-direcional |
| 2 | fVendas.Data | dCalendario.Data | N:1 | Single | ✓ | — |

**Notas** = sinalizar bi-direcionais, inativos, M:M, etc.

#### Análise rápida (1 parágrafo)
{Descrição em PT: "Modelo segue star schema com dCalendario como dimensão de tempo central. Apenas 1 fato (fVendas), 3 dimensões (Calendario, Produto, Vendedor). Único relacionamento bi-direcional é entre fVendas e FotoProduto — pode ser revisitado." Sem opinar (essa é função do review), só descrever.}

### `04-dependencias.md` — Grafo de dependências

**Propósito**: mostrar quem depende de quem entre as medidas. Ajuda no impacto de mudanças.

**Conteúdo**:

#### Árvore por medida-raiz

Identificar **medidas-raiz** (que não são usadas por nenhuma outra) e mostrar a árvore descendente.

```
% Faturamento YoY
└─ Faturamento
│  └─ fVendas[QtdItens]
│  └─ fVendas[PrecoUnitario]
└─ Referência Faturamento LY
   └─ Faturamento (já mapeada acima)
   └─ dCalendario[Data]
```

#### Lista reverse (impacto)

Pra cada medida **base** (usada por outras), listar quem depende.

```markdown
### Faturamento (base)

**Usada por:**
- Margem Bruta
- % Faturamento YoY
- Referência Faturamento LY
- Medida Selecionada

**Implicação:** mudar `Faturamento` afeta 4 outras medidas. Cuidado em refator.
```

#### Tabelas mais referenciadas

Top 5 tabelas mais usadas em medidas (sinaliza onde mora a "carne" do modelo).

## Regras transversais de conteúdo

**Tom**: PT-BR direto, sem jargão desnecessário, com personalidade (provocativo quando faz sentido, mas em doc é mais sóbrio que em revisão crítica de modelo).

**Acentuação**: SEMPRE com todos os acentos.

**Excluir auto-date**: tabelas `LocalDateTable_*` e `DateTableTemplate_*` **não entram** em nenhum dos 5 arquivos. Se modelo tem essas tabelas, mencionar **só** no overview ("o modelo tem Auto Date/Time ligado, gerando 2 tabelas-fantasma ocultas").

**Linkar entre arquivos**: usar links markdown relativos. Ex: em `02-medidas.md`, ao mencionar uma tabela, linkar pra `01-tabelas.md#nome-tabela`.

**Code blocks DAX**: usar fence ` ```dax ` pra sintaxe Markdown highlight (e o HTML aplica syntax highlight via classes `.k`, `.f`, `.s`, `.c`).

**Não inventar números**: se modelo tem 4.2M linhas em fVendas, isso vem do partition info — não inventar tamanho de dados. Se não há info, não citar.

**Não opinar**: esta reference descreve, não julga. Auditoria de qualidade do modelo (anti-patterns, bi-direcional desnecessário, etc.) é um exercício separado, fora do escopo desta reference.

## Geração do HTML (regra inviolável)

**Usar `templates/doc/relatorio.html` LITERAL.** Ele já traz todo o CSS (~600 linhas inline), HTML estrutural, tokens do design system e o JS de scroll-spy/busca/collapse.

- **Só substituir os placeholders `{{...}}`** pelos valores reais. Lista completa na seção "Placeholders do template HTML" abaixo (globais + blocos `{{..._HTML}}`).
- **Proibido:** trocar CSS, inventar cores fora dos tokens, mudar fontes, remover ornamentos, gerar HTML do zero, ou tocar em qualquer coisa dentro de `<!-- -->`, `<style>` ou `<script>`.
- **Encoding UTF-8 puro** — acentos e símbolos (`├ └ ─ → ↔ ⚠`) como caracteres reais, nunca mojibake (`Ã£`, `â`) nem entities. Mojibake quebra o parser: se acontecer, refazer.
- Cada medida vira um `<details class="measure-mini">` com name, DAX-essência, "O que faz", DAX completo (spans `.k .f .s .c`), "Como funciona", "É usada por".
- **Footer fixo obrigatório**, com o texto de marca vindo do placeholder `{{EMPRESA_FOOTER}}` — a marca da consultoria/plataforma nunca é hardcoded no template; se o projeto não tiver um `company-profiles/<empresa>/` configurado, usar um texto neutro tipo "Documentação gerada com Claude Code" no lugar do placeholder.

### Design tokens (resumo)

Vibe **editorial premium dark**, fundo `#0D0C0E`. Fontes: Bebas Neue + Barlow Condensed (display) · Outfit (body) · JetBrains Mono (código) — via Google Fonts CDN (única exceção ao inline). Cores: `--accent-glow #7099FF` (navegação/identificadores), `--accent-gold-bright #E8C9A0` (números/métricas). Badges: **Fato** magenta `#C47FFF`, **Dimensão** blue glow, **Medidas** gold, **Aux** muted. Highlight DAX: `.k` keyword, `.f` função/medida, `.s` string/número, `.c` comentário. O detalhamento completo vive no `<style>` do `relatorio.html` — não reescrever. Esse design system é um **default visual**, não uma identidade de marca fixa: pode ser trocado por outro caso o `company-profiles/<empresa>/` do projeto defina um próprio.

## Placeholders do `templates/doc/relatorio.html`

O template HTML usa estes placeholders `{{...}}` que devem ser substituídos com valores reais derivados dos `.tmdl`. Substituir **somente** no HTML — nunca dentro de comentários `<!-- -->`, `<style>` ou `<script>` (CSS, JS, comentários ficam intocados).

### Placeholders globais

| Placeholder | Conteúdo |
|---|---|
| `{{PROJECT_NAME}}` | Nome do projeto (ex: `16 - Comercial - Dashboard Vendas`) |
| `{{PROJECT_FILENAME}}` | Nome do arquivo `.pbip` |
| `{{TIMESTAMP}}` | Data de geração (ex: `26 abr 2026`) |
| `{{PROJECT_TAGLINE}}` | 1 frase descrevendo o propósito do modelo (inferido) |
| `{{PROJECT_HERO_SUB}}` | Subtítulo do hero (ex: `Modelo comercial · gerado em 26 abr 2026`) |
| `{{TABLES_COUNT}}`, `{{MEASURES_COUNT}}`, `{{RELATIONSHIPS_COUNT}}`, `{{COLUMNS_COUNT}}`, `{{SIZE}}` | Métricas inteiras |
| `{{EMPRESA_FOOTER}}` | Texto de marca do rodapé/título ("Doc gerada por {{EMPRESA}}") — vem de `company-profiles/<empresa>/`; se não configurado, usar texto neutro |

### Blocos HTML (gerados pelo Claude com base nos `.tmdl`)

| Placeholder | Conteúdo |
|---|---|
| `{{NAV_TABLES_HTML}}` | Sub-nav de tabelas (`<a>` com badges fato/dim/med/aux) |
| `{{NAV_MEASURES_HTML}}` | Sub-nav de pastas de medidas (`<a>` com counts) |
| `{{INVENTORY_TABLE_ROWS}}` | Linhas `<tr>` da tabela inventário |
| `{{DATA_SOURCES_TEXT}}` | Texto descritivo das fontes |
| `{{WARNINGS_HTML}}` | Callouts.warn pra problemas detectáveis (paths pessoais, etc.) — pode ser vazio |
| `{{CONFIG_LIST_HTML}}` | Items `<li>` da config-list (culture, compatibility, autoDateTime, etc.) |
| `{{TABLES_CARDS_HTML}}` | Todos os `<article class="table-card">` da seção 01 |
| `{{MEASURE_GROUPS_HTML}}` | Todos os `<div class="measure-group">` da seção 02 |
| `{{REL_SVG_HTML}}` | SVG inline do diagrama de relacionamentos (gerar dinâmico) |
| `{{REL_TABLE_ROWS}}` | Linhas `<tr>` da tabela de relacionamentos |
| `{{DEP_TREE_HTML}}` | Árvore de dependências (uma ou mais) |
| `{{DEP_REVERSE_HTML}}` | Cards reverse das medidas-base |
| `{{TOP_TABLES_LIST_HTML}}` | Items `<li>` com tabelas mais referenciadas |

### Padrão de cada `<details class="measure-mini">`

Todas as medidas seguem este shape — medidas-âncora têm classe `.anchor` + atributo `open`:

```html
<details class="measure-mini [anchor]" [open]>
  <summary>
    <span class="name">{Nome}</span>
    <span class="dax">{DAX-essência em 1 linha}</span>
    <span class="toggle">+</span>
  </summary>
  <div class="mini-body">
    <p class="meta">Tabela: <code>{tabela}</code> · Format: <code>{format}</code></p>
    <p class="desc"><strong>O que faz:</strong> {explicação business}</p>
    <pre class="code">{DAX completo com syntax highlight via spans .k .f .s .c}</pre>
    <div class="label">Como funciona</div>
    <p class="desc">{explicação técnica}</p>
    <div class="label">É usada por</div>
    <p class="measure-deps"><code>{outra-medida-1}</code> · <code>{outra-medida-2}</code></p>
  </div>
</details>
```

### Excluir tabelas auto-date

`LocalDateTable_*` e `DateTableTemplate_*` são auto-geradas pelo Power BI quando Auto Date/Time está ON — **não fazem parte da doc intencional**. Skipar.

## Templates de doc (em `templates/doc/`, herdados)

- `doc/00-overview.md` — esqueleto do sumário do modelo.
- `doc/01-tabelas.md` — catálogo de tabelas (colunas tipadas + source M).
- `doc/02-medidas.md` — catálogo de medidas por displayFolder.
- `doc/03-relacionamentos.md` — mapa de relacionamentos (ASCII + tabela + análise).
- `doc/04-dependencias.md` — grafo de dependências (árvores + reverse + top tabelas).
- `doc/relatorio.html` — template do mini-site (CSS/JS/tokens completos); usar literal, só preencher `{{...}}`.

## Handoff — quando a doc encerra uma fase

A geração de documentação normalmente coincide com o encerramento de uma frente de trabalho (fim da Fase 4/Frontend, entrega ao cliente, pausa prolongada). Nesse ponto, além da doc técnica em `_docs/`, gerar/atualizar o `HANDOFF.md` do domínio (template `templates/HANDOFF.md`, ver `02-processo-e-templates.md`) — ele é o resumo executivo "leia isto primeiro ao retomar", enquanto a doc em `_docs/` é o detalhamento técnico do modelo. Os dois se complementam: o `HANDOFF.md` linka para a doc gerada como um dos "arquivos de referência".
