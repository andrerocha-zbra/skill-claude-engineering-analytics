# Convenções ZBRA

Preferências operacionais e de nomenclatura da ZBRA enquanto consultoria, observadas nos projetos-fonte. Complementa `IDENTIDADE.md` (voz/comunicação) e `design-tokens.md` (visual). Aplica-se a qualquer projeto de cliente conduzido pela ZBRA através do harness — não é específico de um cliente.

## Rodapé padrão de documentos gerados

Todo documento/relatório HTML gerado para um cliente leva um rodapé fixo de autoria:

```
Doc gerada por {{EMPRESA_FOOTER}}
```

Para este perfil, o valor default de `{{EMPRESA_FOOTER}}` é:

```
ZBRA.DEV
```

Fonte: a skill `pbi-doc-zbra` trata isso como regra inviolável ("Footer ZBRA.DEV obrigatório") tanto na seção de branding quanto nas regras de geração de HTML — o rodapé "Doc gerada por ZBRA.DEV" aparece em todo mini-site de documentação de Power BI que a ZBRA entrega.

## Convenção de nome de repo-cérebro de cliente

Cada cliente da ZBRA tem seu próprio "repo-cérebro" (onde vivem as especificações, o histórico e as convenções daquele projeto especificamente). O nome do repositório segue o padrão:

```
<cliente>-brain
```

Exemplo: o cliente GRAACC teria `graacc-brain`.

Dentro desse repo-cérebro, um cliente pode ter seu próprio bloco de convenções específicas — nomes de lakehouse/schemas, orquestração de dados, paleta de cores do relatório, premissas de negócio fixas, etc. O projeto-fonte GRAACC ilustra a forma desse bloco (dentro da skill `bi-delivery-orchestrator`, seção "Perfil GRAACC (convenções específicas deste cliente)"): ali ficam registrados detalhes como nome do lakehouse, schemas de camada, arquivo de orquestração metadata-driven, convenção de nomes de notebook/função, paleta de cores do relatório e premissas de negócio fixas (ex.: janela de atividade). O conteúdo em si é específico do GRAACC e não se replica aqui — o que vale como padrão é a existência de um bloco "Perfil `<cliente>`" próprio por projeto, dentro do repo-cérebro daquele cliente.

## Onde registrar novas preferências da ZBRA

Preferências adicionais da ZBRA que surgirem com o uso (novos padrões de nomenclatura, novas regras de tom, ajustes ao design system, etc.) devem ser adicionadas **neste arquivo** — não espalhadas pelos repositórios de projeto de cliente. Isso mantém a identidade da consultoria centralizada em `company-profiles/zbra/`, único lugar do harness onde citar "ZBRA" é esperado.
