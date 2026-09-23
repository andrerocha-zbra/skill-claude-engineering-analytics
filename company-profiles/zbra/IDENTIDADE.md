# Identidade de comunicação — ZBRA

Este documento é o guia de voz e comunicação da ZBRA. A skill genérica do harness (`plugins/analytics-project-architect/`) consulta este arquivo sempre que precisa gerar conteúdo voltado ao cliente ou a outros públicos — resumos de reunião, handoffs técnicos, documentação, comunicação de novidades, material de mercado, status interno ou one-pagers executivos. Ele reúne, num único lugar, os cinco formatos de comunicação da ZBRA e consolida os padrões de escrita que a empresa proíbe em qualquer texto que produz.

---

## 1. Comunicação Cliente

Formato para falar **com o cliente**: gestão estratégica e tática que contrata e usa o que a ZBRA entrega.

**Quando usar:** apresentar o que foi entregue e o valor que gera para o negócio do cliente; explicar um resultado, um relatório, uma base de dados ou uma decisão possível; textos de tela, e-mails, apresentações e documentos voltados ao cliente. Gatilho: "o cliente vai ler isso".

**Interlocutor:** gestor do cliente. Conhece o negócio dele a fundo, mas não a nossa engenharia. Tem pouco tempo e decide com base em valor e confiança, não em detalhe técnico.

**Objetivo:** que o cliente entenda o que ganhou, como aquilo ajuda o negócio e qual o próximo passo, sem precisar de tradução. Gerar clareza e confiança.

**Tom e voz:**
- Claro, objetivo e um pouco didático.
- Frases curtas, uma ideia por frase.
- Fala do problema do cliente e do resultado, não do nosso processo ou ferramenta.
- Honesto: promete só o que é real e mensurável.
- Português simples. Traduz o técnico em benefício.

**Estrutura recomendada:**
1. O que é (uma frase de contexto).
2. O que foi feito (objetivo, sem processo).
3. O valor para o negócio (o retorno: caixa, tempo, risco, decisão).
4. Como usar / próximo passo (o que o cliente faz com isso).
5. Prova (um número real ou um exemplo concreto).

**Fórmula reutilizável:** Contexto → o que fizemos → valor/retorno → prova.

> Exemplo: "A cobrança do dia ficava espalhada em planilhas *(contexto)*. Reunimos tudo em um painel por canal *(o que fizemos)*. A equipe passou a agir no mesmo dia, em vez de descobrir depois *(valor)*. Hoje são 6 canais acompanhados quase em tempo real *(prova)*."

**Regras específicas deste formato (além dos padrões banidos gerais na seção final):**
- Tom milagroso / "solução mágica": nada de "agora tudo decide sozinho", "o escuro acabou". Entregamos soluções reais, não milagre.
- Absolutos: "ninguém via", "sempre bate", "nunca falha" quase nunca são verdade. Prefira "era percebido com atraso", "os números ficam consistentes".
- Jargão e sigla técnica: DAX, medallion, DirectQuery, MRR sem tradução, nomes de tabela crus.
- Falar do fornecedor: "nosso processo", "documentação viva", "re-verificado ao vivo". O cliente quer o valor dele, não o nosso método.
- Meta e número interno: "163 medidas" não diz nada ao gestor.

**Exemplos antes → depois:**

| Antes (ruim) | Depois (bom) |
|---|---|
| O que estava invisível, agora decide o dia. | O que a equipe passou a acompanhar no dia a dia. |
| Não é um relatório, é uma fundação de dados. | Uma base de dados que a operação usa todos os dias. |
| Antes, ninguém percebia o site fora do ar. | Antes, um site fora do ar era percebido com atraso. |
| A métrica que revelou a diferença entre canais. | O indicador que mostrou a diferença entre os canais. |
| 163 medidas no modelo. | 6 canais de cobrança acompanhados quase em tempo real. |
| Arquitetura medallion governada com DAX otimizado. | Uma base única e confiável, com números que batem entre relatórios. |

