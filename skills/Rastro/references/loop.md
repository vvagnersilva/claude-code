# O loop completo — modo Depurar

O caminho padrão para UM bug, do começo ao fim. **Cada fase precisa terminar antes da
próxima.** Anuncie ao dono em que fase você está. Se pular uma fase, você está violando o
espírito do método — e é aí que o loop de tokens começa.

---

## Fase 0 — PARE e faça a triagem (antes de tocar em qualquer arquivo)
Antes de qualquer coisa, responda em uma linha cada:
- **Qual é o sintoma EXATO?** (a mensagem de erro literal, o comportamento, um print da tela)
- **Quando funcionou pela última vez? O que mudou desde então?** (`git diff`, commits recentes, dependência nova, config alterada)
- **Como o app está rodando?** (comando, ambiente, venv/nvm) — leia isso do `.rastro/config.md`.
- **Severidade** (define a pressa):
  - **P0 Crítico** — perda de dado, falha de segurança, sistema totalmente parado. Trabalhe AGORA.
  - **P1 Alto** — funcionalidade central quebrada; existe contorno, mas conserte logo.
  - **P2 Médio** — funcionalidade não-central quebrada; existe contorno.
  - **P3 Baixo** — cosmético / canto raríssimo. Sem impacto real.
  - Na dúvida entre dois níveis, escolha o **mais alto**.
- **"Já vi esse erro?"** → `python3 scripts/rastro.py buscar "<palavras do erro>"`. Se voltar
  algo parecido, comece pela causa-raiz já registrada.

## Fase 1 — Reproduzir (ver com os próprios olhos)
- Rode o comando/ação exato que dispara o bug. Veja a saída real, não uma suposição.
- Registre o **erro inteiro** (stack trace completo, com arquivo e linha) — não um resumo.
- Anote **o que você esperava × o que aconteceu**.
- É **consistente** (toda vez) ou **intermitente**?
- **Se não consegue reproduzir, não conserte.** Vá para o modo Reproduzir e junte mais contexto.
- Garanta um **teste que dá pra rodar** (o comando de teste/build do config, ou uma checagem observável). Sem um teste que fecha o ciclo sozinho, o loop nunca fecha.

## Fase 2 — Juntar evidência (observar o runtime, não teorizar)
- **Leia o erro inteiro, com calma.** A resposta costuma estar literalmente ali (arquivo, linha, código do erro).
- **Leia o código no ponto do erro** — não adivinhe o que ele faz, leia.
- **Observe o valor real em execução.** O código-fonte é o mapa; o runtime é o território.
  Rode sob debugger e ponha um breakpoint, OU instrumente o mínimo (ver abaixo). Não diga
  "acho que essa variável está null" — imprima/inspecione e **saiba**.
- **Instrumentação mínima e marcada** (quando precisar de logs): ponha 2-3 logs nos pontos de
  decisão do fluxo de dados, **todos com um marcador** para achar e remover depois. Ex.:
  ```
  console.log('[RASTRO] entrada auth:', req.user)   // RASTRO
  print(f"[RASTRO] parser recebeu: {valor}")         # RASTRO
  ```
  Evite a "avalanche de prints" — 2-3 focados valem mais que 30.
- Junte também: mudanças recentes (`git log --oneline -10 -- <arquivo>`) e o dado de entrada que dispara o bug.

## Fase 3 — Causa-raiz (o porquê, não o quê)
Use o modo Causa-raiz (`references/causa_raiz.md`):
- **5 porquês** até chegar a uma causa que não dá pra quebrar mais.
- **Portão da Causa-Raiz:** "se eu remover minha correção, o bug volta? volta → paliativo; não volta → correção real."
- **Rastreie o fluxo de dados de trás pra frente:** o bug está onde o dado **primeiro** fica
  errado, não onde o erro finalmente aparece. Conserte na origem, não no sintoma.
- Escreva a causa-raiz em uma frase específica. "Trava" não é causa. "Trava porque `user` é
  null quando o middleware não trata requisição sem login" é causa.

## Fase 4 — Uma hipótese por vez
- Formule **uma** teoria clara: "Acho que X é a causa porque Y."
- Defina um teste para ela: "Se for isso, então Z deveria ser verdade." Rode. Anote: confirmou, refutou ou inconclusivo.
- **Não pare na primeira que "parece certa"** — a explicação óbvia está errada ~40% das vezes.
- Bug teimoso, intermitente ou que já resistiu a 2+ tentativas? Vá para a **matriz ACH**
  (hipóteses concorrentes × evidências) em `references/causa_raiz.md`.

## Fase 5 — Correção mínima
- Faça a **menor mudança possível** que ataca a causa-raiz. Um lugar só (se precisar de mais de um, justifique cada um separadamente).
- **Sem refatorar, sem otimizar, sem "defensiva" a mais.** Nada de "já que estou aqui".
- **Nunca mude código que você não leu.**

## Fase 6 — Verificar
- Rode o caso de reprodução: passa agora?
- Rode a suíte de testes relevante: você quebrou outra coisa?
- **Explique por que a correção funciona.** Se não consegue explicar, você não corrigiu — voltou a chutar.
- Não funcionou? **PARE.** Conte quantas correções você já tentou:
  - Menos de 3 → volte à Fase 2 com evidência nova.
  - **3 ou mais → pare de corrigir e questione a arquitetura** (modo Sair do loop, regra das 3 quedas).

## Fase 7 — Blindar (fechar de verdade)
Use o modo Blindar (`references/blindar.md`):
- **Guarda de regressão:** escreva um teste que **falha antes** e **passa depois**, testando o cenário da causa-raiz.
- **Limpe a instrumentação:** remova todo log com marcador `[RASTRO]`. O `git diff` final só pode conter a correção intencional.
- **Registre no diário:**
  ```
  python3 scripts/rastro.py registrar --titulo "..." --sintoma "..." --causa "..." \
      --correcao "..." --arquivos "..." --severidade P1 --status verificado --tags "..."
  ```
  Assim o mesmo bug nunca volta nem é re-investigado do zero.

---

## Bandeiras vermelhas — se pensar isto, PARE e volte à Fase 1
- "Conserto rápido agora, investigo depois."
- "Deixa eu só mudar X e ver se resolve."
- "Muda várias coisas de uma vez e roda os testes."
- "Pula o teste, eu verifico na mão."
- "Provavelmente é X, deixa eu corrigir isso."
- "Não entendi direito, mas isso talvez funcione."
- "Só mais uma tentativa" (quando já tentou 2+).

## Racionalizações comuns (e a realidade)
| Desculpa | Realidade |
|---|---|
| "É simples, não preciso de método" | Bug simples também tem causa-raiz. O método é rápido. |
| "É emergência, não dá tempo de método" | Método é MAIS rápido que ficar chutando. |
| "Deixa eu tentar isso primeiro, depois investigo" | A primeira correção define o padrão. Faça certo desde o começo. |
| "Corrigir tudo de uma vez economiza tempo" | Não dá pra isolar o que funcionou. Cria bug novo. |
| "Estou vendo o problema, deixa eu corrigir" | Ver o sintoma ≠ entender a causa-raiz. |
