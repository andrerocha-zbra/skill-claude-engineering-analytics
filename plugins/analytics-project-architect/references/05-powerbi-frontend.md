# Power BI Frontend (HTML/CSS/SVG/JS via DAX)

Método para construir qualquer visual customizado no Power BI usando medidas DAX que retornam HTML+CSS+SVG+JS, renderizadas pelo visual **"HTML Content"** (import do AppSource). O backend (modelo: tabelas, relacionamentos, medidas, regras) calcula; o frontend apenas **consome, formata e exibe**.

## Objetivo

Definir como projetar, questionar, especificar e implementar **qualquer tipo de visual customizado** para Power BI usando medidas DAX que retornam HTML+CSS+SVG+JS — de cards KPI simples a gráficos interativos complexos com JavaScript, tooltips e dados dinâmicos vindos do modelo semântico via DAX.

## Quando usar HTML vs. visual nativo

Usar HTML: cards KPI executivos, gráficos linha/barra/donut/heatmap customizados, tabelas com badges e cores condicionais, section headers, insight banners, empty states — qualquer visual com padrão premium acima do nativo.

Preferir **nativo**: cross-filter crítico com dado simples; drilldown/drillthrough nativo; dispersão/mapa/waterfall (custo de SVG manual alto); stacked com 12+ séries dinâmicas; **tabela que precisa exportar p/ Excel** (HTML não exporta).

## Mapa de decisão da técnica

```
Dados fixos / poucos itens (≤7)? → SVG puro em DAX (sem JS)   ex: heatmap 7 dias, gauge simples
Só layout + cor + badge?         → HTML/CSS puro              ex: KPI card, tabela, header, banner
Gráfico com N pontos dinâmicos?  → HTML + JS + SVG             ex: linha+barra, donut, barras horizontais
```

## Princípios fundamentais

1. **Separação backend/frontend.** O frontend não calcula — ele **consome**. Medidas, regras de negócio e relacionamentos ficam no backend (modelo semântico). O frontend apenas formata e exibe. Backend = tabelas, relacionamentos, medidas DAX, regras de negócio. Frontend = layout, hierarquia visual, cores, storytelling, interação.
2. **Código parametrizado.** Toda variável de design fica no topo da medida como `VAR`. Nunca hardcodar cores, tamanhos ou fontes dentro do HTML/CSS sem uma variável.
3. **Visual como produto.** Padrão esperado: interface madura com respiro visual, tipografia consistente, hover elegante, sombras discretas, leitura executiva imediata.
4. **DAX legível.** Nomes de variáveis semânticos e completos. Nunca `m001`, `f002`, `bg003`, `_vp`, `_cb`.

## Metodologia (antes de implementar)

**Sempre** executar este processo antes de implementar qualquer visual.

### Etapa 1 — Classificar

Antes de perguntar, inferir:
- É **estático** (card, header, tabela de regras) ou **iterativo** (lista de itens, ranking)?
- Precisa de **JS** (gráfico com cálculo de coordenadas, arc trigonométrico, N pontos variáveis)?
- Tem **granularidade** clara (por dia, por campanha, por forma de pagamento)?

### Etapa 2 — Perguntas mínimas obrigatórias

Antes de qualquer visual, confirmar:
1. **Título** do visual.
2. **Medidas e campos** que alimentam (quais measures do modelo?).
3. **Tipo:** card, gráfico, tabela, heatmap, outro?
4. **Interatividade:** tooltip/hover, ou estático?
5. **Protótipo existe?** → extrair funções JS do protótipo se disponível.

### Etapa 3 — Perguntas por categoria

| Tipo | Perguntas específicas |
|---|---|
| **KPI Card** | Valor principal? Comparativo MoM/YoY? Cor semáforo (verde/amarelo/vermelho)? Ícone? |
| **Linha+Barra** | Eixo temporal ou dimensional? Qual campo vai para barra vs linha? Quantidade de pontos (90 dias? 12 meses?)? |
| **Donut** | Quantas fatias? Quais medidas por fatia? Legenda ao lado ou abaixo? |
| **Barras horizontais** | Valores positivos apenas ou pode ter negativo (MoM)? Moeda ou número? Quantas barras? |
| **Heatmap** | Qual dimensão X? Qual métrica de intensidade? Quantos itens? |
| **Tabela** | Quais colunas? Ordenação? Limite de linhas? Badge de ação por linha? |

### Etapa 4 — Validar design

- Paleta: usar design system padrão do projeto (`@client_context/design-system/`) ou customizar?
- Fonte: Raleway (padrão desta reference) ou especificada pelo projeto?
- Tamanho disponível no canvas (largura × altura)?

## Estrutura obrigatória da medida (ordem de blocos)

Toda medida HTML segue esta ordem de blocos **sem exceção** — a ordem permite debugar em partes: cor errada → vai direto ao bloco de cores; dado errado → vai direto ao bloco de dados.