**Checklist rápido antes de enviar:**
- [ ] Um gestor entende sem perguntar o que é.
- [ ] Está claro o valor para o negócio (caixa, tempo, risco ou decisão).
- [ ] Nenhum travessão.
- [ ] Nenhuma afirmação milagrosa ou absoluta.
- [ ] Nenhum jargão sem tradução.
- [ ] Todo número citado é real e datado.

---

## 2. Comunicação Mercado

Formato para falar **com o mercado**: prospects, redes sociais, site institucional, propostas, cases públicos. Vende ideias, produtos, soluções e impacto.

**Quando usar:** divulgar um case, um produto ou uma solução da ZBRA; post, página de venda, proposta comercial, material de evento; atrair quem ainda não é cliente e mostrar do que somos capazes. Gatilho: "isso é público e precisa gerar interesse".

**Interlocutor:** um decisor que ainda não nos conhece (ou conhece pouco). Cético por padrão, comparando opções. Quer saber se resolvemos um problema que ele tem e se dá para confiar.

**Objetivo:** gerar interesse e confiança a ponto de a pessoa querer conversar. Vender a ideia e o resultado, não a tecnologia. Deixar clara a proposta de valor e o próximo passo (chamada para ação).

**Tom e voz:**
- Confiante, mas honesto. Sem promessa milagrosa.
- Começa pelo problema do mercado, não pela ZBRA.
- Concreto: resultado mensurável e prova real valem mais que adjetivo.
- Uma proposta de valor clara, memorável, sem exagero.

**Estrutura recomendada:**
1. Problema que o público reconhece como dele.
2. Solução da ZBRA em uma frase (a proposta de valor).
3. Como funciona em linhas gerais (sem manual).
4. Prova: case, número real, depoimento.
5. Impacto no negócio (o que muda para quem contrata).
6. Chamada para ação (o próximo passo claro).

**Fórmula reutilizável:** Problema → solução (proposta de valor) → prova → impacto → chamada para ação.

> Exemplo: "Captação parada em planilhas trava a decisão *(problema)*. A ZBRA transforma o dado da operação em decisão do dia *(solução)*. Em um projeto real, a análise que levava horas passou a levar minutos *(prova)*, e a equipe passou a agir a tempo *(impacto)*. Vamos conversar sobre o seu caso *(ação)*."

**Regras específicas deste formato:**
- Tom milagroso: "transformação total", "revolução", "resolve tudo" vende desconfiança.
- Absolutos e superlativos vazios: "o melhor", "único", "sempre", "nunca", sem prova.
- Promessa sem lastro: todo número precisa vir de caso real; se for estimativa, diga que é.
- Jargão técnico como argumento de venda: o mercado compra resultado, não sigla.
- Falar só de nós: o texto começa no problema do cliente, não no nosso portfólio.

**Exemplos antes → depois:**

| Antes (ruim) | Depois (bom) |
|---|---|
| Não é só uma ferramenta, é uma revolução. | Uma ferramenta que a equipe usa todo dia para decidir. |
| Nossa solução revoluciona a gestão de dados. | Transformamos o dado da operação em decisão do dia a dia. |
| A melhor plataforma de BI do mercado. | BI que a equipe usa todo dia para agir a tempo. |
| Resultados extraordinários e imediatos. | Em um projeto real, a análise caiu de horas para minutos. |
| Inteligência de dados de ponta a ponta. | Do dado bruto ao relatório que o gestor entende sozinho. |

**Checklist rápido antes de enviar:**
- [ ] Começa por um problema que o público reconhece.
- [ ] A proposta de valor cabe em uma frase.
- [ ] Toda prova é de caso real (ou marcada como estimativa).
- [ ] Nenhum travessão.
- [ ] Nenhuma promessa milagrosa, absoluta ou superlativo sem prova.
- [ ] Tem uma chamada para ação clara.

---

## 3. Comunicação Interna

Formato para comunicação **dentro da ZBRA**: status de projeto, retrospectiva, alinhamento entre times, registro de decisão. Mostra números, tecnologias e o impacto no negócio do cliente.

