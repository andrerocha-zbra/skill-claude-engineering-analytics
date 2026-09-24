# Tempo de trabalho — {{CLIENTE}}

Registro único e acumulado do trabalho realizado por task, do mais recente para o mais
antigo. O tempo do agente não é instrumentado: é uma aproximação da duração da sessão. O
tempo humano estima quanto uma pessoa levaria para executar o mesmo trabalho e, no
fechamento, é detalhado por bloco para permitir conferência.

Ao identificar o início de uma task, abrir imediatamente uma linha no índice e um registro
detalhado com status `Em andamento`, fim `—`. Preencher o fim só depois que o responsável
confirmar que pode fechar. Cada task aparece exatamente uma vez no índice e uma vez nos
registros detalhados — mudou status, mudam as duas.

## Índice

| Task | Status | Início | Fim | Agente | Humano estimado |
|---|---|---|---|---|---|
| TASK-NNN__slug | Em andamento | AAAA-MM-DD HH:mm ±HH:mm | — | depende do fechamento | depende do fechamento |

## Registros detalhados

### TASK-NNN__slug

| Campo | Registro |
|---|---|
| Status | Em andamento |
| Início | AAAA-MM-DD HH:mm ±HH:mm |
| Fim | — |
| Tempo de trabalho do agente | Depende do fechamento (aproximação, não instrumentada). |
| Tempo de trabalho humano estimado | Depende do fechamento. |

#### Entregas realizadas

- {{uma linha por entrega concreta, com caminho do artefato}}

#### Estimativa humana por bloco

{{bloco a bloco, com subtotal conferível}}

| Campo | Registro |
|---|---|
| `commit_msg` | Resumo objetivo e levemente técnico do que foi implementado — vira a mensagem de commit (ver convenção em `references/02-processo-e-templates.md`). |
| `commit_pessoal` | Lembretes privados: débitos técnicos, riscos, melhorias futuras. |
| `commit_gerente` | Síntese do valor entregue e de qualquer decisão ainda necessária, em linguagem de negócio. |
| Resultado | {{o que ficou pronto}} |
| Pendências | {{o que continua em aberto e de quem depende}} |
