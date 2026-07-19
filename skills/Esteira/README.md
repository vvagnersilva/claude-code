# Esteira — o funil que não deixa negócio escapar

A **Esteira** é uma skill de Claude Code que vira o seu **funil de vendas**: ela
acompanha cada negócio em aberto por etapa, te diz **em quem falar hoje**, avisa
**o que está esfriando**, **prevê quanto deve fechar no mês** e escreve o próximo
follow-up pra você enviar. Tudo em português, conversando — você não digita
comando nenhum.

Feita para quem tem **vários negócios em andamento ao mesmo tempo** e perde
dinheiro quando uma proposta esfria ou um follow-up não sai: vendedores,
representantes comerciais, corretores, consultores, agências e donos de serviço.

## O que ela faz

- **Registrar** cada negócio (cliente, valor, etapa, origem).
- **Hoje / Foco** — mostra em quem falar hoje, ranqueado, com o porquê.
- **Esfriando** — avisa os negócios parados antes de você perder.
- **Previsão** — quanto deve entrar (valor × probabilidade de cada etapa).
- **Funil** — quantos e quanto em cada etapa, taxa de conversão, ticket médio,
  motivos de perda.
- **Próximo toque** — escreve a mensagem de follow-up no seu tom (WhatsApp-first).
- **Ganhar / Perder** — fecha o negócio; ao perder, guarda o motivo pra aprender.

## Instalar

1. Baixe e descompacte a pasta **`Esteira`**.
2. Coloque-a dentro de `.claude/skills/` do seu projeto (ou em
   `~/.claude/skills/` para usar em qualquer lugar). O caminho final fica assim:
   `.claude/skills/Esteira/SKILL.md`.
3. Abra o Claude Code nessa pasta e fale naturalmente, por exemplo:
   *"me ajuda a acompanhar minhas vendas"* ou *"registra um cliente novo"*.

Na **primeira vez**, a Esteira faz algumas perguntas rápidas (como você prefere
ser chamado, o que vende, ticket médio, canal e tom de voz) e guarda tudo numa
pasta local `.esteira/`. Depois disso, é só conversar.

## Privacidade

Tudo fica na **sua máquina**, na pasta `.esteira/` (que entra no `.gitignore`
automaticamente). Nenhum dado de cliente sai do seu computador. A Esteira não
usa internet, não precisa de conta nem de chave de API — só do Python 3 que já
vem no seu sistema.

## Como funciona por dentro (pra quem tem curiosidade)

A Esteira é guiada por um arquivo `SKILL.md` (as instruções que o Claude segue) e
um pequeno motor em Python (`scripts/esteira.py`) que faz as contas — id, datas,
probabilidades, previsão e priorização — gravando tudo num arquivo `.csv` local.
Você nunca mexe nisso: conversa com o Claude, e ele cuida do resto.

## Licença

MIT — use, adapte e compartilhe à vontade.
