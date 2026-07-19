# Como classificar a severidade da não-conformidade

A severidade orienta a **prioridade do conserto**. Classifique pelo **risco real** e pelo
**peso da exigência**, nunca pelo "tamanho" aparente do problema. Na dúvida entre dois
níveis, suba um (mais conservador) e explique o porquê ao usuário. Nunca infle para
assustar nem minimize para agradar.

| Nível | Quando usar | Exemplos | Prazo típico |
|-------|-------------|----------|--------------|
| 🔴 **Crítica** | Risco grave/iminente à vida, à saúde, ao dado sensível ou ao negócio; descumprimento legal sério; algo que reprova a auditoria/fiscalização na hora | Máquina sem proteção no ponto de operação; saída de emergência trancada; vazamento de dados pessoais; alvará vencido | Imediato / interromper a atividade |
| 🟡 **Maior** | Descumpre um **requisito obrigatório** da norma, mas sem risco iminente; lacuna que, se não tratada, vira crítica | Procedimento LOTO inexistente; falta de registro de treinamento obrigatório; sem base legal documentada para um tratamento de dados | Curto (dias a poucas semanas) |
| 🟢 **Menor** | Desvio pontual, isolado, de baixo impacto; conformidade existe mas com falha | Sinalização desbotada; um EPI fora do lugar; documento na versão antiga num posto | Médio prazo |
| 🔵 **Observação** | Não é não-conformidade — é **oportunidade de melhoria** ou ponto de atenção | Sugestão de melhorar um fluxo já conforme; risco que ainda não se concretizou | Quando possível |

## Critérios de apoio (risco = probabilidade × consequência)
- **Consequência**: o que acontece de pior se isso falhar? (morte/lesão grave → crítica;
  multa/autuação → maior; retrabalho/incômodo → menor)
- **Probabilidade/abrangência**: acontece sempre e em todo lugar, ou foi um ponto isolado?
  Algo sistêmico pesa mais que um caso único.
- **Exigência legal**: se a norma diz "deve/obrigatório" e não está cumprido → no mínimo
  **Maior**. Se o descumprimento expõe a vida ou para a operação → **Crítica**.

## Causa-raiz (faça SEMPRE para Crítica e Maior)
Tratar o sintoma faz a não-conformidade **voltar**. Use os **5 porquês** para chegar na
causa real antes de escrever a ação:

> NC: a proteção da prensa não estava instalada.
> 1. Por quê? → Foi removida na última manutenção.
> 2. Por quê não foi recolocada? → Não há passo de "recolocar e conferir" no procedimento.
> 3. Por quê o procedimento não cobre isso? → O procedimento de manutenção nunca foi revisado.
> 4. Por quê não foi revisado? → Não há rotina de revisão de procedimentos.
> **Causa-raiz:** ausência de procedimento de manutenção com verificação de proteções.
> **Ação corretiva** (ataca a causa): criar o passo de verificação + rotina de revisão —
> não apenas "recolocar a proteção" (isso é só a correção imediata).

Dica: pare quando o "porquê" vira algo que dá para **mudar no sistema/processo** (não em
"a pessoa foi descuidada"). Causa-raiz boa aponta para um conserto que impede a repetição.

## Não confunda achado com opinião
Cada NC precisa de **evidência objetiva** (o que foi visto, medido, lido). "Acho que está
ruim" não é não-conformidade. "O extintor está com a recarga vencida desde 03/2026
(etiqueta)" é.
