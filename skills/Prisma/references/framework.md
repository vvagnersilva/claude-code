# As 6 faces do Prisma — o framework, com exemplos

Use esta referência ao **Criar** um prompt e ao **Ensinar**. As seis faces são a
checklist do que um bom pedido para IA precisa ter. Você não precisa citar os
nomes para a pessoa — eles são a sua bússola interna.

## As faces, uma a uma

| Face | Pergunta que ela responde | Exemplo de frase pronta |
|------|---------------------------|--------------------------|
| **1. Papel** | Quem a IA deve "vestir"? | "Você é um corretor de imóveis experiente em São Paulo." |
| **2. Objetivo** | O que eu quero, em uma frase? | "Escreva um anúncio para um apartamento de 2 quartos." |
| **3. Contexto** | O que a IA precisa saber? | "O prédio tem piscina, fica perto do metrô, e o público são famílias jovens." |
| **4. Formato** | Como a resposta deve sair? | "Em 3 parágrafos curtos, com um título chamativo e emojis no fim." |
| **5. Exemplo** | Como é um resultado bom? | "No estilo deste anúncio que funcionou: [cola um exemplo]." |
| **6. Limites** | O que evitar / regras? | "Tom acolhedor, sem clichê de imobiliária, não invente o preço." |

**Quanto mais faces preenchidas, melhor o resultado.** As três que mais salvam
um prompt são **Objetivo claro**, **Contexto** e **Formato**. Exemplo é o
"empurrão extra" quando a pessoa tem um modelo do que quer.

## Como montar (passo a passo)

1. Comece pelo **Objetivo** — a frase do que ela quer. Se estiver vago, é a 1ª
   pergunta a fazer.
2. Puxe **Papel** e parte do **Contexto** do `.prisma/config.md` (profissão, tom).
3. Pergunte o **Contexto** específico que falta e o **Formato** desejado.
4. Acrescente **Limites** (tom do perfil + "não invente dados" quando fizer
   sentido).
5. Se a pessoa tiver um modelo, peça e use como **Exemplo**.
6. Escreva tudo em prosa natural e ordenada — não precisa rotular as faces no
   texto final; o prompt deve ler como um pedido humano bem-feito.

## Exemplo completo — antes e depois

**Pedido cru da pessoa:**
> "preciso de um texto pra divulgar minha promoção de fim de ano"

**Prompt fraco (o que a maioria escreveria):**
> "Escreva um texto para divulgar minha promoção de fim de ano."
> → resultado genérico, serve pra qualquer um, esquecível.

**Prompt do Prisma (6 faces):**
> "Você é um redator de marketing que escreve para pequenos comércios locais
> *(Papel)*. Escreva uma mensagem de WhatsApp para anunciar minha promoção de
> fim de ano *(Objetivo)*. Sou dona de uma loja de roupas femininas numa cidade
> do interior; meu público são mulheres de 25 a 45 anos, e a promoção é 30% off
> em toda a coleção de verão até dia 23/12 *(Contexto)*. Quero uma mensagem
> curta, no máximo 4 linhas, com um emoji no começo e uma chamada clara para
> visitar a loja *(Formato)*. Tom animado e próximo, como quem fala com uma
> amiga; nada de parecer propaganda de banco, e não invente desconto além dos
> 30% *(Limites)*."
> → resultado específico, pronto pra enviar, com a cara do negócio.

## Mini-exemplos por face (para Afinar)

- **Faltou Formato?** "Responda em formato de tabela com 3 colunas."
- **Faltou Limite de tamanho?** "No máximo 150 palavras."
- **Veio com invenção?** "Use só as informações que eu dei; se faltar algo,
  pergunte em vez de inventar."
- **Tom errado?** "Reescreva num tom mais formal, para um cliente corporativo."
- **Faltou Exemplo?** "Siga o estilo deste texto que deu certo: [exemplo]."