```dax
/* ── Layout ── */
VAR borda_card = "18px"
VAR padding_card = "16px"

/* ── Tipografia ── */
VAR fonte = "'Raleway','Segoe UI',SegoeUI,-apple-system,BlinkMacSystemFont,Arial,sans-serif"
VAR tamanho_titulo = "15px"
VAR tamanho_valor = "22px"
VAR tamanho_label = "12px"

/* ── Ícones ── */         -- quando aplicável
VAR icone_svg = "<svg ...>...</svg>"

/* ── Cores de superfície ── */
VAR cor_fundo_card = "#F8FBFB"

/* ── Cores de texto ── */
VAR cor_texto_titulo = "#1B3F6F"
VAR cor_texto_valor  = "#1B3F6F"
VAR cor_texto_label  = "#434343"

/* ── Cores de ícones ── */    -- quando aplicável
VAR cor_icone = "#1B3F6F"

/* ── Cores de variação ── */
VAR cor_positivo = "#54AF79"
VAR cor_negativo = "#CA6272"
VAR cor_neutro   = "#8A8A8A"

/* ── Gradientes ── */         -- quando aplicável

/* ── Sombras ── */
VAR sombra_padrao = "0 0 16px rgba(0,82,133,0.20)"
VAR sombra_hover  = "0 14px 28px rgba(15,23,42,0.12)"

/* ── Dados / Medidas ── */
VAR valor_principal = [Medida]
VAR variacao_mom    = [Variação MoM]

/* ── Formatação ── */
VAR valor_formatado = "R$ " & FORMAT(valor_principal / 1000, "#,##0.0") & "k"
VAR seta_direcao    = IF(variacao_mom >= 0, "▲", "▼")
VAR cor_variacao    = IF(variacao_mom >= 0, cor_positivo, cor_negativo)

/* ── Formatação → JSON ── */   -- apenas quando há JS
VAR json = "[" & CONCATENATEX(...) & "]"

/* ── Base iterativa ── */      -- apenas quando iterativo
VAR base_itens = ADDCOLUMNS(SUMMARIZE(...), ...)

/* ── CSS ── */                 -- apenas quando há JS
VAR css = "<style>...</style>"

/* ── SVGs ── */
VAR svg_icone = "<svg ...>...</svg>"

/* ── JS ── */                  -- apenas quando há JS
VAR js = "<script>(function(){ ... }());</script>"

/* ── Blocos HTML ── */
VAR card_html = "<div ...>...</div>"

RETURN card_html
```

Blocos "só quando" são omitidos em visuais HTML/CSS puro.

## Design system canônico

> **Client-agnóstico.** Os hex abaixo são o **default de fábrica** desta reference — um ponto de partida testado, não uma identidade fixa. Num projeto novo, ler `@client_context/design-system/` do cliente antes de aplicar; se o cliente tiver paleta própria, ela substitui a tabela abaixo por completo. As cores devem morar em medidas `[Cor ...]` na pasta `Custom Visuals\Configurações Gerais` — nunca hardcoded dentro do HTML/CSS de cada visual (editar 1 medida propaga a todos os visuais).

| Token | Hex | Uso |
|---|---|---|
| Primária | `#00A8E8` | linhas, destaques |
| Navy | `#1B3F6F` | títulos, valores |
| Teal | `#004D6B` | subtítulos, labels |
| Sucesso | `#54AF79` | positivo/pago |
| Aviso | `#DF9800` | atenção |
| Perigo | `#CA6272` | negativo/vencido |
| Texto | `#434343` | texto secundário |
| Eixo | `#476477` | labels de eixo SVG |
| Soft | `#DAF4FE` | fundo de barras/chips |
| Fundo card `#F8FBFB` · Fundo página `#F5F5F5` · Separador `#8A8A8A` | | |

```dax
/* Referências via medidas em Configurações Gerais — não hardcodar hex */
VAR cor_primaria   = [Cor Primaria]     /* #00A8E8 — azul principal — linhas, destaques */
VAR cor_navy       = [Cor Navy]         /* #1B3F6F — azul escuro — títulos, valores principais */
VAR cor_teal       = [Cor Teal]         /* #004D6B — azul-verde — subtítulos, labels ativos */
VAR cor_sucesso    = [Cor Sucesso]      /* #54AF79 — verde — positivo, pago, ok */
VAR cor_aviso      = [Cor Aviso]        /* #DF9800 — laranja — atenção, intermediário */
VAR cor_perigo     = [Cor Perigo]       /* #CA6272 — vermelho — alerta, negativo, vencido */
VAR cor_texto      = [Cor Texto]        /* #434343 — cinza escuro — texto secundário */
VAR cor_eixo       = [Cor Eixo]         /* #476477 — cinza azulado — labels de eixo SVG */
VAR cor_soft       = [Cor Soft]         /* #DAF4FE — azul claro — fundo de barras, chips */
VAR cor_fundo_card = [Cor Fundo Card]   /* #F8FBFB — quase branco — fundo de cards */
VAR cor_fundo_pag  = [Cor Fundo Pagina] /* #F5F5F5 — cinza claro — fundo da página */
VAR cor_separador  = [Cor Separador]    /* #8A8A8A — separadores, textos neutros */
```

**Tipografia** — fonte `'Raleway','Segoe UI',SegoeUI,-apple-system,BlinkMacSystemFont,Arial,sans-serif`.

| Elemento | Tamanho | Peso |
|---|---|---|
| Título de card | 15px | 700 |
| Valor KPI grande | 22–27px | 800 |
| Valor KPI médio | 18px | 700 |
| Label | 11–12px | 600 |
| Caption / badge | 11px | 600 |
| Eixo SVG | 10px | 400 |
| Título de seção | 32px | 700–800 |

**Sombras**
```dax
VAR sombra_padrao = "0 0 16px rgba(0,82,133,0.20)"    /* estado normal */
VAR sombra_hover  = "0 14px 28px rgba(15,23,42,0.12)" /* hover elevado */
```
Hover sempre acompanhado de `transition: transform .22s ease, box-shadow .22s ease` e `transform: translateY(-4px)`.

**Bordas**
```dax
VAR borda_card    = "18px"   /* cards principais */
VAR borda_bloco   = "16px"   /* blocos internos */
VAR borda_metrica = "14px"   /* métricas pequenas */
VAR borda_badge   = "12px"   /* badges/pills */
VAR borda_chip    = "999px"  /* chips completamente arredondados */
```

## Regras críticas de escaping DAX (errar quebra silenciosamente)

Esta é a seção mais importante para HTML+JS via DAX.

### Regra 1 — JSON sempre com aspas simples

**❌ ERRADO** — `""` em DAX é delimitador de string, não aspas duplas literais:
```dax
VAR json = "[{""name"":""Boleto"",""value"":1234}]"
-- Output: [{"name":"Boleto","value":1234}]  -- parece certo mas...
-- ...DAX trata "" como " e fecha/abre a string DAX em lugares errados
```

