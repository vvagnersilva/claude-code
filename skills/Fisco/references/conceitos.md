# Conceitos fiscais em português de gente (guia da IA)

Este arquivo é o seu roteiro para **explicar** o que confunde o dono de negócio.
Regra número um: **explique o CONCEITO, nunca crave a alíquota atual**. Alíquotas e
faixas mudam por atividade, faturamento e ano — o número exato é do contador ou do
extrato do DAS. Se o dono quiser o número, diga **onde ele aparece**, não invente.

Fale como quem explica para um amigo. Sempre puxe o exemplo para a **atividade do
dono** (que está no `.fisco/config.md`).

---

## Os regimes tributários (o "plano" de imposto do negócio)

Pense no regime como o **plano de imposto** que a empresa escolhe. Cada um tem uma
lógica de cobrança diferente.

- **MEI (Microempreendedor Individual)** — o plano mais simples, para quem fatura pouco
  (há um teto anual). Paga um **valor fixo por mês** (o DAS do MEI), não uma porcentagem.
  Tem limites de atividade e não pode ter mais que um funcionário. Bom para começar; a
  pessoa "sai" do MEI quando cresce.
- **Simples Nacional** — junta vários impostos numa **guia só** (o DAS) e a alíquota é uma
  **porcentagem do faturamento** que cresce por faixa. É o regime da maioria dos pequenos
  negócios de serviço. Divide as atividades em **Anexos** (III e V são os de serviço).
- **Lucro Presumido** — o governo "presume" uma margem de lucro sobre o faturamento e
  cobra os impostos sobre essa base. Os impostos vêm **separados** (não numa guia só).
  Costuma fazer sentido para quem fatura mais alto ou tem folha pequena.
- **Lucro Real** — imposto sobre o lucro **de verdade** (receita menos despesas
  comprovadas). Mais trabalhoso; comum em empresas maiores ou com margem baixa.

**Como explicar a escolha:** "Não existe o melhor pra todo mundo — depende do seu
faturamento, da sua folha de pagamento e da sua atividade. Dá pra ter uma ideia da
direção (modo Regime), mas a conta oficial e a decisão são com o contador."

---

## O DAS (a guia do Simples)

- **DAS = Documento de Arrecadação do Simples Nacional.** É a **guia única** que junta os
  impostos do Simples num boleto só, pago **todo mês**.
- Vence, em regra, **no dia 20** do mês seguinte ao faturamento (se cair em fim de semana/
  feriado, costuma ir para o próximo dia útil — **confirme com o contador**).
- O valor sai de uma porcentagem do seu faturamento (a **alíquota efetiva** da sua faixa).
  Onde você vê o número real: no **PGDAS-D** / extrato do Simples que o contador gera.

---

## Obrigação acessória (o "dever de informar")

- Além de **pagar** o imposto (obrigação principal), a empresa tem que **informar** coisas
  ao fisco: declarações, arquivos, a própria emissão de nota. Isso é a **obrigação
  acessória** — o "dever de contar o que aconteceu", mesmo quando não há imposto a pagar.
- Exemplos que o dono ouve: **DEFIS** (declaração anual do Simples), **DCTF**, **EFD**,
  **SPED**, a entrega da **nota fiscal**. Não precisa decorar as siglas — o importante é
  entender que **esquecer uma obrigação acessória também gera multa**, por isso o
  **calendário** (modo 3) existe.

---

## Fator R (a regra dos 28% no Simples)

- Algumas atividades de serviço podem cair no **Anexo III** (alíquotas menores) ou no
  **Anexo V** (maiores) — e o que decide é o **Fator R**.
- **Fator R = folha de pagamento dos últimos 12 meses ÷ faturamento dos últimos 12 meses.**
  Se der **28% ou mais**, a atividade tende ao **Anexo III** (mais barato). Se der **menos
  de 28%**, tende ao **Anexo V** (mais caro).
- "Folha" aqui inclui **pró-labore** (a retirada do dono) + salários + encargos.
- É por isso que às vezes **aumentar o pró-labore** faz o imposto cair — mas nem sempre
  compensa (você paga mais INSS na folha). O modo Regime calcula o Fator R; a decisão de
  mexer nele é **com o contador**.

---

## ISS, retenção e nota fiscal de serviço

- **ISS (Imposto Sobre Serviços)** é **municipal** — a alíquota varia de cidade para cidade
  (dentro de uma faixa). Quem presta serviço emite **nota fiscal de serviço** (NFS-e) pela
  prefeitura.
- **Retenção**: em alguns casos, quem **contrata** o serviço já desconta (retém) parte do
  imposto e recolhe no lugar do prestador. Aparece como "ISS retido" ou "retenção de
  federais". Se o dono vê descontos na nota que não entende, é provavelmente retenção —
  vale conferir com o contador para não pagar duas vezes.

---

## Como você (IA) deve responder sobre esses conceitos

1. **Conceito primeiro, número depois** — explique a ideia; para o valor exato, aponte a
   fonte (extrato do DAS, contador) em vez de inventar.
2. **Um exemplo da atividade do dono** — "no seu caso, de [atividade], normalmente…".
3. **Feche com o lembrete** — "confirme com o seu contador; isto não é parecer contábil".
4. **Nunca** diga "você paga X%" como se fosse oficial. Diga "a sua alíquota efetiva
   aparece no seu DAS; quer que eu te ajude a organizar isso?".
