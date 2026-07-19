# Transformar elogio em prova social

Um depoimento guardado num CSV nao vende nada. Prova social so funciona quando aparece
para quem ainda esta decidindo. Aqui estao os formatos — todos feitos **so com frases
reais do cliente** e **so com consentimento**.

## Antes de tudo
- Use apenas depoimentos com `consent=sim` (cheque `list-dep`). Sem permissao = nao publica.
- **Nunca invente** numero, case, nota ou frase. Se o cliente nao disse, nao existe.
- Prefira o **especifico** ao generico: "tirei 2 dentes sem dor" vale mais que "otimo profissional".

## Formatos

### 1) Card de depoimento (post/story/site)
- Frase curta do cliente (a parte mais forte), nome (ou "M.S." se a pessoa preferir discricao), e o servico.
- 1 linha de contexto: o problema que ele tinha antes.
- Visual simples: aspas grandes + nome embaixo. (O dono monta no Canva; o Aplauso entrega o texto.)

### 2) Secao "O que dizem nossos clientes"
- 3 a 5 depoimentos curtos, variados (servicos/perfis diferentes), para site, proposta ou apresentacao.
- Ordene do mais forte para o mais simples.

### 3) Trecho para proposta / orcamento
- 1 depoimento que combine com o servico que esta sendo vendido naquela proposta.
- Encaixe perto do preco ("veja o que a <nome> falou de um trabalho parecido").
- Conecta com a skill de proposta/orcamento, se o dono usar uma.

### 4) Bio / destaque fixo
- A melhor frase, curtissima, para bio do Instagram, assinatura de e-mail ou destaque ("⭐ 4,9 no Google — veja").

### 5) Post de prova social (no tom do dono)
- Conte a historia: situacao do cliente -> o que foi feito -> resultado nas palavras dele -> convite leve.
- Aplique o anti-IA do `tom_de_voz.md`: sem clichê, sem "transforme sua vida", sem regra de tres decorativa.
- Pergunte ao dono se pode marcar/citar o cliente (consentimento tambem vale para post).

## Pedido de permissao (quando consent=nao)
Mensagem curta para liberar o uso:
> "Oi <nome>! Seu retorno foi tao bacana que queria poder mostrar para outras pessoas.
> Posso usar seu depoimento (so o texto, do jeito que voce quiser aparecer — nome
> completo, so inicial, ou anonimo)? Sem problema se preferir que nao 🙂"
Depois do "sim", atualize: `add-dep ... --consent sim` ou marque no registro existente.
