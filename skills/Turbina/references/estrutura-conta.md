# Estrutura de conta e planejamento de campanha

Guia para o modo **Planejar**. Objetivo: montar o esqueleto certo antes de gastar,
no caminho mais simples que resolve — sem complexidade prematura.

## A hierarquia (Meta e Google, em PT-BR de gente)

```
CAMPANHA        → define o OBJETIVO e (às vezes) o orçamento total
  └ CONJUNTO    → define o PÚBLICO, o orçamento e onde/quando aparece
      └ ANÚNCIO → o CRIATIVO (imagem/vídeo) + o TEXTO (copy) + o link/CTA
```

- No **Meta**, o conjunto de anúncios é onde mora o público e o orçamento.
- No **Google**, o equivalente é o *grupo de anúncios* (busca) ou a *campanha*
  (Performance Max / Demanda). A lógica de decisão é a mesma.

## Passo 1 — Cravar o "resultado"

Antes de tudo, defina o que conta como **resultado** desta campanha (é o que vai
virar CPA depois). Um só, claro:
- conversa/mensagem no WhatsApp ou Direct;
- lead (formulário/cadastro);
- venda no checkout;
- agendamento;
- (só quando faz sentido) visita ao site.

O objetivo da campanha no Gerenciador precisa **casar** com esse resultado (ex.:
objetivo "Vendas/Conversões" com o pixel medindo compra; "Cadastro" com formulário).
Objetivo errado = otimização errada = verba gasta com a pessoa errada.

## Passo 2 — Temperatura do público (frio → morno → quente)

Estruture os conjuntos pela relação da pessoa com o negócio:

| Temperatura | Quem é | Público típico | O que o anúncio faz |
|---|---|---|---|
| **Frio** | nunca te viu | interesses, lookalike, aberto (deixar a IA achar) | apresenta, gera o 1º clique |
| **Morno** | já interagiu | engajou no perfil, viu vídeo, visitou site | aprofunda, quebra objeção |
| **Quente (retargeting)** | quase comprou | add-to-cart, iniciou checkout, abriu conversa | fecha, lembra, oferece prova/urgência honesta |

Começando do zero, o mais simples que funciona:
- **1 campanha**, **2–3 conjuntos frios** (ex.: 1 lookalike + 1 interesse + 1 aberto),
  **1 conjunto de retargeting** (quando já houver público pra remarketing).
- Não crie 10 conjuntos no dia 1: verba dividida demais nunca sai do aprendizado.

## Passo 3 — Públicos, sem exagero

- **Lookalike / público semelhante:** parte de uma base boa (compradores, leads
  qualificados). Melhor ativo quando existe. 1% é mais parecido; 3–5% é mais amplo.
- **Interesses:** comece amplo; a plataforma de 2026 otimiza melhor com público maior
  do que com micro-segmentação. Não empilhe 30 interesses minúsculos.
- **Aberto / Advantage+ / sem segmentação:** deixe a IA da plataforma achar. Muitas
  vezes bate a segmentação manual — teste como um dos conjuntos frios.
- **Retargeting:** só depois de ter tráfego/base. Janelas comuns: 7, 14, 30 dias.
- **Evite sobreposição:** públicos muito parecidos em conjuntos diferentes competem
  no mesmo leilão (você dá lance contra si mesmo). Mantenha-os distintos.

## Passo 4 — Nomenclatura (pra exportação ficar legível depois)

Nomeie com padrão. Quando a Turbina for **ler a exportação**, nomes claros valem ouro:

```
[Objetivo]-[Temperatura]-[Público]-[Data]
Ex.: VENDA-FRIO-LookalikeCompradores-Jul
     LEAD-RETARGETING-VisitouSite14d-Jul
```

Anúncio: `[Formato]-[Ângulo]-[Versão]` → `VIDEO-ProvaSocial-v1`, `IMG-Oferta-v2`.
Assim, no diagnóstico, dá pra ver na hora qual ângulo/público está ganhando.

## Passo 5 — Distribuição inicial de verba

Sem histórico, um ponto de partida simples (ajuste depois pelos números):
- **~70%** no frio (é onde se acha cliente novo),
- **~20%** no morno,
- **~10%** no quente/retargeting (público pequeno, não precisa de muito).

Respeite o **orçamento mínimo por conjunto** para ele sair do aprendizado: como regra
de bolso, cada conjunto precisa de verba pra gerar ~**50 resultados/semana**. Se o
orçamento total não paga isso em todos os conjuntos, **tenha menos conjuntos** — não
espalhe fino.

## O que NÃO fazer no começo (evitar complexidade prematura)

- Não crie dezenas de conjuntos/anúncios "pra testar tudo": divide a verba e ninguém
  aprende.
- Não fique ligando/desligando campanha toda hora: reseta o aprendizado.
- Não confie em público minúsculo achando que "quanto mais específico melhor" — em
  2026 a plataforma otimiza melhor com espaço pra respirar.
- Não escale antes de ter sinal (ver `regras-otimizacao.md`).

## Entrega do modo Planejar

Um plano pronto pro dono montar no Gerenciador:
1. Objetivo da campanha + o que conta como resultado.
2. Lista dos conjuntos (temperatura + público) com a verba de cada um.
3. Quantos anúncios por conjunto e quais ângulos testar (a escrita vai pro **Verbo**).
4. Nomenclatura sugerida.
5. O que observar nos primeiros 3–4 dias antes de mexer.
