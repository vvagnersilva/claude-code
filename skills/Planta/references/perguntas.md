# Banco de perguntas do Briefing (levantamento)

Conduza como um consultor curioso e simpático, **uma pergunta de cada vez**, em
português simples, na linguagem do cliente. Não despeje tudo de uma vez. Pule o
que já foi respondido. O objetivo é entender o processo de verdade **antes** de
desenhar ou orçar qualquer coisa.

> Regra: se o cliente não souber um número (volume, tempo), registre como
> **[CONFIRMAR]** e siga — nunca chute como se fosse fato.

## Bloco 1 — Contexto do negócio
1. O que o negócio faz e quem é o cliente dele?
2. Qual o **setor** (saúde, jurídico, imóveis, varejo, serviços...)? Serve pra
   dar exemplos certos e calibrar a solução.
3. Quantas pessoas tocam o processo que vamos automatizar?

## Bloco 2 — O processo atual (o coração do briefing)
4. Me conta **passo a passo** como isso funciona hoje, do começo ao fim.
5. Em cada passo: **quem faz**, **em qual ferramenta** e **quanto tempo leva**?
6. Onde mais **trava, atrasa ou dá erro**? (o gargalo)
7. O que acontece quando dá errado hoje? (cliente reclama, perde venda, retrabalho)

## Bloco 3 — Ferramentas que já existem
8. Quais ferramentas o negócio **já usa** no dia a dia? (WhatsApp, planilha,
   e-mail, sistema/ERP, CRM, agenda, formulário, Instagram...)
9. Tem algum sistema onde os dados já ficam guardados? Dá pra exportar/entrar?
10. O cliente já paga por alguma ferramenta de automação (n8n, Make, Zapier)?
    *(Se NÃO usa nenhuma, NÃO empurre — resolva com o que ele já tem.)*

## Bloco 4 — Volume e dados
11. **Quantas vezes** isso acontece por dia/semana/mês? (volume = tamanho do ganho)
12. Os dados de entrada vêm de onde e em que formato? (mensagem, planilha, PDF, formulário)
13. Tem dado sensível/pessoal envolvido? (pra tratar com cuidado e respeitar LGPD)

## Bloco 5 — Resultado e sucesso (NÃO pule)
14. Se isso funcionasse perfeitamente, **o que mudaria na prática?** (o **output**)
15. Qual **número** mostraria que deu certo? (de **X** para **Y** — ex.: "responder
    de 4h para 30 min", "no-show de 30% para 10%", "5h/semana de volta")
16. Quanto vale **a hora** de quem faz isso hoje? (entra no cálculo de ROI)

## Bloco 6 — Restrições
17. Tem **prazo** ou data limite? Por quê?
18. Tem orçamento em mente? (pra calibrar a ambição da solução — não pra dar preço agora)
19. Quem **decide** e quem **aprova**? Mais alguém precisa dar o ok?

## Fechamento do briefing
- Resuma em **3-4 frases** o que entendeu (processo, dor, output, métrica) e
  **confirme com o usuário**: "É isso? Faltou algo?"
- Só depois de confirmado, registre o projeto:
  `planta.py novo --cliente "..." --setor "..."` e
  `planta.py info --proj <slug> --output "..." --metrica "..."`.
- Anote o que ficou como **[CONFIRMAR]** pra perguntar ao cliente antes da proposta.