**Quando usar:** reportar status ou resultado de um projeto para o time e a liderança; registrar uma decisão, um aprendizado ou um risco; alinhar quem entra no projeto ou quem depende dele. Gatilho: "é para a ZBRA se organizar e decidir".

**Interlocutor:** time e liderança da ZBRA. Conhece a stack e o vocabulário. Quer o quadro real para decidir e ajudar, sem maquiagem.

**Objetivo:** dar visão honesta do estado do projeto: o que foi feito, com que números e tecnologia, qual o impacto no cliente, o que está travado e o que vem a seguir. Habilitar decisão interna.

**Tom e voz:**
- Direto e franco. Problema é problema; risco é risco.
- Denso em fato: números, datas, tecnologias, decisões.
- Jargão técnico é permitido (o time entende), mas sem enfeite.
- Sempre amarra o técnico ao impacto no negócio do cliente.

**Estrutura recomendada:**
1. Onde estamos (status em uma linha).
2. O que foi feito (entregas, com números e tecnologias).
3. Impacto no negócio do cliente (por que isso importa para ele).
4. Riscos e bloqueios (o que pode dar errado, o que trava).
5. Decisões tomadas / a tomar.
6. Próximos passos (quem faz o quê, até quando).

**Fórmula reutilizável:** Status → feito (números + tech) → impacto no cliente → riscos → próximos passos.

> Exemplo: "Silver estável, Gold sob demanda *(status)*. Fato de doações com ~5,9 mi de linhas no Fabric, 6 cargas orquestradas por metadata *(feito)*. Isso dá ao cliente números que batem entre relatórios *(impacto)*. Risco: uma origem crua ainda sem watermark *(risco)*. Próximo: fechar o incremental até sexta *(passo)*."

**Regras específicas deste formato:**
- Tom milagroso: relatório interno não é vitrine; nada de "entrega impecável", "sucesso total".
- Absolutos: "nunca falha", "100% coberto" sem evidência. Diga o número real.
- Esconder problema: status maquiado atrapalha decisão. Franqueza acima de imagem.
- Número sem origem ou data: todo dado citado tem fonte e período.
- Impacto solto: não basta listar tecnologia; diga o que ela muda para o cliente.

**Exemplos antes → depois:**

| Antes (ruim) | Depois (bom) |
|---|---|
| Não foi só entregar, foi transformar a operação. | Entregamos 3 relatórios; a análise caiu de horas para minutos. |
| Entrega impecável, tudo funcionando 100%. | 3 relatórios em produção; 1 origem ainda sem carga incremental. |
| Fizemos várias medidas e otimizações. | 163 indicadores no modelo; refresh caiu de 8 para 3 min após F2. |
| O modelo ficou muito bom. | Modelo estável; falta validar 2 medidas de aging com o cliente. |
| Sempre bate com o sistema. | Bate com o sistema nos 3 canais testados; falta validar cartão. |

**Checklist rápido antes de enviar:**
- [ ] O status real está claro na primeira linha.
- [ ] Todo número tem origem e data.
- [ ] O impacto no negócio do cliente está explícito.
- [ ] Riscos e bloqueios aparecem (sem maquiagem).
- [ ] Próximos passos têm dono e prazo.
- [ ] Nenhum travessão, nenhuma frase de vitrine.

---

## 4. Comunicação Técnica / Handoff

Formato para falar **com outro time técnico**: quem vai operar, manter ou continuar o que a ZBRA construiu (engenharia de dados, dev, BI). Documenta arquitetura, decisões e como operar.

**Quando usar:** passar um projeto para outro time (handoff) ou documentar para o futuro; explicar arquitetura, convenções, decisões e trade-offs; descrever como rodar, atualizar e diagnosticar problemas. Gatilho: "alguém técnico precisa continuar isto sem nos perguntar".

**Interlocutor:** pessoa técnica que não estava no projeto. Sabe programar e modelar, mas não conhece as escolhas específicas. Precisa reproduzir, manter e evoluir com segurança.

