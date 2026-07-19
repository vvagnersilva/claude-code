# As etapas do funil (e quando avançar)

Todo negócio vive em **uma etapa por vez**. Avançar é uma decisão honesta: só
sobe quando o critério de saída foi cumprido. Inflar etapa (marcar "negociação"
um negócio que só recebeu uma proposta) estraga a previsão e engana o próprio
dono.

| Etapa | O que é | Critério para AVANÇAR (sair dela) | Prob. padrão | Esfria após |
|-------|---------|-----------------------------------|--------------|-------------|
| **Lead** | Contato novo, ainda cru. Apareceu um interessado, alguém pediu informação, um nome veio de indicação. | Passou nas 4 perguntas de qualificação (ver `qualificacao.md`). | 10% | 3 dias |
| **Qualificado** | Tem encaixe real: precisa do que você vende, tem verba e você fala com quem decide. | Aconteceu a primeira conversa de verdade (reunião, call, visita ou diagnóstico). | 25% | 5 dias |
| **Reunião** | Já houve a conversa que entende a dor e o caso de uso. | A proposta/orçamento foi enviada. | 45% | 5 dias |
| **Proposta** | Orçamento ou proposta entregue, com preço e escopo. | O cliente começou a discutir condições/preço (sinal de que vai fechar). | 60% | 4 dias |
| **Negociação** | Discutindo preço, prazo ou condições — perto do sim. | Contrato fechado ou desistência. | 80% | 3 dias |
| **Ganho** 🎉 | Fechou. Vira cliente. | — (saiu do funil) | 100% | — |
| **Perdido** | Não fechou. Sempre com o **motivo** registrado. | — (saiu do funil) | 0% | — |

## Por que a probabilidade sobe a cada etapa

A probabilidade padrão é uma estimativa honesta de quanto, em média, um negócio
naquela etapa costuma fechar no mercado de serviços. Ela serve para a
**previsão**: um negócio de R$ 10.000 em **Negociação (80%)** "vale" R$ 8.000
hoje; o mesmo valor ainda em **Lead (10%)** vale R$ 1.000. Isso evita comemorar
cedo demais e mostra onde está o dinheiro mais "quente".

O dono pode ajustar a probabilidade de um negócio específico com `--prob` quando
sentir que aquele caso é mais (ou menos) provável que a média da etapa.

## Por que negócio "esfria" mais rápido perto do fim

Quanto mais avançado o negócio, mais caro é deixá-lo parado: uma **proposta** sem
resposta há 4 dias ou uma **negociação** parada há 3 dias provavelmente está
esfriando — o cliente foi falar com concorrente, esqueceu, ou perdeu o impulso.
Um **lead** novo aguenta um pouco mais. Por isso o limite de "esfriando" é menor
nas etapas finais. Quando um negócio passa do limite, a Esteira avisa no `hoje` e
no `esfriando` para o dono dar um toque antes de perder.

## A regra de ouro do funil

> **Todo negócio em aberto precisa de um próximo passo com data.**

Negócio sem próximo passo definido é negócio que vai cair no esquecimento. Sempre
que mover para Proposta ou Negociação, combine: "quando você cobra a resposta?".
Esse hábito simples — um próximo passo com data — é o que mais aumenta a taxa de
fechamento.
