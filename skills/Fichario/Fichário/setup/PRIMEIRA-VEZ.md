# Setup de primeira vez — Fichário

Rode isto **uma única vez**, quando ainda não existe `.fichario/config.md`. Ao terminar, **apague a pasta `setup/`** para a skill ficar limpa.

## Passo 1 — Conversar (4 perguntas curtas, em PT-BR)
Pergunte ao dono, de forma leve e uma de cada vez (ou em bloco se ele preferir):

1. **Como você quer ser chamado?** (nome ou apelido)
2. **Qual sua profissão / área de atuação?** (ex.: dentista, gestor de tráfego, contador, estudante de IA)
3. **Quais são os principais assuntos que você estuda ou quer guardar?** (3 a 6 temas — viram suas tags favoritas; ex.: ia, vendas, conteudo, gestao)
4. **Que tom você prefere nas respostas?** (ex.: direto e objetivo / explicado e didático / informal)

> Em sessão automática/headless, NÃO use perguntas interativas: use as respostas que vierem no texto do pedido. Se nada vier, use padrões sensatos (nome "você", área "geral", assuntos "ia, negocio, conteudo", tom "direto e didático") e siga.

## Passo 2 — Gravar o config
Crie o arquivo `.fichario/config.md` **na raiz do projeto do dono** (a mesma raiz onde ficará a pasta `.fichario/`), com o conteúdo preenchido:

```markdown
# Configuração do Fichário

- Nome: <nome>
- Área: <profissão/área>
- Assuntos principais: <tema1, tema2, tema3, ...>
- Tom: <tom preferido>
- Criado em: <AAAA-MM-DD>
```

Use acentuação correta de português. Garanta que a pasta `.fichario/` exista (o motor cria ao gravar o primeiro cartão, mas você pode criar agora).

## Passo 3 — Sugerir o `.gitignore`
Se o projeto usa git, lembre o dono de que `.fichario/` é privado e já vem no `.gitignore` da skill. Não suba o conhecimento pessoal para repositório público.

## Passo 4 — Autodestruir o setup
Apague a pasta `setup/` inteira (este arquivo incluso). A partir daqui, a skill funciona pelos 6 modos do `SKILL.md`.

## Passo 5 — Primeira ideia
Convide o dono a guardar a primeira ideia: *"Pronto! Me conta uma coisa que você aprendeu hoje que vale guardar — eu transformo no seu primeiro cartão."*