**✅ CORRETO** — aspas simples são literais em DAX sem escaping:
```dax
VAR json = "[{'name':'Boleto','value':1234}]"
-- Output: [{'name':'Boleto','value':1234}]  -- válido como JS object literal
```

### Regra 2 — Decimal pt-BR → JSON

`FORMAT` em pt-BR usa `,` como decimal. JSON precisa de `.`:
```dax
-- ❌ Errado: "1234,56" → erro de sintaxe JS
VAR v = FORMAT([Medida], "0.00")

-- ✅ Correto: "1234.56" → número válido em JS
VAR v = SUBSTITUTE(FORMAT([Medida], "0.00"), ",", ".")
```
Para valores sem decimal (inteiros): `FORMAT([Medida], "0")` — não adiciona separador de milhar com este formato, sem problema.

### Regra 3 — Data: MM maiúsculo para mês

```dax
-- ❌ ERRADO: "dd/mm" → mm = minutos em DAX FORMAT → "08/00"
FORMAT('dCalendário'[Data], "dd/mm")

-- ✅ CORRETO: "dd/MM" → MM = mês
FORMAT('dCalendário'[Data], "dd/MM")
```

### Regra 4 — Template literals JS (backtick) funcionam em DAX

O backtick `` ` `` não tem significado especial em DAX — é um caractere literal. Template literals JS ficam intactos:
```dax
VAR js = "<script>
  var label = `${r.label}: ${brl(r.value)}`;
  el.innerHTML = `<rect x='${x}' y='${y}'/>`;
</script>"
-- Os backticks e ${} são preservados literalmente → JS os processa corretamente
```

### Regra 5 — Atributos SVG/HTML sempre com aspas simples

```dax
-- ✅ Usar aspas simples nos atributos dentro da string DAX
VAR svg = "<rect x='10' y='20' fill='#00A8E8'/>"
VAR div = "<div class='card' style='color:#fff'>"

-- ❌ Evitar aspas duplas (precisam de "" e ficam ilegíveis)
VAR svg = "<rect x=""10"" y=""20"" fill=""#00A8E8""/>"
```

### Regra 6 — `"` literal no output HTML

Quando o HTML gerado DEVE conter `"` (raro, mas ocorre em atributos especiais):
```dax
VAR html = "<div data-value=""42"">texto</div>"
-- DAX string: "" → output: "  → HTML: data-value="42"
```

**Nunca** usar `\` para escapar `'` (vira `\` literal no JS). **Nunca** `JSON.parse` (usar object literal direto).

### Tabela resumo

| Quero no output | Escrever na string DAX |
|---|---|
| `{'k':'v'}` JSON/JS object | `"{'k':'v'}"` — **aspas simples** (`""` é delimitador DAX, quebra a string) |
| `1234.56` número JSON | `SUBSTITUTE(FORMAT(val,"0.00"),",",".")` — pt-BR usa `,` como decimal |
| `dd/MM` data (mês) | `FORMAT(data,"dd/MM")` — **MM maiúsculo** (`mm` = minutos) |
| `` `${expr}` `` template literal JS | `` "`${expr}`" `` — backtick é literal em DAX, funciona |
| `fill='#fff'` atributo SVG/HTML | `"fill='#fff'"` — sempre aspas simples nos atributos |
| `"` literal no HTML (raro) | `""` (doubled) na string DAX |

## Padrões por tipo de visual

### KPI Card (HTML/CSS puro — sem JS)

**Quando usar:** 1 a 6 cards com valor, variação MoM e badge de status. `.card` > `.label` (título uppercase) + `.value` + `.delta` (dot colorido + seta ▲/▼ + % MoM).

```html
<div class='card'>
  <div class='label'>TÍTULO</div>
  <div class='value'>R$ 1.234k</div>
  <div class='delta'>
    <span class='dot' style='background:#54AF79'></span>
    ▲ 5.2% MoM
  </div>
</div>
```

CSS-chave: `.kpi{background;border-radius:18px;box-shadow;padding;flex:1;position:relative;overflow:hidden;min-height:130px;transition:transform .22s,box-shadow .22s}` `.kpi:hover{transform:translateY(-4px);box-shadow:hover}` `.kpi::after{...border-radius:50%}` (bolha decorativa).

Template DAX completo:
```dax
Bullets 001: Valor Emitido =

/* ── Layout ── */
VAR borda_card   = "18px"
VAR padding_card = "18px 20px 16px"
/* ── Tipografia ── */
VAR fonte = "'Raleway','Segoe UI',SegoeUI,-apple-system,BlinkMacSystemFont,Arial,sans-serif"
/* ── Cores de superfície ── */
VAR cor_fundo_card = "#F8FBFB"
/* ── Cores de texto ── */
VAR cor_texto_label    = "#434343"
VAR cor_texto_valor    = "#1B3F6F"
VAR cor_texto_subtitulo = "#004D6B"
/* ── Cores de variação ── */
VAR cor_positivo = "#54AF79"
VAR cor_negativo = "#CA6272"
VAR cor_primaria = "#00A8E8"
/* ── Sombras ── */
VAR sombra_padrao = "0 0 16px rgba(0,82,133,0.20)"
VAR sombra_hover  = "0 14px 28px rgba(15,23,42,0.12)"
/* ── Dados / Medidas ── */
VAR valor_principal  = [SUA_MEDIDA]
VAR variacao_mom     = [SUA_VARIACAO_MOM]
/* ── Formatação ── */
VAR valor_formatado  = "R$ " & FORMAT(valor_principal / 1000, "#,##0.0") & "k"
VAR variacao_formatada = FORMAT(ABS(variacao_mom), "0.0%")
VAR seta_direcao     = IF(variacao_mom >= 0, "▲", "▼")
VAR cor_badge        = IF(variacao_mom >= 0, cor_positivo, cor_negativo)
/* ── CSS ── */
VAR css_cards = "<style>.krow{display:flex;gap:12px;width:100%;font-family:" & fonte & "}.kpi{background:" & cor_fundo_card & ";border-radius:" & borda_card & ";box-shadow:" & sombra_padrao & ";padding:" & padding_card & ";flex:1;position:relative;overflow:hidden;min-height:130px;transition:transform .22s,box-shadow .22s}.kpi:hover{transform:translateY(-4px);box-shadow:" & sombra_hover & "}.kpi::after{content:'';position:absolute;right:-30px;top:-30px;width:100px;height:100px;border-radius:50%;background:rgba(218,244,254,.92)}.ki-label{color:" & cor_texto_label & ";font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.4px}.ki-val{color:" & cor_texto_valor & ";font-size:22px;font-weight:800;margin:10px 0 6px;line-height:1}.ki-badge{display:inline-flex;align-items:center;gap:3px;font-size:11px;font-weight:600}.ki-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:4px}</style>"
/* ── Blocos HTML ── */
VAR card_html = "<div class='kpi'><div class='ki-label'>SEU TÍTULO</div><div class='ki-val'>" & valor_formatado & "</div><div class='ki-badge' style='color:" & cor_badge & "'><span class='ki-dot' style='background:" & cor_primaria & "'></span>" & seta_direcao & " " & variacao_formatada & " MoM</div></div>"
RETURN css_cards & "<div class='krow'>" & card_html & "</div>"
```

