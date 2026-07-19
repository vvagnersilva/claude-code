# Como o Leme decide a ordem (método de priorização)

Este guia explica, em português simples, como o `leme.py` calcula a prioridade.
Leia antes de justificar a ordem para o dono — a confiança vem de explicar o porquê.

## A nota é uma soma de fatores (e cada ponto é rastreável)

Cada tarefa ganha uma **nota**. Quanto maior, mais cedo ela deve ser feita. A
nota é a soma de pedaços, e o motor sempre devolve de onde veio cada pedaço:

| Fator | Peso | O que significa |
|-------|------|-----------------|
| Prazo chegando | até **+12** | quanto mais perto (ou passado) o `vence_em`, mais alto |
| Importante | **+9** | o dono marcou como importante |
| Urgente | **+7** | o dono marcou como urgente |
| Tempo parada | até **+2** | tarefa antiga na fila sobe devagar (não deixa cair no esquecimento) |
| Tem projeto | **+1** | está associada a uma área/projeto |
| Bloqueada | **−8** | está esperando algo/alguém → desce na fila de hoje |

Exemplo real: "subiu porque é importante (+9), o prazo está chegando (+8) e é
urgente (+7)". Some tudo e você tem a nota. **Nunca** apresente uma ordem sem o
motivo — o `leme.py` já entrega o motivo pronto no campo "por quê".

## O prazo não é "tem ou não tem" — ele tem uma curva

O peso do prazo cresce suave conforme a data se aproxima:

- vence daqui a mais de 2 semanas → quase não conta (piso baixo);
- vai chegando perto → o peso sobe de forma gradual;
- venceu há uma semana ou mais → peso máximo (e fica nesse teto).

Por isso uma tarefa que venceu ontem pesa mais que uma que vence só mês que vem,
mesmo que as duas sejam "importantes".

## As duas perguntas que importam (matriz de Eisenhower)

No momento de capturar, só duas perguntas decidem o quadrante:

|  | **Importante** | **Não importante** |
|--|----------------|--------------------|
| **Urgente** | **Faça agora** | **Delegue** (alguém pode fazer?) |
| **Não urgente** | **Agende** (marque um dia) | **Avalie/elimine** (precisa mesmo?) |

O dono responde "é urgente?" e "é importante?"; o quadrante orienta a conversa e
os pesos entram na nota. Simples para quem responde, preciso para quem calcula.

## As "3 de hoje"

Depois de calcular tudo, o Leme mostra só as **3 tarefas de maior nota que não
estão bloqueadas** como as "3 de hoje". O resto vira "depois". O limite de 3 é
de propósito: para quem está atolado, foco vale mais que uma lista enorme. As
bloqueadas ficam à parte, lembrando o que precisa destravar.

## A revisão da semana (ritual GTD)

Uma vez por semana, o `revisar` separa a lista em 4 quadros:

1. **Concluídas (últimos 7 dias)** — comemore o que andou.
2. **Atrasadas** — o prazo passou: concluir ou remarcar?
3. **Paradas** — abertas há mais de 2 semanas sem andar. Para cada uma, a
   pergunta clássica: **fazer agora, agendar, delegar ou eliminar?**
4. **Sem data** — abertas sem prazo: defina um "quando".

Feche a revisão pedindo ao dono para escolher as **3 tarefas-chave da próxima
semana** e marcá-las como importantes. Assim a próxima semana já começa com o
leme apontado para o que importa.
