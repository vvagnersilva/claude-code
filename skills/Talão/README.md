# Talão — o talão de orçamentos do prestador de serviço

O **Talão** é uma skill de Claude Code que transforma "preciso fazer um orçamento"
no documento pronto pra mandar pro cliente. Você conta o serviço e o que entra
(material, mão de obra, custos); o Talão soma na conta certa — custo direto →
custo indireto → margem → desconto → imposto → **total** —, gera o orçamento com a
sua marca e ainda acompanha quem ficou sem responder. Tudo conversando em português,
sem comando nem código.

É para quem vende **trabalho por job**: instalação/HVAC, obra/reforma, manutenção,
edição de vídeo, design, marketing, eventos, consultoria — qualquer serviço que se
cobra por trabalho.

## O que ele faz
- **Orça**: monta a lista de itens separando material, mão de obra e custos, com
  coeficiente de perda/dificuldade e frete por item.
- **Precifica**: aplica custo indireto, margem, desconto e imposto na ordem certa,
  com centavo exato — e te mostra o lucro estimado (visão interna).
- **Emite**: gera um documento HTML lindo com a sua marca; é só abrir e imprimir
  em PDF pra enviar. O cliente vê itens e total — nunca o seu custo ou margem.
- **Acompanha**: marca enviado/aceito/recusado, avisa o que está sem resposta ou
  com validade vencendo, e sugere a mensagem de follow-up no seu tom.
- **Painel**: valor em aberto, valor fechado, taxa de aceite e ticket médio.

## Como instalar
1. Baixe e descompacte o `Talão.zip`.
2. Copie a pasta `Talão` para dentro de `.claude/skills/` do seu projeto
   (ou de `~/.claude/skills/` para usar em qualquer pasta).
3. Abra o Claude Code nessa pasta. Na primeira vez, diga algo como
   **"quero fazer um orçamento"** — o Talão roda uma conversa rápida de
   configuração (nome do negócio, marca, padrões de preço) e já começa.

## Como usar (você só conversa)
- "Preciso orçar a instalação de 3 splits pro Mercado Bom Preço."
- "Inclui 18 metros de tubulação a 38 reais o metro, com 10% de sobra."
- "Coloca 25% de margem e 5% de ISS, e parcela em 3 vezes."
- "Gera o PDF do orçamento."
- "Quais orçamentos estão sem resposta?"
- "Como está minha taxa de aceite?"

O Talão faz as contas e escreve o documento e as mensagens; **você** aprova o preço
e envia ao cliente.

## Regras de ouro
- Nunca inventa preço, quantidade ou custo — se faltar, ele pergunta.
- Sempre separa material e mão de obra e nunca esquece os custos invisíveis.
- O cliente vê só itens e total; seu custo e sua margem ficam só pra você.
- Você sugere, o dono decide e envia.
- Seus dados ficam 100% na sua máquina, na pasta `.talao/`. Nenhuma chave, nenhuma
  nuvem.

## Requisitos
- Claude Code.
- Python 3 (já vem no macOS e na maioria dos Linux) — o motor usa só a biblioteca
  padrão, sem instalar nada.

## Licença
MIT — veja `LICENSE`.
