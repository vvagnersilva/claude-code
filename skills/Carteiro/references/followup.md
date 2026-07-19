# Follow-up — o lembrete gentil (nada cai)

O maior estrago numa caixa de entrada nao e demorar pra responder: e **esquecer**.
Um cliente que ficou 10 dias sem retorno acha que foi ignorado — e vai embora
calado. O Carteiro existe pra isso nao acontecer.

## Os degraus (quanto tempo esperando)
O motor conta os dias desde o ultimo contato e marca:
- 🟢 **recente** (0-2 dias) — tranquilo, ainda no prazo natural.
- 🟡 **3-6 dias** — ja passou do razoavel; vale um empurraozinho.
- 🔴 **7+ dias** — esta caindo no esquecimento; retome hoje, com prioridade.

Use `pend-hoje` pra ver quem esta esperando, do mais antigo pro mais novo.

## Dois lados da fila
- `direcao eu_devo` — **o dono deve a resposta.** Aqui o Carteiro escreve o retorno
  (nao um "lembrete", a resposta em si) e pede desculpa leve pela demora se passou
  do prazo. Ex: "Oi <nome>, desculpa a demora! Sobre <assunto>: ...".
- `direcao aguardo` — **o dono ja respondeu e espera o outro.** Aqui o Carteiro
  escreve um lembrete gentil, sem cobrar com dureza. Ex: "Oi <nome>, tudo bem?
  So passando pra saber se voce chegou a ver o que te mandei sobre <assunto> —
  fico no aguardo quando puder. Abraco!".

## Tom do lembrete
- Gentil e sem culpa — a pessoa nao respondeu, nao cometeu um crime.
- Reancora o assunto em uma linha (o outro pode ter esquecido o contexto).
- Um unico proximo passo claro.
- Curto. Um lembrete longo parece cobranca.
- Sempre no tom do dono (config).

**Importante:** isto NAO e cobranca de pagamento atrasado — pra isso existe a Regua.
O follow-up do Carteiro e sobre uma resposta/decisao pendente, nao sobre dinheiro
devido. Se o assunto for pagamento em atraso, avise o dono que a Regua e a skill
certa.

## Fluxo
1. `pend-hoje` mostra quem esta esperando.
2. Para cada 🔴/🟡, o Carteiro escreve o retorno/lembrete no tom do dono.
3. O dono revisa e envia (WhatsApp ou e-mail).
4. Depois de enviar: `pend-tocar --id N` (zera o contador) ou `pend-responder
   --id N` se o assunto foi resolvido.
