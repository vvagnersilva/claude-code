# Custos, margem e impostos — a ordem certa da conta

O Talão monta o preço sempre na mesma ordem, porque a ordem muda o resultado. Use
isto para entender e explicar cada etapa ao dono em PT-BR simples.

## A ordem (o motor já faz assim)

1. **Custo direto** — o que o trabalho consome de verdade.
   - Cada item: `valor unitário × quantidade × coeficiente + frete`.
   - O **coeficiente** (`--coef`) cobre perda/sobra de material e dificuldade.
     Ex.: cano de cobre quase sempre sobra → `--coef 1.1` (10% a mais). Telhado de
     difícil acesso → coeficiente maior na mão de obra.
   - Soma material + mão de obra + serviço + custo = **custo direto**.

2. **+ Custo indireto (overhead)** — o que o negócio gasta para existir e que não
   aparece no item: telefone, ferramenta, deslocamento médio, administração,
   impostos fixos, software. Entra como um **percentual sobre o custo direto**
   (`--overhead`). Pequeno prestador costuma trabalhar entre **8% e 20%**. Se o
   dono nunca calculou, comece com 10–12% e ajuste.

3. **+ Margem (lucro)** — o que sobra pra você depois de pagar tudo
   (`--margem`, % sobre a base de custo). Não confunda com "preço alto": margem é a
   saúde do negócio. Faixas comuns por tipo de serviço:
   - Serviço com muito material (instalação, obra): **15% a 30%**.
   - Serviço de mão de obra/conhecimento (consultoria, design, edição): **40% a 100%+**.
   - Quanto mais especializado e menos concorrência, maior a margem defensável.

4. **− Desconto** — abatimento sobre o subtotal, em **R$** (`--desconto`) ou em
   **%** (`--desconto-pct`). Aplicado ANTES do imposto, porque você não paga
   imposto sobre o que abriu mão.

5. **+ Imposto** — percentual sobre a base já com desconto (`--imposto`). Por
   padrão o motor soma o imposto **por fora** (cliente paga o imposto em cima).
   - **ISS** (serviço): costuma ser **2% a 5%** conforme o município e a atividade.
   - **Simples Nacional**: a alíquota efetiva varia por faixa de faturamento e
     anexo (geralmente entre ~6% e ~16% para serviços). Use a alíquota efetiva do
     contador do dono — **nunca chute**; se ele não souber, oriente a confirmar com
     o contador e deixe o campo em 0 até lá.
   - Se o dono é MEI ou não destaca imposto, deixe `--imposto 0`.

6. **= TOTAL ao cliente** e, se parcelado, **total ÷ parcelas** (`--parcelas`).

## Regras práticas
- **Imposto sempre depois do desconto.** O motor já garante isso.
- **Margem é sobre o custo, não sobre o preço final.** O `calcular` mostra o lucro
  estimado em R$ e em % sobre o custo para o dono validar.
- **O cliente não vê custo nem margem.** O documento (`html`) traz só itens e
  total. A quebra de custo/margem é interna (`calcular`).
- **Quando faltar um número, pergunte.** Preço de material muda toda semana —
  oriente o dono a confirmar o valor atual antes de enviar, e use a **validade**
  para se proteger.
