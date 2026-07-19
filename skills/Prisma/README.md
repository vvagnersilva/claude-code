# Prisma 🔺 — seu engenheiro de prompts de bolso

Um prisma separa luz branca bagunçada num espectro nítido. É o que esta skill faz
com pedidos para IA: pega um *"faz um texto aí pra mim"* e devolve uma instrução
clara, completa e reutilizável — que faz **qualquer ferramenta de IA** (ChatGPT,
Claude, Gemini, geradores de imagem) entregar muito melhor.

O Prisma **não faz a tarefa por você** — ele entrega o **prompt pronto** para
você colar onde quiser. É o ourives da instrução.

## O que ele faz (6 modos)

1. **Criar** — você diz o que quer (mesmo vago), ele faz 2-4 perguntas rápidas e
   devolve um prompt pronto e estruturado.
2. **Consertar** — você cola um prompt que não funcionou + o resultado ruim, ele
   diagnostica o que faltou e devolve a versão corrigida.
3. **Afinar** — "deixa mais curto", "mais formal", "muda o formato" — ajustes
   finos no último prompt.
4. **Molde** — transforma um prompt que deu certo num modelo reutilizável com
   campos `{para preencher}`.
5. **Biblioteca** — guarda, busca e reusa seus prompts, organizados por categoria.
6. **Ensinar** — micro-aula de 1 minuto de como pedir bem para a IA, com exemplo
   da sua área.

## As 6 faces de um bom prompt

Papel · Objetivo · Contexto · Formato · Exemplo · Limites. O Prisma cuida disso
por baixo — você só conversa em português.

## Como instalar

1. Descompacte o arquivo `Prisma.zip`.
2. Copie a pasta `Prisma` para dentro de `.claude/skills/` no seu projeto
   (ou em `~/.claude/skills/` para usar em qualquer projeto).
3. Abra o Claude Code nessa pasta e fale: **"Prisma, me ajuda a montar um
   prompt"**. Na primeira vez ele faz um setup rápido e pronto.

Caminho final esperado:
```
.claude/skills/Prisma/SKILL.md
```

## Privacidade

Tudo fica no seu computador. Suas configurações e sua biblioteca de prompts
ficam na pasta `.prisma/` (ignorada pelo Git). Nada é enviado para fora.

## Requisitos

- Claude Code instalado.
- Python 3 (já vem no macOS e na maioria dos Linux) — usado só para organizar a
  biblioteca local. Nenhuma biblioteca extra, nenhuma chave de API.

## Licença

MIT — use, adapte e compartilhe à vontade.
