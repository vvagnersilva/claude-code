# Leme 🧭

**O seu assistente pessoal de tarefas, dentro do Claude Code.**

Você joga tudo que está na sua cabeça — e o Leme responde em português simples:

- **As 3 tarefas que importam hoje** (e o porquê de cada uma)
- **A fila inteira priorizada**, da mais importante para a menos
- **Nada cai no esquecimento** — tarefas paradas voltam à tona sozinhas
- **O que está te travando** (esperando alguém) fica separado, não atrapalha
- **Revisão da semana** — o que saiu, o que atrasou, o que decidir
- **"Tô atolado, por onde começo?"** — foco, não uma lista infinita

Tudo roda na sua máquina. Suas tarefas não saem do seu computador.

## Para quem é

Donos de negócio e profissionais de "dia corrido" — clínicas, barbearias,
agências, escritórios, consultorias, corretores, contadores, autônomos — que
vivem apagando incêndio e perdem coisas no meio do caminho. Não precisa saber
programar nem decorar comando nenhum: é só conversar.

## Instalação

1. Baixe e descompacte o arquivo `Leme.zip`.
2. Copie a pasta `Leme` para dentro da pasta `.claude/skills/` do seu projeto
   (crie se não existir):

   ```
   seu-projeto/
   └── .claude/
       └── skills/
           └── Leme/
   ```

   Dica: para usar em qualquer projeto, copie para `~/.claude/skills/Leme`.
3. Abra o Claude Code nessa pasta e diga: **"Leme, me organiza o dia"**.

## Primeira conversa

Na primeira vez, o Leme faz um papo rápido: como você prefere ser chamado, o
que você faz e como você organiza tarefas hoje. Ele cria a pasta local `.leme/`
(onde ficam suas tarefas e configurações) e está pronto. Esse setup acontece
uma vez só.

## Frases do dia a dia

| Você diz | O Leme faz |
|----------|------------|
| "Anota: ligar pro contador amanhã" | Captura a tarefa e já calcula a prioridade |
| "Joga tudo: proposta do João, pagar o aluguel, comprar material" | Captura uma por uma |
| "O que eu faço hoje?" | Mostra as 3 de hoje, com o motivo de cada |
| "Me mostra a fila toda" | Lista priorizada, da maior nota para a menor |
| "O que tem de Comercial?" | Filtra por projeto/área |
| "Terminei a #3" | Marca como feita |
| "Empurra a proposta pra sexta" | Muda o prazo |
| "A #4 virou urgente" | Atualiza e reordena |
| "Revisão da semana" | Os 4 quadros: feitas, atrasadas, paradas, sem data |

## Garantias

- **Nunca inventa** — tarefa, prazo e prioridade saem só do que você registrou.
- **Sempre explica a ordem** — toda priorização vem com o porquê.
- **Foco antes de lista** — sempre te aponta as 3 que importam hoje.
- **Dados 100% locais** — nada é enviado para a internet.
- **Sem dependências** — usa só o Python que já vem no sistema. Sem conta,
  sem chave de API, sem mensalidade.
- **Você decide e executa** — o Leme organiza e recomenda; a ação é sua.

## Requisitos

- Claude Code instalado
- Python 3 (já vem no macOS e na maioria dos Linux; no Windows, instale de python.org)

## Licença

MIT — veja o arquivo `LICENSE`.
