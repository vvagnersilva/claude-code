# Comparar regime — direcional e honesto (guia da IA)

Objetivo: ajudar o dono a entender **qual regime tende a valer mais a pena**, sempre como
**estimativa para validar com o contador**. Aqui mora o maior risco de "inventar número" —
então siga as regras abaixo à risca.

## Regra de ouro (não negociável)
- O motor **NUNCA** embute uma tabela de alíquotas. As alíquotas mudam por atividade
  (CNAE), faixa de faturamento, ISS do município e ano — e ainda vão mudar com a Reforma.
- A alíquota efetiva **vem sempre do dono/contador**, nunca de você. Se o dono não tem os
  números, **explique onde conseguir** e **não invente**.
- Toda saída deste modo fecha com: "isto é só a matemática das alíquotas informadas; a
  decisão é com o contador; não é parecer contábil".

---

## Passo 1 — Fator R (seguro, é só uma razão)

Comece por aqui quando a atividade é de serviço. É **razão pura**, sem alíquota:
```
python3 scripts/fisco.py fator-r --receita-anual "R$ 600.000" --folha-anual "R$ 180.000"
```
- **Fator R = folha 12m ÷ receita 12m.** ≥ 28% tende ao **Anexo III** (mais barato);
  < 28% tende ao **Anexo V** (mais caro).
- "Folha" = pró-labore + salários + encargos dos últimos 12 meses.
- Se der abaixo de 28%, o motor mostra quanto a folha precisaria subir para cruzar a linha.
  **Aumentar pró-labore** pode reduzir o imposto do Simples, mas aumenta o INSS da folha —
  **nem sempre compensa**. Diga isso e mande simular com o contador.

## Passo 2 — Onde o dono acha as alíquotas efetivas

Para comparar Simples x Presumido, você precisa de **duas alíquotas efetivas**. Explique
onde cada uma aparece:
- **Simples:** a alíquota efetiva do mês está no **extrato do PGDAS-D** (o contador gera) ou
  dividindo o **valor do DAS ÷ faturamento** do mês. Ex.: DAS de R$ 5.600 sobre R$ 50.000 de
  faturamento = 11,2% efetivo.
- **Lucro Presumido:** a carga efetiva não é uma tabela fixa — some as guias (PIS, COFINS,
  ISS, IRPJ, CSLL) de um mês típico e divida pelo faturamento, OU peça ao contador uma
  **simulação de Presumido**. Nunca chute; peça o número.

## Passo 3 — A comparação (aritmética sobre os números informados)

```
python3 scripts/fisco.py comparar --receita-mensal "R$ 50.000" --simples-aliq "11,2%" --presumido-aliq "16,33%"
```
- O motor multiplica a receita por cada alíquota, mostra o imposto/mês e /ano de cada e diz
  qual sai mais barato **pelos números informados**.
- Leia em voz simples: "com as alíquotas que você me passou, o Simples fica R$ X/mês mais
  barato — mas isso muda se o seu ISS, o Fator R ou a atividade forem diferentes. Leva essa
  simulação pro contador confirmar."

---

## Sinais que ajudam a orientar a conversa (sem cravar)

Use como **contexto qualitativo**, não como regra fixa:
- **Presumido tende a ganhar** quando o faturamento é mais alto, a **folha é pequena**
  (Fator R baixo, jogando o serviço no Anexo V caro) e a margem é boa.
- **Simples tende a ganhar** quando o faturamento é menor/médio e a folha é relevante
  (Fator R ≥ 28%, Anexo III).
- Com **modelos enxutos/automatizados** (pouca folha), bater os 28% de Fator R virou
  difícil — por isso cada vez mais serviço de margem alta simula o Presumido. **Simular**,
  não presumir.
- **A Reforma pode mudar essa conta** nos próximos anos — mais um motivo para revisar com o
  contador periodicamente, não decidir uma vez e esquecer.

## Como você (IA) NUNCA deve agir
- ❌ "Você paga 6% no Simples" (cravou alíquota).
- ❌ "Mude para o Presumido que você economiza R$ X" (decidiu pelo dono).
- ✅ "Pelos números que você me deu, a direção é essa — leva pro contador confirmar e decidir."