**Objetivo:** que outra pessoa técnica opere e evolua o que foi construído sem depender de quem fez. Precisão e rastreabilidade acima de estilo.

**Tom e voz:**
- Preciso e literal. Nada de metáfora ou marketing.
- Passo a passo reproduzível, com caminhos, nomes e comandos exatos.
- Explica o porquê das decisões, não só o quê.
- Denso em referência; enxuto em adjetivo.

**Estrutura recomendada:**
1. O que é e para quem (escopo e público).
2. Arquitetura (componentes, fluxo, onde cada coisa vive).
3. Decisões e trade-offs (o que foi escolhido e por quê).
4. Como operar (rodar, atualizar, configurar; comandos e caminhos).
5. Convenções (nomenclatura, padrões, o que não mudar sem motivo).
6. Diagnóstico (erros comuns, como investigar, de onde vem cada número).
7. Roadmap / pendências (o que falta, o que evoluir).

**Fórmula reutilizável:** O que é → arquitetura → decisões (porquê) → como operar → convenções → diagnóstico.

> Exemplo: "Lakehouse no Fabric, camadas Bronze e Silver *(arquitetura)*. Destino vem do `metadata_driven_orchestration.csv`, não do `TARGET_TABLE` *(decisão + porquê)*. Para atualizar: editar a linha de config e rodar o notebook `nb_orchestration` *(como operar)*."

**Regras específicas deste formato:**
- Tom milagroso ou de vitrine: doc técnico não vende; descreve.
- Absolutos sem prova: "nunca quebra", "sempre funciona". Descreva limites e condições reais.
- Vago: "configure o ambiente" sem dizer como. Dê o caminho, o comando, o valor.
- Decisão sem porquê: registrar a escolha sem o motivo gera retrabalho depois.
- Passo não reproduzível: se outra pessoa não consegue repetir, não está documentado.

**Exemplos antes → depois:**

| Antes (ruim) | Depois (bom) |
|---|---|
| Não é um pipeline comum, é uma solução robusta. | Pipeline incremental por watermark; reprocessa se o schema da origem mudar. |
| Basta rodar o pipeline. | Rode `nb_orchestration` no workspace X; ele lê a config e carrega Bronze e Silver. |
| A carga é incremental e robusta. | Carga incremental por watermark em `dt_atualizacao`; reprocessa se a origem mudar de schema. |
| Usamos a melhor arquitetura. | Medallion (Bronze, Silver); Gold sob demanda. Motivo: evitar custo de refresh sem uso. |
| Os nomes seguem um padrão. | Medidas: `<Página> - <ID>: <Nome>`. Não renomear sem atualizar os visuais que as referenciam. |

**Checklist rápido antes de enviar:**
- [ ] Outra pessoa técnica reproduz sem perguntar.
- [ ] Cada decisão importante tem o porquê registrado.
- [ ] Caminhos, comandos e nomes são exatos.
- [ ] Erros comuns e diagnóstico estão cobertos.
- [ ] Nenhum travessão, nenhuma frase de vitrine.
- [ ] Pendências e limites estão explícitos.

---

## 5. Comunicação Executiva / One-pager

Formato para a **síntese ultracurta** destinada a um decisor de alto nível (C-level do cliente ou liderança da ZBRA). Cabe em uma página ou uma tela.

**Quando usar:** levar uma decisão ou um resultado ao topo, com pouquíssimo tempo de leitura; abrir uma apresentação, resumir um projeto, pedir um sim/não. Gatilho: "a pessoa tem 60 segundos e precisa decidir".

**Interlocutor:** decisor de alto nível. Enxerga o negócio inteiro, tem tempo curtíssimo e foco em valor, risco e próximo passo. Não vai ler detalhe; quer a essência.

**Objetivo:** em uma página, dizer o problema, o que foi feito, o valor com um número, o próximo passo e a decisão pedida. Habilitar decisão rápida sem exigir contexto extra.

**Tom e voz:**
- Máxima densidade, mínimo texto. Cada palavra paga aluguel.
- Um número âncora que resume o valor.
- Afirmações verificáveis, sem floreio.
- Escaneável: título forte, poucos blocos, destaque no que decide.

