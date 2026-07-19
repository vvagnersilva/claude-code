# Indicacao — boca a boca de proposito

Cliente feliz indica — mas quase nunca por conta propria. Basta pedir, na hora certa e
do jeito certo. Indicacao tras o cliente de **maior confianca** e menor custo.

## Duas formas

### A) Pedido pontual (comece por aqui)
Pedir a 1 cliente satisfeito que indique alguem. Simples, sem custo, alta conversao.
- Momento: logo apos um elogio ou bom resultado (mesmos gatilhos de `momentos.md`).
- Seja **especifico**: nao diga "indica ai pros amigos". Diga "voce conhece alguem que
  tambem esta passando por <problema que voce resolve>?". Quanto mais especifico, mais o
  cerebro do cliente encontra um nome.
- Sem pressao. Um "nao" tranquilo preserva o relacionamento.

Molde (adapte ao tom do dono):
> "Que bom que voce gostou, <nome>! Posso te pedir um favor? Se voce conhece alguem que
> tambem precisa de <servico/resultado>, sinta-se a vontade para passar meu contato — e
> sempre um prazer atender quem vem da sua indicacao. 🙏"

### B) Programa simples de indicacao
Um incentivo claro e honesto para quem indica. Bom quando ja ha volume de clientes felizes.
- **Recompensa sustentavel**: desconto no proximo servico, um brinde, um bonus — algo que
  caiba no seu bolso e nao vire prejuizo. Evite prometer o que nao consegue manter.
- **Regras simples** (2 linhas): quem indica ganha X quando o indicado fecha. Sem letra miuda.
- **Recompense rapido** quando der certo — isso faz a pessoa indicar de novo.
- Cuidado: indicacao premiada e diferente de **comprar avaliacao** (proibido). Recompense a
  indicacao que vira cliente, nunca uma nota/review.

## Acompanhamento (use o motor)
- Registre o pedido: `add-ind --quem-indicou "<nome>" --indicado "<nome ou ?>" --status pedido`.
- Quando a pessoa indicar de fato: `set-ind --id <n> --status indicou`.
- Quando o indicado fechar: `set-ind --id <n> --status virou_cliente`.
- Quando recompensar quem indicou: `set-ind --id <n> --status recompensado`.
- O Painel (`resumo`) mostra quantas indicacoes estao em aberto e quantas viraram cliente.

## Boas praticas
- **Agradeca sempre** quem indica, mesmo que o indicado nao feche. Reconhecimento sustenta o boca a boca.
- Peca indicacao a quem ja te elogiou ou ja e cliente fiel — nao a quem mal te conhece.
- 1 pedido bem feito vale mais que 10 disparos genericos.
