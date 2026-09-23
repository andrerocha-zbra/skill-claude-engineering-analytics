# Onboarding de empresa

Roda uma vez, quando `company-profiles/<empresa>/` ainda não existe. Recolhe o contexto que os outros references não têm como inferir — quem é a consultoria, que tipo de cliente ela atende, como ela se comunica, e como a pessoa por trás dela quer trabalhar com o Claude — e distribui esse conteúdo nos arquivos do perfil de empresa. Depois da primeira vez, a skill segue direto para o kickoff normal; não repete esta entrevista.

## Como conduzir

Uma seção por vez: explique o objetivo da seção, faça as perguntas, espere a resposta, confirme se falta algo, resuma o que entendeu, avance. Peça respostas ricas — quanto mais contexto, melhor o resto da skill se comporta — mas nunca insista além do que a pessoa quiser dar numa seção.

Antes de começar, pergunte se já existem materiais prontos: briefing de marca, apresentação institucional, página "sobre", proposta comercial, SOPs. Se houver, leia primeiro, extraia o que já responde às perguntas abaixo, e não repita o que já está claro — confirme só o que ficou ambíguo.

Regras que valem para as duas partes:

- Nunca inventar informação nem preencher lacuna com suposição.
- Nunca mudar o sentido do que a pessoa respondeu.
- Marcar `PENDENTE_VALIDACAO` (mesmo vocabulário de evidência do método) quando uma resposta ficar incompleta, em vez de completar por conta própria.
- Antes de escrever qualquer arquivo: mostrar um resumo do que vai em cada um, apontar o que ficou conflitante ou incompleto, esperar confirmação.
- Não substituir um arquivo já existente sem antes ler o que tem nele.

## Seção 1 — O negócio

> Alimenta `company-profiles/<empresa>/IDENTIDADE.md`.

1. O que a consultoria faz? Explique como explicaria a alguém de fora do mercado de dados.
2. Em que tipo de projeto ela é mais forte — engenharia, BI, modelagem, ML, um pacote completo?
3. O que mudou nos últimos anos no jeito de conduzir projetos de dados que mais afetou como ela trabalha?

## Seção 2 — Os clientes

> Alimenta `IDENTIDADE.md`.

1. Que tipo de cliente ela atende — porte, setor, maturidade de dados?
2. Em que situação um cliente costuma procurar — o que já tentaram antes e não funcionou?
3. O que normalmente falta no lado do cliente quando o projeto começa — dado, governança, clareza de requisito?

## Seção 3 — Posicionamento

> Alimenta `IDENTIDADE.md`.

1. O que diferencia o jeito de conduzir um projeto em relação a fazer isso sem um método?
2. Se tivesse que resumir a proposta de valor em um parágrafo, qual seria?
3. Existe uma forma específica de trabalhar (uma metodologia, uma disciplina) que a consultoria sempre aplica, independente do cliente?

## Seção 4 — Marca e voz

> Alimenta `IDENTIDADE.md`. É o que a skill usa para escrever conteúdo client-facing — atas, resumos, documentação — no tom certo.

1. Se a consultoria tivesse uma personalidade, quais adjetivos a descreveriam?
2. Qual tom nas comunicações externas — formal, direto, técnico, informal?
3. Existem palavras ou expressões que a consultoria evita, ou que usa com frequência?
4. Dois ou três exemplos reais de comunicação (e-mail, proposta, post) que representam bem esse tom — colar o texto ou linkar.

## Seção 5 — Operação e ferramentas

> Alimenta `company-profiles/<empresa>/convencoes.md`.

1. Qual nuvem de dados a consultoria usa por padrão quando o cliente não tem preferência — Fabric ou Databricks?
2. Que ferramentas de gestão de projeto, comunicação e documentação são usadas no dia a dia?
3. Existe alguma convenção própria (nomenclatura, formato de commit, estrutura de proposta) que já é usada hoje e deveria virar padrão?

## Seção 6 — Pessoas-chave

> Alimenta `IDENTIDADE.md`.

1. Quem são as pessoas envolvidas na condução de projetos — nome, papel, em que tipo de decisão cada uma deve ser consultada?
2. Há parceiros ou fornecedores recorrentes que valem menção?
3. Alguma regra de como se referir a essas pessoas ou a informação que não deve ser misturada entre projetos?

## Seção 7 — Como trabalhar com o Claude

> Alimenta `company-profiles/<empresa>/preferencias-trabalho.md` (arquivo novo — herdado por todo projeto criado depois, na seção "Preferências de trabalho" do `CLAUDE.md` gerado por `scripts/scaffold_cliente.py`).

1. Como prefere que o Claude se comunique — direto e curto, explicação detalhada, listas, conversa mais natural?
2. O que o Claude deve sempre fazer? (Ex.: confirmar antes de mudança estrutural, entregar a ação antes da explicação.)
3. O que o Claude nunca deve fazer?
4. Alguma frustração recorrente ao trabalhar com IA que vale evitar aqui?

## Fechamento

Depois de cobrir as 7 seções:

1. Resumir o que vai em cada arquivo (`IDENTIDADE.md`, `convencoes.md`, `preferencias-trabalho.md`) e onde o design visual (`design-tokens.md`) já existente se encaixa, se já houver um.
2. Apontar toda resposta pendente ou conflitante.
3. Esperar aprovação.
4. Criar os arquivos em `company-profiles/<empresa>/`.
5. Seguir para o kickoff do primeiro projeto.
