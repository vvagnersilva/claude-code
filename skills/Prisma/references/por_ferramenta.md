# Afinando o prompt para cada ferramenta de IA

O framework das 6 faces vale para tudo, mas cada ferramenta responde melhor a
certas ênfases. Ao **Criar**, ajuste o prompt à ferramenta que a pessoa vai usar
(está no `config.md` ou pergunte).

## Chat de texto (ChatGPT, Claude, Gemini, Copilot)
- **Papel e Contexto importam muito.** Comece dizendo quem a IA deve ser e dê o
  contexto antes do pedido.
- **Peça para a IA perguntar quando faltar dado:** "se precisar de alguma
  informação para fazer bem, me pergunte antes de escrever."
- **Para tarefas complexas, peça passo a passo:** "pense em etapas antes de
  responder" melhora a qualidade.
- **Formato explícito** (tópicos, tabela, tamanho) evita textão.

## Texto longo / documento (artigo, e-mail, proposta, post)
- Reforce **Exemplo** (um modelo do estilo) e **Limites de tom**.
- Dê a **estrutura desejada**: "introdução, 3 seções, conclusão com chamada".
- Diga o **público** dentro do Contexto — muda tudo o registro do texto.

## Gerador de imagem (gerador de imagem do ChatGPT, Gemini, Midjourney, etc.)
- A ordem que funciona: **assunto → estilo → composição → luz/cor → detalhes →
  o que evitar.**
- Seja **concreto e visual**: "foto", "ilustração plana", "aquarela", "ângulo de
  cima", "luz natural de fim de tarde", "fundo desfocado".
- **Diga o que NÃO quer** (Limites): "sem texto na imagem", "sem deformações nas
  mãos".
- Formato/proporção conta: "imagem quadrada para Instagram", "horizontal 16:9".
- Menos "papel/persona", mais descrição da cena. Aqui o Contexto é a CENA.

## Claude Code / assistente que mexe em arquivos
- Seja **específico sobre o resultado e onde**: "crie um arquivo X com…", "ajuste
  só a parte Y".
- Peça **um passo de cada vez** e que confirme antes de mudanças grandes.
- Dê o **critério de pronto**: "está pronto quando rodar sem erro e fizer Z".

## Regra geral
Se a pessoa não sabe qual ferramenta combina, o prompt das 6 faces funciona em
qualquer uma — só ajuste a ênfase acima. Quando salvar na biblioteca, registre a
ferramenta com `--ferramenta` para lembrar onde aquele prompt brilha.