**Estrutura recomendada (uma página):**
1. Título (a mensagem em uma linha).
2. Problema / contexto (uma a duas frases).
3. O que foi feito (uma a duas frases).
4. Valor (um número âncora + o que ele significa).
5. Próximo passo / decisão pedida (o que se espera do leitor).

**Fórmula reutilizável:** Título → problema → o que fizemos → número âncora → decisão pedida.

> Exemplo: "**Base pronta; R$ 4,75 mi de receita recorrente a recuperar.** A operação não via quem parou de pagar *(problema)*. Reunimos a base e criamos a leitura de retenção *(feito)*. 121.901 doadores ativos que não pagam, R$ 4,75 mi *(número)*. Decisão: aprovar a fase de recuperação *(passo)*."

**Regras específicas deste formato:**
- Tom milagroso: no topo, exagero destrói credibilidade mais rápido ainda.
- Absolutos: "ninguém", "sempre", "nunca". Um decisor testa isso na hora.
- Detalhe técnico: nada de arquitetura, sigla ou processo. Só valor e decisão.
- Mais de uma página: se não cabe, não é executivo.
- Número sem significado: todo número vem com o que ele quer dizer para o negócio.

**Exemplos antes → depois:**

| Antes (ruim) | Depois (bom) |
|---|---|
| Não é um projeto, é uma transformação. | Base de dados pronta; três relatórios em uso na operação. |
| Implementamos uma arquitetura moderna de dados que revoluciona a gestão. | Base de dados pronta; três relatórios já em uso na operação. |
| Enorme potencial de ganho com nossa solução. | R$ 4,75 mi de receita recorrente mapeada para recuperação. |
| O projeto foi um sucesso absoluto. | Análise que levava horas passou a levar minutos. |
| Recomendamos seguir com todas as próximas fases imediatamente. | Decisão pedida: aprovar a fase de recuperação de recorrência. |

**Checklist rápido antes de enviar:**
- [ ] Cabe em uma página ou uma tela.
- [ ] Tem um número âncora com significado claro.
- [ ] A decisão pedida está explícita.
- [ ] Zero detalhe técnico.
- [ ] Nenhum travessão, nenhuma frase milagrosa ou absoluta.
- [ ] O título entrega a mensagem sozinho.

---

## 6. Padrões de escrita de IA/marketing banidos (consolidado)

Estes padrões aparecem repetidos, palavra por palavra, nos cinco formatos acima — são o núcleo comum do que a ZBRA proíbe em qualquer comunicação, cliente ou interna. Reunidos aqui sem duplicação:

- **Antítese de contraste** — "Não é X, é Y" / "Não foi só X, foi Y" / "Em vez de X, Y".
  - *Ex.: "Não é um relatório, é uma fundação de dados." → "Uma base de dados que a operação usa todos os dias."*
  - *Ex.: "Não é só uma ferramenta, é uma revolução." → "Uma ferramenta que a equipe usa todo dia para decidir."*
  - *Ex.: "Não foi só entregar, foi transformar a operação." → "Entregamos 3 relatórios; a análise caiu de horas para minutos."*
  - *Ex.: "Não é um pipeline comum, é uma solução robusta." → "Pipeline incremental por watermark; reprocessa se o schema da origem mudar."*
  - *Ex.: "Não é um projeto, é uma transformação." → "Base de dados pronta; três relatórios em uso na operação."*

- **Reversão dramática** — usar o antes/depois como efeito de estilo, não como informação.
  - *Ex.: "O que estava invisível, agora decide o dia." → "O que a equipe passou a acompanhar no dia a dia."*
  - *Ex.: "Antes, ninguém percebia o site fora do ar." → "Antes, um site fora do ar era percebido com atraso."*

- **Tríade decorativa** — regra de três usada só pelo ritmo, sem função informativa.

- **Substantivo grandioso** — "fundação de dados", "jornada", "ativo estratégico" quando cabe um termo concreto.
  - *Ex.: "Arquitetura medallion governada com DAX otimizado." → "Uma base única e confiável, com números que batem entre relatórios."*

