# Consertar um prompt — do sintoma à face que faltou

Use no modo **Consertar**. A pessoa cola o prompt que usou e descreve o que veio
errado. Cada sintoma quase sempre aponta para uma das 6 faces ausente ou fraca.
Diagnostique, explique em 1-2 linhas e devolva o prompt corrigido.

## Tabela de sintomas → causa → conserto

| Sintoma ("o resultado veio…") | Face que faltou | Como consertar |
|-------------------------------|-----------------|----------------|
| **Genérico, vago, "serve pra qualquer um"** | Contexto + Objetivo | Acrescente detalhes do negócio/situação e deixe o objetivo numa frase específica. |
| **Sobre outra coisa / fugiu do tema** | Objetivo | Reescreva o objetivo como UMA frase direta, no começo do prompt. |
| **Formato errado (veio texto, eu queria lista)** | Formato | Diga exatamente o formato: lista, tabela, e-mail, nº de itens, tamanho. |
| **Longo demais / curto demais** | Formato (tamanho) | Fixe o tamanho: "no máximo 150 palavras" / "em 5 bullets". |
| **Inventou dados, preço, nome, estatística** | Limites | Acrescente: "use só o que eu informei; se faltar, pergunte — não invente". |
| **Tom errado (formal demais / informal demais)** | Limites (tom) + Papel | Defina o tom e dê um Papel coerente ("você é um atendente simpático"). |
| **Não parece comigo / sem a minha voz** | Papel + Exemplo | Dê um exemplo de texto seu e peça para seguir o estilo. |
| **Bom, mas faltou profundidade / raso** | Exemplo + Contexto | Mostre um modelo de "bom" e dê mais contexto do porquê. |
| **Resposta em inglês / idioma errado** | Limites (idioma) | "Responda em português do Brasil." |
| **Ignorou parte do pedido** | Objetivo com itens demais | Quebre em passos numerados ou peça uma coisa de cada vez. |

## Como devolver o conserto

1. **Diga o que faltava** (curto e gentil): "O resultado veio genérico porque o
   prompt não dava contexto do seu negócio nem o formato de saída."
2. **Entregue o prompt consertado** em bloco copiável, já com as faces que
   faltavam preenchidas.
3. **Ensine de leve:** "Da próxima vez, sempre diga *para quem* é e *em que
   formato* você quer — é o que mais muda o resultado."
4. Ofereça **guardar a versão boa** na biblioteca para não refazer.

## Exemplo

**Prompt da pessoa:**
> "faz um resumo dessa reunião"
**Reclamação:** "veio enorme e sem as decisões que importam."

**Diagnóstico:** faltou **Formato** (o que destacar e o tamanho) e **Objetivo**
(o foco do resumo).

**Prompt consertado:**
> "Resuma a reunião abaixo em no máximo 10 linhas, destacando só: (1) as
> decisões tomadas, (2) quem ficou responsável pelo quê e (3) os prazos. Ignore
> conversa solta. Escreva em tópicos. Texto da reunião: [cole aqui]."
