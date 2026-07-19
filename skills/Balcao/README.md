# Balcao 🛎️ — a recepcao que responde seu cliente na hora e do seu jeito

O **Balcao** e uma skill de Claude Code para donos de negocio de servico. Ele cuida do
**atendimento inbound**: aquelas mensagens que chegam o dia todo no WhatsApp/Instagram/e-mail
("Quanto custa?", "Que horas abre?", "Voces fazem X?", "Como uso o que comprei?", reclamacoes).
O Balcao guarda a **base de conhecimento** do seu negocio e te entrega a resposta pronta,
**consistente e no seu tom**, para voce so revisar e enviar.

A regra mais importante: **o Balcao nunca inventa.** Se a resposta nao esta na base, ele
nao chuta preco nem prazo — ele te avisa e guarda a pergunta para voce responder uma vez e
nunca mais precisar repetir.

## O que ele faz

- **Responder** — voce cola a mensagem do cliente, ele tria, busca na base e escreve a resposta no seu tom.
- **Triar** — chegaram varias mensagens? Ele prioriza (reclamacao e urgente primeiro).
- **Reclamacao** — acolhe, pede desculpa e aponta a solucao, sem discutir.
- **Base / FAQ** — monta e faz crescer o banco de perguntas e respostas do negocio.
- **Respostas-padrao** — saudacao, fora do horario, "ja te retorno", pos-venda, no seu tom.
- **Resumo** — mostra o que os clientes mais perguntam (candidatos a resposta-padrao/automacao).

Tudo fica **local** na sua maquina, em `.balcao/` (fora do controle de versao). Nada sai do seu computador.

## Instalacao

1. Descompacte o `Balcao.zip`.
2. Copie a pasta `Balcao` para dentro de `.claude/skills/` do seu projeto
   (ou para `~/.claude/skills/Balcao` para usar em qualquer projeto).
3. Abra o Claude Code nesse projeto. Na primeira vez, peca algo como
   *"configurar o Balcao para o meu negocio"* — ele vai te fazer algumas perguntas
   (servicos, precos, horarios, as perguntas que voce mais ouve) e montar sua base.
   Depois disso a configuracao se apaga sozinha e a skill fica pronta.

## Como usar no dia a dia

Voce so conversa, em portugues normal. Exemplos do que dizer ao Claude:

- *"Chegou essa mensagem: 'oi, quanto custa um oculos de grau?' — como respondo?"*
- *"Cola aqui 5 mensagens de clientes e me diz quais responder primeiro."*
- *"Esse cliente ta bravo porque o pedido atrasou, me ajuda a responder."*
- *"Adiciona na base: pergunta 'fazem entrega?' resposta 'sim, entregamos na cidade toda'."*
- *"O que meus clientes mais perguntam?"*

O Balcao escreve a resposta — **quem envia e voce.**

## Requisitos

- [Claude Code](https://claude.com/claude-code)
- Python 3 (ja vem no macOS/Linux; biblioteca padrao apenas — nao instala nada)

## Privacidade

Sua base de conhecimento e suas mensagens ficam so na sua maquina, em `.balcao/`.
A skill nao envia nada para lugar nenhum e nao manda mensagens sozinha — ela apenas
sugere a resposta para voce revisar e enviar.

## Licenca

MIT — veja `LICENSE`. Feito para a comunidade **Maestros da IA**.