- **Punchline com dois-pontos** para soar profundo — "O ponto é outro:", "O valor:".

- **Adjetivo de hype sem função** — "poderoso", "robusto", "única e confiável", "mais clara".
  - *Ex.: "A carga é incremental e robusta." → "Carga incremental por watermark em `dt_atualizacao`; reprocessa se a origem mudar de schema."*

- **Metáfora publicitária** — "a porta se abre", "o coração que pulsa".

- **Frase de efeito** curta e isolada, usada só para impressionar.

> No lugar de tudo isso: frase declarativa direta, um fato por frase, substantivo concreto, dito como uma pessoa explicaria a um colega.

Padrões adicionais, específicos de determinados formatos mas recorrentes:

- **Travessão (`—`)** — soa artificial em todos os formatos da ZBRA. Usar ponto, vírgula, dois-pontos ou parênteses.
- **Tom milagroso / "solução mágica"** — "agora tudo decide sozinho", "o escuro acabou", "transformação total", "revolução", "resolve tudo", "entrega impecável", "sucesso total". Entregamos soluções reais, não milagre — e isso vale tanto para o cliente quanto para dentro de casa (relatório interno não é vitrine) e, no topo (one-pager executivo), o exagero destrói credibilidade ainda mais rápido.
  - *Ex.: "Implementamos uma arquitetura moderna de dados que revoluciona a gestão." → "Base de dados pronta; três relatórios já em uso na operação."*
  - *Ex.: "O projeto foi um sucesso absoluto." → "Análise que levava horas passou a levar minutos."*
- **Absolutos** — "ninguém via", "sempre bate", "nunca falha", "100% coberto", "sempre", "nunca" quase nunca são verdade e um decisor testa isso na hora. Preferir formulações que descrevem a condição real ("era percebido com atraso", "os números ficam consistentes", "bate com o sistema nos 3 canais testados; falta validar cartão").
  - *Ex.: "Sempre bate com o sistema." → "Bate com o sistema nos 3 canais testados; falta validar cartão."*
- **Jargão e sigla técnica sem tradução** — DAX, medallion, DirectQuery, MRR, nomes de tabela crus. Aceitável em comunicação técnica e interna (o público entende); proibido para cliente e proibido em one-pager executivo (zero detalhe técnico).
- **Promessa sem lastro / superlativo vazio** — "o melhor", "único", "resultados extraordinários", "enorme potencial de ganho". Todo número precisa vir de caso real; se for estimativa, dizer que é.
  - *Ex.: "A melhor plataforma de BI do mercado." → "BI que a equipe usa todo dia para agir a tempo."*
  - *Ex.: "Enorme potencial de ganho com nossa solução." → "R$ 4,75 mi de receita recorrente mapeada para recuperação."*
- **Falar do fornecedor / falar só de nós** — "nosso processo", "documentação viva", "re-verificado ao vivo", portfólio da ZBRA em vez do problema do cliente. O cliente e o mercado querem o valor deles, não o nosso método.
- **Meta e número interno sem tradução** — "163 medidas" não diz nada a um gestor ou ao mercado; vira número interno legítimo só em comunicação interna, desde que tenha origem e data.
  - *Ex.: "163 medidas no modelo." → "6 canais de cobrança acompanhados quase em tempo real." (versão cliente)*
  - *Ex.: "Fizemos várias medidas e otimizações." → "163 indicadores no modelo; refresh caiu de 8 para 3 min após F2." (versão interna, com origem e data)*
- **Esconder problema / status maquiado** — específico da comunicação interna: franqueza acima de imagem; problema é problema, risco é risco.
- **Vago / passo não reproduzível** — específico da comunicação técnica: "configure o ambiente" sem dizer como; decisão registrada sem o porquê gera retrabalho depois.
- **Detalhe técnico em contexto executivo** — específico do one-pager: nada de arquitetura, sigla ou processo; só valor e decisão. Mais de uma página deixa de ser executivo.
