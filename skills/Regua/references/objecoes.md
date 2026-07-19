# Como responder às reações do cliente (objeções de cobrança)

> Regra mestra: **acolher → confirmar o combinado → oferecer um caminho → manter o
> cliente**. Nunca discutir, ameaçar, ironizar ou expor. Adapte ao tom do dono
> (`.regua/config.md`). Toda resposta termina com **um próximo passo claro**.

## "Tá difícil esse mês / não tenho como pagar agora"
- Acolha de verdade e ofereça opção concreta:
  "Imagino, {nome}, acontece com todo mundo. Vamos resolver juntos: prefere a gente
  **dividir em 2x** ou marcar uma **nova data** que caiba melhor? Me diz um valor/dia
  que funciona pra você."
- Se combinar nova data, **reagende** no sistema: `regua.py editar --id N --venc DD/MM/AAAA`.
- Se combinar parcelar, registre o que ele pagar agora com `regua.py pagar` e ajuste o restante.

## "Já paguei!"
- Nunca contrarie de cara. Peça a confirmação com leveza:
  "Que ótimo, {nome}! Deve ter cruzado aqui no meu controle 🙏. Você consegue me mandar
  o comprovante (ou a data/horário do Pix) pra eu localizar e dar baixa na hora?"
- Ao confirmar, baixe: `regua.py quitar --id N` (ou `pagar` se foi parcial).
- Se realmente foi pago e não estava lançado, corrija — a Régua nunca insiste num valor já quitado.

## "Não recebi a cobrança / não sabia"
- "Sem problema, {nome}! Devo ter falhado em te avisar. Aqui está: {serviço}, {valor},
  venceu em {data}. Te mando a chave Pix/2ª via agora pra facilitar. 👍"
- Reenvie o lembrete do degrau atual e marque o contato (`regua.py marcar --id N`).

## "Vou pagar semana que vem / depois"
- Aceite, mas **fixe uma data combinada** (compromisso, não no ar):
  "Combinado, {nome}! Posso anotar pra **{data específica}** então? Assim deixo aqui
  registrado e não te incomodo antes."
- Reagende para a data combinada com `editar --venc` e siga a régua a partir dali.

## "O serviço teve problema / não fiquei satisfeito"
- **Pare a cobrança** e trate a insatisfação primeiro:
  "Obrigado por falar, {nome} — isso é importante. Me conta o que houve pra eu resolver.
  Acertamos o pagamento depois que você estiver satisfeito, pode ser?"
- Avise o dono: pode haver retrabalho, desconto ou cancelamento da conta antes de cobrar.

## "Achei caro / não vou pagar tudo"
- Não brigue pelo valor já combinado; relembre o acordo com calma e ofereça saída:
  "Entendo, {nome}. O combinado da {serviço} foi {valor}. Se ficou pesado, **posso
  parcelar** pra aliviar. Como prefere fazer?"

## Cliente sumiu (não responde há dias)
- Reforço educado, sem repetir a mesma frase do degrau anterior:
  "Oi, {nome}, tudo bem? Só retomando aqui sobre os {valor} em aberto. Faço questão de
  resolver no diálogo — me dá um retorno quando puder? 🙏"
- Se persistir, suba um degrau na régua (rode `regua.py hoje` no dia seguinte do offset).

---

### Limites (não cruzar nunca)
- Sem ameaça ("vou te negativar hoje"), sem cobrança em grupo, sem falar com chefe/familiar do cliente.
- Sem juros/multa que o dono não informou.
- Medidas formais (protesto, negativação, cobrança judicial) **não** são feitas pela Régua —
  oriente o dono a procurar contador/advogado e a decidir se mantém o cliente.
