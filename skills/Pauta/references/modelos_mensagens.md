# Modelos de mensagem (WhatsApp-first)

Use como ESQUELETO e adapte ao tom da config (`.pauta/config.md`). Sempre troque
os campos `{entre chaves}` por dados reais da agenda. Mantenha curto, humano e com
emoji so se combinar com o tom. Nunca mande textao.

Boas praticas que reduzem falta (no-show):
- Lembrete 2 dias antes (D-2) + pedido de confirmacao 1 dia antes (D-1).
- Sempre facilite remarcar na mesma mensagem ("se nao puder, me avisa que a gente
  acha outro horario").
- Personalize: nome, servico, profissional, data e hora.

---

## 1. Confirmacao do agendamento (na hora que marca)
> Oi, {cliente}! Aqui e da {negocio} 😊
> Seu {servico} com {profissional} ficou marcado para **{dia_semana}, {data} as {hora}**.
> Qualquer coisa e so me chamar por aqui. Ate la!

## 2. Lembrete D-2 (2 dias antes)
> Oi, {cliente}! So passando pra lembrar do seu {servico} na {dia_semana} ({data}) as {hora}, com {profissional}.
> Ta tudo certo pra voce? Se precisar mudar, me avisa que a gente ajeita 🙂

## 3. Confirmacao D-1 (1 dia antes - pedido de resposta)
> Oi, {cliente}! Seu {servico} e **amanha as {hora}** com {profissional}.
> Consegue confirmar pra mim? Responde **SIM** que ja deixo tudo separado.
> Se nao der, sem problema - me fala que remarco rapidinho.

## 4. Remarcacao (oferecendo horarios)
> Sem problema, {cliente}! Vamos achar outro horario.
> Tenho esses livres: {opcao_1}, {opcao_2}, {opcao_3}. Qual fica melhor pra voce?

## 5. Cancelamento (confirmando + reabrindo a porta)
> Tudo certo, {cliente}, cancelei seu {servico} de {data}.
> Quando quiser remarcar e so me chamar - sera um prazer te atender 🙏

## 6. Retorno (cliente na hora de voltar)
> Oi, {cliente}! Faz {tempo_desde_ultima} que voce fez seu ultimo {servico} com a gente.
> Costuma ser um bom momento pra renovar 😉 Quer que eu ja separe um horario essa semana?

## 7. Reativacao (cliente que sumiu)
> Oi, {cliente}! Senti sua falta por aqui 🙂 Faz um tempinho que voce nao aparece.
> Ta tudo bem? Se quiser voltar, te encaixo num horario tranquilo - e so dizer o dia.

## 8. Encaixe (abriu vaga, chamar da lista de espera)
> Oi, {cliente}! Abriu uma vaga pra {servico} **{data} as {hora}**.
> Lembrei que voce queria - quer que eu garanta pra voce? Responde rapidinho que e por ordem de chegada 🙂

---

### Dica de cadencia para a agenda do dia seguinte
1. Rode `python3 scripts/pauta.py dia amanha`.
2. Para quem ainda esta `agendado`, gere a mensagem **3 (D-1)**.
3. Marque `confirmado` conforme as pessoas respondem (`status --id N --para confirmado`).
4. No dia, quem nao compareceu vira `faltou` e entra na regua de reativacao.