### Tabela com badges (HTML/CSS puro — sem JS)

**Quando usar:** ranking, top N, piores dias, comparativos — com badges de ação. `<td>` com pill `padding:4px 8px;border-radius:12px;background:rgba(218,244,254,.55)` contendo dot colorido + texto.

```dax
VAR linha = "<tr>"
    & "<td>" & [campo] & "</td>"
    & "<td style='font-weight:700;color:#1B3F6F'>R$ " & FORMAT([valor]/1000,"#,##0.0") & "k</td>"
    & "<td><span style='font-weight:700;color:" & cor & "'>" & FORMAT([pct],"0.0%") & "</span></td>"
    & "<td><span style='display:inline-flex;align-items:center;gap:5px;padding:4px 8px;border-radius:12px;background:rgba(218,244,254,.55);color:#004D6B;font-weight:600;font-size:11px'>"
    & "<span style='width:7px;height:7px;border-radius:50%;background:" & cor & ";display:inline-block'></span>"
    & acao & "</span></td>"
    & "</tr>"
```

CSS: `table{border-collapse:collapse}` `th{color:#004D6B;font-weight:700;border-bottom:1.5px solid rgba(0,77,107,.15)}` `tr:hover td{background:rgba(218,244,254,.35)}`.

### Gráfico Linha + Barra (JS+SVG)

**Quando usar:** série temporal com 2 métricas — uma como barra (volume) e outra como linha (realizado). Dados → JSON via `TOPN(90, FILTER(SUMMARIZE('dCalendário',[Data]), NOT ISBLANK([Medida])), [Data], DESC)` + `ADDCOLUMNS` (`@e` barra, `@p` linha, `@l` label `dd/MM`) → `CONCATENATEX` com `{'label':...,'e':...,'p':...}`.

```dax
VAR base = ADDCOLUMNS(
    TOPN(90, FILTER(SUMMARIZE('dCalendário','dCalendário'[Data]), NOT ISBLANK([Medida])), 'dCalendário'[Data], DESC),
    "@e", [MedidaBarra],
    "@p", [MedidaLinha],
    "@l", FORMAT('dCalendário'[Data], "dd/MM")
)
VAR json = "[" & CONCATENATEX(
    base,
    "{'label':'" & [@l] & "','e':" & SUBSTITUTE(FORMAT([@e],"0.00"),",",".") & ",'p':" & SUBSTITUTE(FORMAT([@p],"0.00"),",",".") & "}",
    ",",
    'dCalendário'[Data], ASC
) & "]"
```

Função JS (extraída e adaptada — usar como está):
```javascript
(function(){
  var tip = document.getElementById('tp');
  var sT = function(h,e){ tip.innerHTML=h; tip.style.left=(e.clientX+14)+'px'; tip.style.top=(e.clientY+14)+'px'; tip.style.opacity=1; };
  var hT = function(){ tip.style.opacity=0; };
  var bT = function(el){ el.querySelectorAll('[data-tip]').forEach(function(n){ n.addEventListener('mousemove',function(e){sT(n.dataset.tip,e)}); n.addEventListener('mouseleave',hT); }); };
  var brl = function(v){ return isNaN(v) ? 'R$ 0' : v.toLocaleString('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0}); };
  var data = DATA_JSON; /* substituído pelo & json & */
  var el = document.getElementById('ch'); if(!el) return;
  var w=900, h=330, pl=52, pr=18, pt=20, pb=42;
  var maxY = Math.max.apply(null, data.map(function(r){ return Math.max(r.e||0,r.p||0); }).concat([1])) * 1.18;
  var X = function(i){ return pl + (i/(data.length-1||1))*(w-pl-pr); };
  var Y = function(v){ return h-pb-(v/maxY)*(h-pt-pb); };
  var pts = data.map(function(r,i){ return X(i)+','+Y(r.p); }).join(' ');
  var barW = Math.max(3,(w-pl-pr)/data.length*0.55);
  var bars = data.map(function(r,i){
    return `<rect x='${X(i)-barW/2}' y='${Y(r.e)}' width='${barW}' height='${Math.max(0,h-pb-Y(r.e))}' rx='4' fill='COR_BARRA' opacity='.78' data-tip='${r.label} | ${brl(r.e)}'/>`;
  }).join('');
  var ticks = [0,.25,.5,.75,1].map(function(t){
    return `<line stroke='rgba(0,77,107,.18)' x1='${pl}' x2='${w-pr}' y1='${Y(maxY*t)}' y2='${Y(maxY*t)}'/><text x='8' y='${Y(maxY*t)+4}' fill='#476477' font-size='10'>${brl(maxY*t)}</text>`;
  }).join('');
  var step = Math.ceil(data.length/8);
  var labels = data.filter(function(_,i){ return i%step===0; }).map(function(r){ var idx=data.indexOf(r); return `<text x='${X(idx)-14}' y='${h-16}' fill='#476477' font-size='10'>${r.label}</text>`; }).join('');
  var circles = data.map(function(r,i){ return `<circle cx='${X(i)}' cy='${Y(r.p)}' r='4' fill='COR_LINHA' data-tip='${r.label} | ${brl(r.p)}'/>` }).join('');
  el.innerHTML = `<svg viewBox='0 0 ${w} ${h}'>${ticks}${bars}<polyline points='${pts}' fill='none' stroke='COR_LINHA' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/>${circles}${labels}</svg>`;
  bT(el);
}());
```
**Substituir:** `COR_BARRA` (ex: `#DAF4FE`), `COR_LINHA` (ex: `#00A8E8`), `DATA_JSON` pelo `& json &`.

