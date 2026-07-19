# Pauta — sua agenda cheia e ninguém falta

Pauta é uma skill do Claude Code que cuida do ciclo do **cliente recorrente** de
qualquer negócio de serviço — clínicas, barbearias, salões, consultórios,
restaurantes e consultorias. Ela ajuda você a **marcar, confirmar, lembrar,
remarcar, chamar de volta e reativar** clientes, e gera as mensagens prontas (no
seu tom) para você revisar e enviar pelo WhatsApp.

O objetivo é simples: **agenda cheia e o mínimo de faltas**. Lembrete 2 dias antes
+ pedido de confirmação 1 dia antes derrubam o no-show de forma comprovada.

## O que ela faz

- **Agendar** — você cola o pedido do cliente, ela mostra os horários livres e salva.
- **Confirmar / Lembrar** — lista a agenda do dia seguinte e escreve as mensagens.
- **Remarcar / Cancelar** — em segundos, já oferecendo novos horários.
- **Retorno** — avisa quem está na hora de voltar (corte de 21 em 21 dias, etc.).
- **Reativar** — encontra quem sumiu e escreve o convite de volta.
- **Lista de espera / encaixe** — preenche buracos de cancelamento.
- **Resumo** — contagem por status e sua taxa de no-show.

Tudo fica **na sua máquina**, num arquivo local (`.pauta/agenda.csv`). Nada é
enviado para fora; o Pauta **sugere** as mensagens, quem envia é você.

## Como instalar

1. Copie a pasta `pauta` para a pasta de skills do seu Claude Code:
   - Projeto específico: `.claude/skills/pauta/`
   - Para todos os projetos: `~/.claude/skills/pauta/`
2. Abra o Claude Code na pasta do seu negócio e diga, por exemplo:
   *"vamos configurar minha agenda"* ou *"organiza meus agendamentos"*.
3. Na **primeira vez**, o Pauta faz algumas perguntas (serviços, horários, tom) e
   grava sua configuração local. Depois disso ele fica pronto para o dia a dia.

## Como usar (exemplos do que dizer)

- "Cliente quer cortar o cabelo quinta de tarde, que horários eu tenho?"
- "Confirma a agenda de amanhã pra mim."
- "Quem está na hora de voltar?"
- "Quem sumiu nos últimos 2 meses?"
- "Remarca o agendamento da Ana pra sexta 15h."

## Requisitos

- Claude Code
- Python 3 (já vem no macOS e na maioria dos Linux — nenhuma instalação extra).

## Licença

MIT. Veja `LICENSE`.
