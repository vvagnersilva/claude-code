# Alambique — o destilador de conteúdo

Aprenda **de verdade** do que você assiste e lê. Você entrega conteúdo longo — a transcrição ou o link de um vídeo do YouTube, um podcast, uma aula gravada, uma live, um artigo ou um PDF — e o Alambique destila a essência:

- **Em uma frase** — o resumão do conteúdo.
- **Resumo em pontos** — só o que importa.
- **Conceitos-chave** — explicados de forma simples, sem jargão.
- **Como aplicar no seu caso** — personalizado pela sua profissão.
- **Ações práticas** — o que fazer com isso.
- **Cartões de revisão** — que voltam **na hora certa** pra você não esquecer.

E guarda um histórico de tudo que você estudou. **Nunca inventa**: só usa o que está no conteúdo.

## Para quem é
Para qualquer pessoa que consome muito conteúdo (vídeos, aulas, podcasts, artigos) e sente que esquece quase tudo. Você não precisa saber programar — é só conversar em português.

## Como instalar
1. Descompacte o arquivo. Você verá uma pasta chamada `Alambique`.
2. Copie a pasta `Alambique` para dentro da pasta de skills do seu Claude Code:
   - No seu projeto: `.claude/skills/Alambique/`
   - Ou para todos os projetos: `~/.claude/skills/Alambique/`
3. Abra o Claude Code nesse projeto. Na primeira vez, o Alambique faz 4 perguntas rápidas (seu nome, sua profissão, o que você estuda e o tom que prefere) e já fica pronto.

## Como usar (é só falar)
Você conversa naturalmente. Por exemplo:
- *"Resume esse vídeo pra mim"* (e cola a transcrição, ou manda o link).
- *"Cria cartões pra eu fixar isso."*
- *"Me revisa o que estudei essa semana."*
- *"Como eu aplico isso no meu trabalho?"*
- *"O que aquele podcast falava sobre preços?"*

O Alambique cuida de te trazer o cartão certo no dia certo — você não precisa lembrar de revisar.

## Ler vídeos do YouTube pelo link (opcional)
Se você quiser que o Alambique leia um vídeo do YouTube só pelo link, instale uma vez o `yt-dlp`:
```
pip install yt-dlp
```
Não é obrigatório: sem ele, é só colar a transcrição ou o texto que o Alambique destila do mesmo jeito (funciona para podcasts, aulas, artigos e PDFs também).

## Privacidade
Tudo que você estuda fica **no seu computador**, na pasta `.alambique/`. Nada é enviado para fora. Se você usa git, essa pasta já está protegida contra subir para repositório.

## Requisitos
- Claude Code.
- Python 3 (já vem no Mac e na maioria dos Linux). O motor usa só a biblioteca padrão — nada para instalar.
- `yt-dlp` é opcional, só para ler vídeos do YouTube pelo link.

---
Feito para a comunidade Maestros da IA. Licença MIT.