### Donut (JS+SVG) — NUNCA usar `stroke-dasharray`

`stroke-dasharray` não divide corretamente as fatias com múltiplos segmentos. Técnica correta: **arc path trigonométrico**. Cada fatia acumula ângulo (offset `-π/2` começa no topo); `large-arc-flag=1` se fatia > π:

```javascript
var total = rows.reduce(function(a,b){ return a+b.value; }, 0) || 1;
var acc = 0;
var R=76, cx=105, cy=105;
var segs = rows.map(function(r,i){
  var a0 = acc/total * 2*Math.PI - Math.PI/2; /* ângulo início — offset -π/2 para começar no topo */
  acc += r.value;
  var a1 = acc/total * 2*Math.PI - Math.PI/2; /* ângulo fim */
  var large = a1-a0 > Math.PI ? 1 : 0;        /* arc-flag: 1 se fatia > 180° */
  var x0=cx+R*Math.cos(a0), y0=cy+R*Math.sin(a0);
  var x1=cx+R*Math.cos(a1), y1=cy+R*Math.sin(a1);
  /* M=mover para centro, L=linha ao perímetro, A=arco, Z=fechar */
  return `<path d='M ${cx} ${cy} L ${x0.toFixed(2)} ${y0.toFixed(2)} A ${R} ${R} 0 ${large} 1 ${x1.toFixed(2)} ${y1.toFixed(2)} Z' fill='${cores[i%cores.length]}' data-tip='${r.name}: ${brl(r.value)}'/>`;
}).join('');
/* Buraco central — círculo por cima */
var centro = `<circle cx='${cx}' cy='${cy}' r='48' fill='#F8FBFB'/>`;
/* Texto central — maior fatia */
var pct_maior = ((rows[0].value/total)*100).toFixed(1)+'%';
var texto = `<text x='${cx}' y='${cy-4}' text-anchor='middle' fill='#1B3F6F' font-size='17' font-weight='800'>${pct_maior}</text><text x='${cx}' y='${cy+16}' text-anchor='middle' fill='#434343' font-size='10'>maior fatia</text>`;
el.innerHTML = `<svg viewBox='0 0 210 210' width='200' height='200'>${segs}${centro}${texto}</svg>`;
```

Dados → JSON para donut:
```dax
/* Para fatias com CALCULATE por campo de filtro: */
VAR json = "["
    & "{'name':'Nome A','value':" & SUBSTITUTE(FORMAT(val_a,"0.00"),",",".") & "}"
    & ",{'name':'Nome B','value':" & SUBSTITUTE(FORMAT(val_b,"0.00"),",",".") & "}"
    & "]"

/* Para fatias de SUMMARIZE iterativo: */
VAR base = ADDCOLUMNS(SUMMARIZE(tabela, tabela[campo]), "@v", [Medida])
VAR json = "[" & CONCATENATEX(base, "{'name':'" & tabela[campo] & "','value':" & SUBSTITUTE(FORMAT([@v],"0.00"),",",".") & "}", ",", [@v], DESC) & "]"
```

Legenda ao lado (HTML, flex space-between, dot + nome + valor):
```javascript
var lg = document.getElementById('lg');
if(lg) lg.innerHTML = rows.map(function(r,i){
  return `<div style='display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:11px;color:#434343;margin-bottom:6px'><span><span style='display:inline-block;width:10px;height:10px;border-radius:50%;background:${cores[i%cores.length]};margin-right:4px'></span>${r.name}</span><strong>${brl(r.value)}</strong></div>`;
}).join('');
```

SVG precisa de `overflow:visible` (fatias próximas à borda são cortadas sem isso).

### Barras horizontais (JS+SVG)

**Quando usar:** ranking, funil, aging, MoM por categoria.

```javascript
var w=760, h=270, pl=120, pr=22, pt=20, pb=30;
var max = Math.max.apply(null, rows.map(function(r){ return Math.abs(r.value); }).concat([1])) * 1.15;
el.innerHTML = `<svg viewBox='0 0 ${w} ${h}'>` + rows.map(function(r,i){
  var yp = pt + i*((h-pt-pb)/rows.length) + 8;
  var bw = (Math.abs(r.value)/max)*(w-pl-pr);
  var col = r.color || cores[i%cores.length];
  /* Para MoM com negativos: */
  var lbl = r.value < 0 ? '-'+Math.abs(r.value).toFixed(1)+'%' : '+'+r.value.toFixed(1)+'%';
  /* Para quantidades/valores: */
  var lbl2 = num(r.value); /* ou brl(r.value) para monetário */
  return `<text x='8' y='${yp+18}' fill='#476477' font-size='13' font-weight='600'>${r.name}</text>`+
         `<rect x='${pl}' y='${yp}' height='24' width='${bw}' rx='12' fill='${col}' data-tip='${r.name}: ${lbl2}'/>`+
         `<text x='${pl+bw+8}' y='${yp+17}' fill='#476477' font-size='12'>${lbl2}</text>`;
}).join('') + `</svg>`;
```

