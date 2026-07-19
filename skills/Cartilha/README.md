# Cartilha — tire o processo da sua cabeça e passe pra frente

A **Cartilha** é uma skill para Claude Code que pega aquilo que hoje **só você
sabe fazer** — que está na sua cabeça — e transforma num **passo a passo (POP)**
que qualquer pessoa da sua equipe consegue seguir. Depois ela te ajuda a
**treinar** quem vai assumir e a **delegar** sem a qualidade cair. Tudo
conversando, em português, sem código.

Com o tempo você acumula uma **cartilha** própria do seu negócio: os processos
que antes viviam só com você viram um manual que a equipe executa — e você ganha
liberdade pra crescer sem ser o gargalo.

## Para quem é

Donos de negócio e gestores que sentem que **"tudo depende de mim"**, que vão
**contratar ou treinar** alguém, ou que precisam **padronizar e delegar** um
processo sem ver a qualidade despencar. Clínicas, barbearias, contabilidade,
agências, lojas, construtoras, indústrias, consultorias. Não precisa saber
programar.

## O que ela faz

- **Mapear** — você conta como faz um processo; a Cartilha captura numa conversa
  curta e esperta.
- **Padronizar** — vira um POP limpo: objetivo, passo a passo, decisões, checklist
  de qualidade e os erros a evitar — seguível por uma pessoa nova, sem você do lado.
- **Treinar** — monta a trilha pra um novo contratado assumir o processo (observar
  → fazer junto → sozinho com conferência → sozinho), com marcos e verificação.
- **Delegar** — gera o briefing pra passar uma tarefa: contexto, objetivo,
  entregável, prazo, padrão e — o que mais destrava — até onde a pessoa decide
  sozinha.
- **Manual / Painel** — veja todos os processos, os críticos e os que ainda faltam
  fechar.
- **Revisar** — quando algo dá errado na prática, a melhoria entra no POP e a
  versão sobe; o procedimento fica cada vez mais à prova de erro.

## Como instalar

1. Baixe e descompacte o arquivo `Cartilha.zip`.
2. Copie a pasta `Cartilha` para dentro de `.claude/skills/` do seu projeto (ou
   para `~/.claude/skills/Cartilha` para usar em qualquer lugar). O caminho final
   fica assim:

   ```
   .claude/skills/Cartilha/
   ├── SKILL.md
   ├── scripts/cartilha.py
   ├── references/
   └── setup/
   ```

3. Abra o Claude Code nessa pasta. Na primeira vez, é só dizer algo como
   **"está tudo na minha cabeça, quero começar a documentar meus processos"** — a
   Cartilha faz uma conversa rápida de configuração e já documenta o primeiro
   procedimento com você.

## Como usar (você só conversa)

Você nunca digita comando nem código — só fala em português. Exemplos:

- "Está tudo na minha cabeça, documenta como eu faço o fechamento do caixa." → **Mapear/Padronizar**
- "Vou contratar uma recepcionista, monta o treino do atendimento." → **Treinar**
- "Preciso passar a parte de orçamentos pro meu assistente." → **Delegar**
- "Quais processos eu já tenho documentados?" → **Manual / Painel**
- "Quando o fulano seguiu, ele esqueceu de conferir o Pix — já corrige isso." → **Revisar**

Por baixo, a Cartilha usa um pequeno programa em Python (já incluso, só biblioteca
padrão) para guardar e organizar os procedimentos. Você só conversa.

## Privacidade

Tudo fica na **sua** máquina, na pasta `.cartilha/` do seu projeto. Nada é
enviado para fora, nenhuma conta, nenhuma chave de API, nenhuma internet
necessária. Os processos de um negócio são informação sensível — por isso ficam
só com você. A Cartilha **escreve** os procedimentos e os textos de treino/
delegação; quem treina e cobra a equipe é sempre você.

## Requisitos

- Claude Code instalado.
- Python 3 (já vem no macOS e na maioria dos sistemas). Nada mais para instalar.

## Licença

MIT — veja o arquivo `LICENSE`.
