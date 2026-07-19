# Setup de primeira vez — Alambique

Rode isto **uma única vez**, quando ainda não existe `.alambique/config.md`. Ao terminar, **apague a pasta `setup/`** para a skill ficar limpa.

## Passo 1 — Conversar (4 perguntas curtas, em PT-BR)
Pergunte ao dono, de forma leve (uma de cada vez ou em bloco):

1. **Como você quer ser chamado?** (nome ou apelido)
2. **Qual sua profissão / área de atuação?** (ex.: dentista, gestor de tráfego, contador, corretor, estudante de IA) — é o que personaliza o "como aplicar".
3. **O que você mais costuma estudar / consumir?** (ex.: vídeos de IA, aulas de marketing, podcasts de gestão, artigos técnicos — vira suas tags favoritas)
4. **Que tom você prefere?** (ex.: direto e objetivo / explicado e didático / informal)

> Em sessão automática/headless, NÃO use perguntas interativas: use as respostas que vierem no texto do pedido. Se nada vier, use padrões sensatos (nome "você", profissão "geral", estuda "ia, negocio, produtividade", tom "direto e didático") e siga.

## Passo 2 — Gravar o config
Crie o arquivo `.alambique/config.md` **na raiz do projeto do dono** (a mesma raiz onde ficará a pasta `.alambique/`), com o conteúdo preenchido e **acentuação correta de português**:

```markdown
# Configuração do Alambique

- Nome: <nome>
- Profissão: <profissão/área>
- Costuma estudar: <tema1, tema2, tema3>
- Tom: <tom preferido>
- Criado em: <AAAA-MM-DD>
```

A pasta `.alambique/` é criada pelo motor ao guardar o primeiro estudo, mas você pode criá-la agora.

## Passo 3 — Lembrar da privacidade
Se o projeto usa git, `.alambique/` é privado e já vem no `.gitignore` da skill. Os estudos do dono não sobem para repositório.

## Passo 4 — (Opcional) legendas do YouTube
Se o dono quiser que o Alambique leia vídeos do YouTube automaticamente pelo link, ele precisa ter o `yt-dlp` instalado (`pip install yt-dlp`). Não é obrigatório: sem ele, é só colar a transcrição/texto que o Alambique destila igual. Mencione isso só se fizer sentido.

## Passo 5 — Autodestruir o setup
Apague a pasta `setup/` inteira (este arquivo incluso). A partir daqui, a skill funciona pelos 6 modos do `SKILL.md`.

## Passo 6 — Primeiro estudo
Convide o dono: *"Pronto! Me manda um vídeo, um podcast, uma aula ou cola um texto que você quer estudar — eu destilo e a gente monta seus primeiros cartões de revisão."*