**Regra `rx='12'` (pill):** padrão para barras horizontais. Nunca `rx='0'`. **Para MoM (valores negativos):** usar `Math.abs(r.value)` para largura; cor por sinal vinda do JSON (`r.color`).

### Heatmap (SVG puro em DAX — sem JS para ≤7 itens fixos)

**Quando usar SVG puro (sem JS):** 7 dias da semana, 12 meses fixos — qualquer conjunto pequeno e conhecido. **Quando usar JS:** dados completamente dinâmicos (N itens variáveis, sem número fixo).

```dax
VAR c1 = CALCULATE([Metrica], FILTER('dCalendário', WEEKDAY('dCalendário'[Data],2)=1)) /* Seg */
VAR c2 = CALCULATE([Metrica], FILTER('dCalendário', WEEKDAY('dCalendário'[Data],2)=2)) /* Ter */
/* ... 7 variáveis ... */
VAR max_c = MAXX({c1,c2,c3,c4,c5,c6,c7}, [Value])
VAR safe = IF(max_c = 0 || ISBLANK(max_c), 1, max_c)
VAR i1 = 0.18 + 0.72 * DIVIDE(IF(ISBLANK(c1),0,c1), safe) /* intensidade 18%–90% */
/* ... 7 intensidades ... */

/* Barra por dia: x = 30 + i*78 (para 7 barras em 580px) */
VAR bar1 = "<rect x='30' y='40' width='56' height='130' rx='18' fill='#00A8E8' opacity='" & FORMAT(i1,"0.00") & "'/>"
          & "<text x='58' y='190' text-anchor='middle' fill='#476477' font-size='11'>Seg</text>"
          & "<text x='58' y='110' text-anchor='middle' fill='" & IF(i1>0.55,"#fff","#1B3F6F") & "' font-weight='800' font-size='13'>" & FORMAT(IF(ISBLANK(c1),0,c1),"0%") & "</text>"
/* ... 7 barras ... */

VAR svg = "<svg viewBox='0 0 580 220' style='width:100%;height:auto'>" & bar1 & bar2 & bar3 & bar4 & bar5 & bar6 & bar7 & "</svg>"
```

**Intensidade:** `0.18` = mínimo visível, `0.90` = máximo. Texto branco quando `intensity > 0.55`.

### Section header / Insight / Empty state (HTML/CSS puro)

**Section Header:**
```dax
VAR header = "<div style='display:flex;align-items:center;gap:14px;margin-bottom:18px'>"
    & "<div style='width:52px;height:52px;border-radius:14px;background:rgba(0,168,232,.12);display:flex;align-items:center;justify-content:center'>" & icone_svg & "</div>"
    & "<div><div style='font-size:24px;font-weight:800;color:#1B3F6F;line-height:1'>" & titulo & "</div>"
    & "<div style='font-size:13px;font-weight:500;color:#004D6B;margin-top:4px'>" & subtitulo & "</div></div>"
    & "</div>"
```

**Insight Card:**
```dax
VAR insight = "<div style='background:#F8FBFB;border-radius:16px;box-shadow:0 0 16px rgba(0,82,133,.20);padding:16px'>"
    & "<h3 style='color:#1B3F6F;font-size:15px;margin:0 0 8px;font-family:Raleway,sans-serif'>" & titulo_insight & "</h3>"
    & "<p style='color:#434343;font-size:12px;line-height:1.6;margin:0'>" & texto_insight & "</p>"
    & "</div>"
```

**Empty State** (quando dado é `BLANK`):
```dax
VAR empty_state = IF(
    ISBLANK([Medida]),
    "<div style='display:flex;flex-direction:column;align-items:center;justify-content:center;height:200px;color:#8A8A8A;font-family:Raleway,sans-serif'>"
    & "<svg width='48' height='48' viewBox='0 0 24 24' fill='none' stroke='#DAF4FE' stroke-width='1.5'><circle cx='12' cy='12' r='10'/><path d='M12 8v4m0 4h.01'/></svg>"
    & "<p style='margin:12px 0 0;font-size:13px'>Sem dados para o período selecionado</p>"
    & "</div>",
    conteudo_normal
)
```
Sempre tratar com `IF(ISBLANK(val),0,val)` antes de formatar.

## Tooltip padrão (todo visual com JS)

CSS (dentro do `<style>`):
```css
.tp { position:fixed; background:#1B3F6F; color:#fff; padding:6px 10px; border-radius:8px;
      font-size:11px; font-family:'Raleway',sans-serif; pointer-events:none;
      opacity:0; transition:opacity .12s; z-index:9999; white-space:nowrap; }
```
**`position:fixed`** — `absolute` não segue o cursor.

HTML (no skeleton): `<div id='tp' class='tp'></div>`.

JS (IIFE pattern — copiar exatamente):
```javascript
var tip = document.getElementById('tp');
var sT = function(h,e){ tip.innerHTML=h; tip.style.left=(e.clientX+14)+'px'; tip.style.top=(e.clientY+14)+'px'; tip.style.opacity=1; };
var hT = function(){ tip.style.opacity=0; };
var bT = function(el){ el.querySelectorAll('[data-tip]').forEach(function(n){ n.addEventListener('mousemove',function(e){sT(n.dataset.tip,e)}); n.addEventListener('mouseleave',hT); }); };
```

**Uso:** adicionar `data-tip='texto do tooltip'` em qualquer elemento SVG (`<rect>`, `<circle>`, `<path>`). Chamar `bT(el)` **após** `el.innerHTML = svg`. Cada visual roda em iframe isolado → `getElementById('tp')` não conflita entre visuais.

## Helpers JS reutilizáveis

Copiar no início de qualquer IIFE que precise:
```javascript
var brl = function(v){ return isNaN(v)||v===null ? 'R$ 0' : v.toLocaleString('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0}); };
var num = function(v){ return isNaN(v) ? '0' : Math.round(v).toLocaleString('pt-BR'); };
var pct = function(v){ return (v*100).toFixed(1)+'%'; };
```

