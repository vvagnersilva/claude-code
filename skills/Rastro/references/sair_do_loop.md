# Sair do loop — pare de queimar tokens

Este é o modo de emergência: você (ou a própria IA) está travado, girando em círculos, e
cada conserto quebra outra coisa. É exatamente aqui que a assinatura vai embora. A saída
não é "tentar mais forte" — é PARAR e resetar.

---

## Sinal de que você está no loop
- Cada correção revela um novo estado compartilhado / acoplamento.
- Cada correção cria um sintoma novo em outro lugar.
- As correções começam a exigir "refatoração enorme".
- Você já reverteu e re-aplicou a mesma ideia mais de uma vez.
- Você não consegue mais explicar por que o código faz o que faz.

## Protocolo de resgate (rode na hora)
1. **PARE.** Feche o arquivo que você está encarando. Pare de digitar correção.
2. **Reverta TUDO.** Volte as correções empilhadas ao estado anterior (`git checkout`/`git
   revert` do que você mexeu). Patch em cima de patch não tem conserto — só limpando dá pra ver de novo.
3. **Releia o erro do topo.** A mensagem literal, do começo. Não o resumo.
4. **Separe fato de hipótese.** Escreva duas listas:
   - **O que eu SEI** (só fatos observados: o erro X, na linha Y, com a entrada Z).
   - **O que eu NÃO SEI** (as incógnitas — esses são seus alvos de investigação).
5. **Ataque UMA incógnita.** Escolha uma da segunda lista e investigue só ela, com evidência. Uma de cada vez.

Isso zera o loop e te devolve ao método (reproduzir → evidência → uma hipótese).

---

## A regra das 3 quedas
Conte as tentativas de correção que falharam:
- **1-2 falhas** → volte à investigação com evidência nova (Fase 2 do loop).
- **3 ou mais falhas** → **PARE de corrigir.** O problema quase nunca é "mais um patch" —
  é a arquitetura. Sinais de problema arquitetural: cada correção destrava um novo
  acoplamento; cada correção pede refatoração grande; cada correção cria sintoma novo.
  
  **Questione os fundamentos, com o dono:**
  - Esse padrão/abordagem é sólido, ou está lutando contra o desenho do sistema?
  - Vale refatorar a arquitetura em vez de continuar consertando sintoma?
  - **Converse com o dono antes de tentar mais correções.** Três quedas é o sinal de que a
    decisão saiu do "conserto" e virou "redesenho" — e essa é uma decisão do dono, não um chute a mais.

---

## Por que isto economiza tokens (e dinheiro)
Cada patch empilhado sem causa-raiz adiciona contexto, gera código novo pra revisar, e
puxa a IA para consertar o sintoma do patch anterior — o gasto cresce em espiral. Projetos
tocados sem esse freio gastam de 4 a 6 vezes mais tokens que os que param, entendem e
corrigem na origem. Parar cedo (3 quedas) e reverter tudo é, quase sempre, o movimento mais
barato que existe.
