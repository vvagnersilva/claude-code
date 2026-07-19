# Engrenagem

**Um consultor de automacao dentro do seu Claude Code.** Ela descobre quais
tarefas repetitivas do seu negocio valem a pena automatizar, mostra **por onde
comecar**, calcula **quanto tempo e dinheiro voce economiza** e te ajuda a montar
a **primeira automacao** hoje. Feita para dono de negocio de servico — sem jargao,
em portugues.

> Para quem sempre pensa "eu sei que dava pra automatizar um monte de coisa, mas
> nao sei por onde comecar".

## O que ela faz (6 modos)
1. **Mapear** — conversa rapida pra descobrir onde o seu tempo vai.
2. **Priorizar** — ordena tudo num roteiro: Ganho Rapido, Projeto, Talvez, Evite.
3. **Planejar** — para cada tarefa, o jeito mais simples de automatizar.
4. **Comecar** — entrega a primeira automacao pronta pra usar (modelo, checklist ou planilha).
5. **ROI** — quanto voce ganha, em horas e em reais por mes/ano.
6. **Revisar** — acompanha o progresso e aponta o proximo ganho.

## Como instalar
1. Baixe e descompacte o arquivo `Engrenagem.zip`.
2. Copie a pasta `Engrenagem` para dentro de `.claude/skills/` no seu projeto
   (ou em `~/.claude/skills/Engrenagem` para usar em qualquer projeto).
   O caminho final fica assim:
   ```
   .claude/skills/Engrenagem/
   ├── SKILL.md
   ├── scripts/engrenagem.py
   ├── references/banco-de-automacoes.md
   └── setup/PRIMEIRA-VEZ.md
   ```
3. Abra o Claude Code nesse projeto.

## Como usar
E so conversar em portugues. Por exemplo:

- "quero automatizar meu negocio mas nao sei por onde comecar"
- "me ajuda a mapear meus processos"
- "o que eu automatizo primeiro?"
- "quanto tempo eu economizo se automatizar isso?"

Na **primeira vez**, a Engrenagem faz uma configuracao rapida (uns 2 minutos):
pergunta seu tipo de negocio, quanto vale 1 hora do seu tempo, quais ferramentas
voce ja usa e o tom das suas mensagens. Isso fica guardado so na sua maquina, na
pasta `.engrenagem/` do projeto (que nao vai pro Git).

## Precisa de que?
- Claude Code instalado.
- Python 3 (ja vem no Mac e na maioria dos Linux). O motor usa **so** a biblioteca
  padrao — nao instala nada.
- Nenhuma chave de API, nenhuma conta paga. Tudo roda local.

## Seus dados
Tudo fica em `.engrenagem/` na raiz do seu projeto:
- `config.md` — sua configuracao
- `processos.csv` — o mapa das suas tarefas
- `roteiro.md` — o roteiro priorizado

Nada e enviado pra lugar nenhum. A pasta ja vem no `.gitignore`.

## Licenca
MIT — use, adapte e compartilhe a vontade.