## O que fazer e não fazer

### ✅ Fazer

- `{'key':'val'}` — aspas simples no JSON/JS objects dentro de strings DAX.
- `SUBSTITUTE(FORMAT(val,"0.00"),",",".")` — decimal correto para JSON.
- `FORMAT(data,"dd/MM")` — MM maiúsculo para mês (não `mm`).
- Backticks `` ` `` em template literals JS — são literais em DAX, funcionam.
- `(function(){ ... }())` — IIFE para isolar escopo JS.
- `svg{width:100%;height:auto}` + `viewBox='0 0 W H'` — SVG responsivo.
- `<rect rx='12'>` — pill shape para barras horizontais.
- `<polyline stroke-linecap='round' stroke-linejoin='round'>` — linha suave.
- `toFixed(2)` nas coordenadas de arc path — evita strings gigantes.
- `if(!el) return;` — verificar elemento antes de usar `getElementById`.
- `bT(el)` após `el.innerHTML = ...` — ativar tooltips.
- Tooltip com `position:fixed` — segue o cursor corretamente.
- Buraco do donut com `<circle fill=cor_fundo>` — mais limpo que `stroke-width` gigante.
- Heatmap com SVG puro quando ≤7 itens — evita JS desnecessário.
- Separar `@e` (barra) e `@p` (linha) no JSON — nomes curtos mas distintos.
- IIFE com `var` (não `const`/`let`) para máxima compatibilidade.
- Nomes de VAR DAX **semânticos e completos** (`variacao_percentual`, `cor_badge`) — nunca `_vp`, `m001`. Design todo em VAR no topo; nada hardcoded no meio do CSS.

### ❌ Não fazer

- `{"key":"val"}` — `""` em DAX quebra a string silenciosamente.
- `stroke-dasharray` para donut multi-fatia — divisão incorreta garantida.
- `"dd/mm"` — `mm` são minutos em DAX `FORMAT`, não mês.
- `\` para escapar `'` dentro de string DAX — produz `\` literal no JS.
- `JSON.parse(string)` — desnecessário; usar object literal JS diretamente.
- `position:absolute` no tooltip — não segue o cursor corretamente.
- SVG sem `overflow:visible` no donut — fatias próximas à borda são cortadas.
- `Math.abs()` esquecido em valores negativos para largura de `<rect>` — erro de render.
- Variáveis de design hardcoded no CSS sem VAR no topo da medida.
- Nomes de variáveis genéricos: `_c1`, `_f2`, `_b3` — use nomes semânticos.
- Fontes diferentes em visuais da mesma página — sempre a fonte do design system.
- `border-radius` diferente do padrão do card sem motivo específico.
- CSS duplicado — extrair para variável DAX e reutilizar com `& variavel &`.
- Ignorar `ISBLANK()` nos valores — sempre tratar com `IF(ISBLANK(val),0,val)`.
- Usar `""` (doubled) para atributos HTML dentro do JS — usar `'` sempre.

## Nomenclatura de medidas HTML

**Padrão obrigatório:** `[Categoria] [NNN]: [Descrição]` — `[Categoria]` é o grupo funcional (`Geral`, `Bullets`, `Gráficos`, `Tabelas`, `Heatmap`); `[NNN]` é sequencial **dentro da categoria** (001, 002, ...); `[Descrição]` é o nome direto do visual, sem prefixo redundante.

```
Geral 001: Cards KPI Principais       ← row com todos os KPIs
Geral 002: Card Valor Emitido         ← card individual (exemplo de uso)
Bullets 001: Valor Emitido            ← bullet standalone
Bullets 002: Valor Pago
Gráficos 001: Vencimentos Diários     ← gráfico line+bar
Tabelas 001: Top Campanhas            ← tabela com badges
Heatmap 001: Conversão por Dia da Semana
```

**UDF/utilitários** seguem prefixo próprio: `UDF 000: CSS Cards KPI` (CSS compartilhado), `UDF 001: Card KPI Template` (template de card).

### Nomenclatura de variáveis DAX dentro da medida

**Regra crítica: nunca usar nomes abreviados.** Variáveis são documentação viva — devem ser legíveis sem contexto.

❌ ERRADO: `_vp`, `_cb`, `_st`, `_bom`, `_pos`, `_neg`, `_f`
✅ CORRETO: `variacao_percentual`, `cor_badge`, `seta_direcao`, `crescimento_e_bom`, `cor_positivo`, `cor_negativo`, `fonte`

| Padrão | Exemplo |
|---|---|
| Dado bruto | `valor_pago`, `qtd_emitidos`, `taxa_conversao` |
| Formatado | `valor_pago_formatado`, `variacao_formatada` |
| Variação | `variacao_percentual`, `variacao_mom_pago`, `variacao_yoy_emitido` |
| Cor | `cor_badge`, `cor_positivo`, `cor_negativo`, `cor_semaforo_conversao` |
| Direção / seta | `seta_direcao` |
| Período | `label_periodo` |
| Flag booleana | `crescimento_e_bom` |
| HTML parcial | `badge_variacao_html`, `badge_subtitulo_html`, `badge_html` |
| HTML de card | `card_valor_pago_html`, `linha_campanha_html` |
| Base iterativa | `base_campanhas`, `base_dias`, `base_meses` |
| JSON | `json`, `json_fatias`, `json_barras` |

## Catálogo de componentes

| Componente | Técnica | JS? | Tooltip? |
|---|---|---|---|
| KPI Cards (N cards em row) | HTML/CSS | Não | Não |
| Section Header (ícone+título) | HTML/CSS | Não | Não |
| Insight Card / Banner | HTML/CSS | Não | Não |
| Empty State | HTML/CSS/SVG | Não | Não |
| Tabela com badges | HTML/CSS | Não | Não |
| Ranking com variação | HTML/CSS | Não | Não |
| Gráfico Linha+Barra | JS+SVG | Sim | Sim |
| Donut (N fatias) | JS+SVG | Sim | Sim |
| Barras horizontais | JS+SVG | Sim | Sim |
| Barras verticais agrupadas | JS+SVG | Sim | Sim |
| Heatmap (≤7 itens) | SVG puro DAX | Não | Não |
| Heatmap (N dinâmico) | JS+SVG | Sim | Sim |
| Gauge / Progresso | SVG puro DAX | Não | Não |

