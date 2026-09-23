# Power BI — Modelagem e DAX

Conduz a camada semântica (colunas calculadas, relacionamentos, tipos/formatação, limpeza) e as medidas DAX. Modelagem e DAX **não têm skill própria** — esta reference conduz, e a escrita no modelo acontece via **Power BI MCP em CLI interativo** (ver `references/07-mecanismos-e-hooks.md`, mecanismo M1 — escrita no modelo).

## Disciplina de camadas (o que resolver onde)

- **Enriquecimento de dado bruto → camada de dados (Silver/Gold)**, não no modelo. Coluna que exige lógica de negócio pesada ou reuso entre relatórios vive no notebook, não como coluna calculada DAX.
- **Coluna calculada DAX** só para o que é intrínseco ao modelo (ex.: ordenação de bloco, flag derivada de outras colunas do próprio modelo).
- **Não editar TMDL na mão.** Usar a ferramenta (Power BI MCP) ou produzir spec. Edição manual de TMDL corrompe/gera merge hell. A spec sobrevive ao refactor.
- Cada camada lê da anterior; proibido read inter-domínio na mesma camada (resumo derivado vem da origem bruta).

## Modelagem — checklist

1. **Fontes/partições:** Gold/Silver como origem; conferir M só onde precisa (evitar sweep).
2. **Tipos e formatação:** inteiro/decimal/data/texto corretos; `formatString` (moeda, %, `dd/mm/yy`); `summarizeBy: none` em colunas categóricas/códigos (evita somar código — erro comum).
3. **Relacionamentos:** cardinalidade e direção corretas; ativo/inativo; `dCalendário` como dimensão de data (role-playing quando houver múltiplas datas).
4. **Ocultar** colunas técnicas (`codigo_*`, chaves legadas) com `isHidden`.
5. **Coluna calculada** só quando necessária (ex.: `SWITCH` de ordenação); documentar no contrato.
6. **Limpeza** de medidas/tabelas legadas fica para **depois** do frontend (só se sabe o reuso com os visuais montados).

## Nomenclatura de medidas

Padrão: `Nome da Página - NN.N: Medida` (ex.: `Perfil Clientes - 03.0: % Ativos`). Grupos transversais em `displayFolder`: `Regras de Negócio`, `Geral`, `Cores`, `Custom Visuals`. Medidas HTML seguem `05-powerbi-frontend.md` (`[Categoria] NNN:`). Sem prefixo legado.

## DAX — princípios

- Medida por página conforme a spec; regras de negócio centralizadas em medidas `Regras de Negócio - *` reutilizadas (ex.: janela de atividade, base ativa).
- Variáveis semânticas (`VAR base_ativa = ...`), não `_x`. `DIVIDE` no lugar de `/` (trata div/0). `CALCULATE` + `FILTER` explícitos para janelas/segmentos.
- Formatação e cor de destaque em medidas próprias (`Cor *`) — reaproveitadas nos visuais HTML.
- Time intelligence sobre `dCalendário` marcada como tabela de datas.

## Aplicação no modelo (via MCP — resumo; detalhe em `references/07-mecanismos-e-hooks.md`)

- **Leitura** (`List`/`Get` de tabela/coluna/medida/relacionamento) roda na sessão normal → usar para inspeção e verificação.
- **Escrita** (`Create`/`Update`/`Rename`/`Delete`) e **`dax_query Execute`** exigem **CLI interativo com aprovação** (auto-recusam em SDK/headless). Preparar prompt determinístico (`runN_*.txt`) com os JSONs exatos; DAX longo em arquivo `.dax` cru para o CLI ler (evita inferno de escaping).

## Verificação (antes de fechar a fase)

Ler de volta pelo MCP: medida existe, `formatString`/`displayFolder` corretos, `summarizeBy` adequado; relacionamento com cardinalidade esperada; rodar `dax_query` de sanity (contagens batem, domínios válidos, nada no futuro, ordens de grandeza contra a Ata). Ver `references/07-mecanismos-e-hooks.md`, mecanismo M3 (verificação).

## Impacto de mudanças na camada de dados

Renomear/retipar coluna no Silver quebra: `sourceColumn` no TMDL (refresh falha) e bindings de visual. Antes de renomear, checar medidas/colunas/visuais que referenciam a coluna (via MCP `List` de medidas + busca no report). Preferir: repontar `sourceColumn` mantendo o nome de modelo, ou renomear modelo+visual juntos. Registrar no `PROJETO.md`.