## Template genérico copy-paste

### Template A — Visual com JS + dados tabulares

```dax
Gráficos 001: Vencimentos Diários =

/* ── Dados / Medidas ── */
VAR dias_filtrados = FILTER(SUMMARIZE('dCalendário','dCalendário'[Data]), NOT ISBLANK([MEDIDA_PRINCIPAL]))
VAR base = ADDCOLUMNS(
    TOPN(90, dias_filtrados, 'dCalendário'[Data], DESC),
    "@v1", [MEDIDA_BARRA],
    "@v2", [MEDIDA_LINHA],
    "@l",  FORMAT('dCalendário'[Data], "dd/MM")
)
/* ── Formatação → JSON ── */
VAR json = "[" & CONCATENATEX(
    base,
    "{'label':'" & [@l] & "','e':" & SUBSTITUTE(FORMAT([@v1],"0.00"),",",".") & ",'p':" & SUBSTITUTE(FORMAT([@v2],"0.00"),",",".") & "}",
    ",",
    'dCalendário'[Data], ASC
) & "]"
/* ── CSS ── */
VAR css = "<style>*{box-sizing:border-box;margin:0;padding:0}.w{padding:16px;background:#F8FBFB;border-radius:18px;box-shadow:0 0 16px rgba(0,82,133,.20);font-family:'Raleway','Segoe UI',sans-serif}.ti{font-size:15px;font-weight:700;color:#1B3F6F;margin-bottom:8px}.tp{position:fixed;background:#1B3F6F;color:#fff;padding:6px 10px;border-radius:8px;font-size:11px;pointer-events:none;opacity:0;transition:opacity .12s;z-index:9999;white-space:nowrap}svg{width:100%;height:auto}</style>"
/* ── JS ── */
VAR js = "<script>(function(){var tip=document.getElementById('tp');var sT=function(h,e){tip.innerHTML=h;tip.style.left=(e.clientX+14)+'px';tip.style.top=(e.clientY+14)+'px';tip.style.opacity=1};var hT=function(){tip.style.opacity=0};var bT=function(el){el.querySelectorAll('[data-tip]').forEach(function(n){n.addEventListener('mousemove',function(e){sT(n.dataset.tip,e)});n.addEventListener('mouseleave',hT)})};var brl=function(v){return isNaN(v)?'R$ 0':v.toLocaleString('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0})};var data=" & json & ";var el=document.getElementById('ch');if(!el)return;/* INSERIR LÓGICA DO GRÁFICO AQUI */bT(el);}());</script>"
RETURN "<div class='w'><div class='ti'>TÍTULO DO VISUAL</div>" & css & "<div id='ch'></div><div id='tp' class='tp'></div></div>" & js
```

### Template B — Visual HTML/CSS puro (sem JS)

```dax
Bullets 001: Valor Emitido =

/* ── Layout ── */
VAR borda_card = "18px"
/* ── Tipografia ── */
VAR fonte = "'Raleway','Segoe UI',SegoeUI,-apple-system,BlinkMacSystemFont,Arial,sans-serif"
/* ── Cores ── */
VAR cor_texto_valor = "#1B3F6F"
VAR cor_texto_label = "#434343"
VAR sombra_padrao   = "0 0 16px rgba(0,82,133,0.20)"
/* ── Dados / Medidas ── */
VAR valor_principal = [MEDIDA]
/* ── Formatação ── */
VAR valor_formatado = "R$ " & FORMAT(valor_principal/1000,"#,##0.0") & "k"
/* ── Blocos HTML ── */
VAR conteudo = "<div style='font-size:22px;font-weight:800;color:" & cor_texto_valor & "'>" & valor_formatado & "</div>"
RETURN "<div style='padding:16px;background:#F8FBFB;border-radius:" & borda_card & ";box-shadow:" & sombra_padrao & ";font-family:" & fonte & "'>" & conteudo & "</div>"
```

## Perfil de cliente — mantendo uma galeria de referência por projeto

Cada projeto tende a acumular um conjunto de medidas HTML "canônicas" (a primeira KPI card bem resolvida, o primeiro donut com tooltip funcionando) que servem de referência rápida para replicar o padrão em visuais novos — mais rápido que reconstruir do zero a partir só desta reference. Manter esse "perfil de cliente" **dentro do projeto**, nunca nesta skill:

- **Onde guardar:** `@client_context/design-system/` (tokens de paleta/tipografia já ajustados ao cliente) e, opcionalmente, um índice de medidas de referência em `_docs/` do domínio Power BI (ex.: "ver `Geral 002` como exemplo de KPI card com variação MoM").
- **O que registrar por medida de referência:** nome da medida, o que ela exemplifica (ex.: "arc path de donut com legenda lateral"), e o arquivo/projeto onde ela vive.
- **Se a consultoria tiver identidade própria** (nome, paleta, voz) a aplicar por cima do design system default desta reference, ela mora em `company-profiles/<empresa>/` (fora do escopo desta skill) — nunca hardcoded aqui nem nos templates.

Exemplo de estrutura de índice (adaptar ao projeto real, não copiar literal):

```markdown
## Galeria de referência — {{CLIENTE}}

| Medida | Técnica | O que exemplifica |
|---|---|---|
| Geral 002: Card Valor Principal | HTML/CSS | KPI card com badge de variação MoM |
| Gráficos 001: Série Temporal | JS+SVG | linha+barra com tooltip e eixo formatado |
| Tabelas 001: Ranking Top N | HTML/CSS | tabela com badge de ação por linha |
```
