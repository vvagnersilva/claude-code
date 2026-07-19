# SETUP — primeira conversa do Carteiro (rode UMA vez)

Este arquivo guia a IA na configuracao inicial. **So execute se
`.carteiro/config.md` ainda NAO existir.** Se ja existe, ignore este arquivo e va
direto trabalhar.

## Objetivo
Fazer 4-5 perguntas curtas, gravar `.carteiro/config.md` na RAIZ do projeto e
depois **apagar os arquivos de setup** pra skill ficar limpa.

## Passo 1 — Conversa de boas-vindas
Diga, no maximo em 3 linhas: "Sou o Carteiro — deixo sua caixa de entrada sob
controle: eu tri­o suas mensagens, rascunho as respostas no seu tom e nao deixo
ninguem sem retorno. Antes de comecar, me conta 5 coisinhas rapidas." Entao
pergunte (pode ser tudo de uma vez, aceite respostas curtas):

1. **Seu nome** (como voce assina as respostas).
2. **Seu negocio / area** (pra eu entender o contexto das mensagens).
3. **Tom das suas respostas** — ex.: cordial e direto, informal e proximo,
   formal e tecnico.
4. **Canais** que voce usa — ex.: e-mail, WhatsApp, Instagram.
5. **Remetentes importantes (VIPs)** — nomes/e-mails que devem SEMPRE entrar na
   frente (clientes-chave, chefe, contador, socio). Pode deixar em branco.

Se a pessoa nao souber ou nao quiser responder algo, use um padrao razoavel e siga
— nunca trave o setup.

## Passo 2 — Gravar o config
Crie o arquivo `.carteiro/config.md` na RAIZ do projeto (o motor procura la) com
EXATAMENTE este formato de linha (`- **Rotulo:** valor`), preenchendo com as
respostas:

```markdown
# Config do Carteiro
- **Nome:** <nome>
- **Negocio:** <negocio/area>
- **Tom:** <tom das respostas>
- **Canais:** <canais separados por virgula>
- **Remetentes VIP:** <nomes/e-mails separados por virgula, ou "nenhum">
```

Descubra a raiz rodando qualquer comando do motor (ele imprime/usa `.carteiro/` na
raiz). Uma forma simples: crie a pasta `.carteiro/` no diretorio atual do projeto
e grave o `config.md` la.

Confirme que deu certo:
```bash
python3 "<pasta-desta-skill>/scripts/carteiro.py" config
```
Deve imprimir os campos que voce gravou.

## Passo 3 — Garantir privacidade (.gitignore)
Se o projeto tiver controle de versao (uma pasta `.git`), garanta que a pasta de
dados nao seja versionada: acrescente uma linha `.carteiro/` ao arquivo
`.gitignore` da RAIZ do projeto (crie o arquivo se nao existir). Isso mantem as
mensagens e a fila 100% privadas.

## Passo 4 — Autodestruir o setup
Com o `config.md` gravado e conferido, **apague os arquivos de setup** pra deixar a
skill limpa (a pessoa nunca mais vai precisar deles):

```bash
rm -f "<pasta-desta-skill>/SETUP.md"
```

Depois diga: "Prontinho, <nome>! Pode colar aqui suas mensagens que eu tri­o e ja
te digo o que responder hoje. 📬"

## Passo 5 — Comecar
Va direto pro modo **Triar** (peca a pessoa colar as mensagens) ou pergunte o que
ela quer fazer primeiro.
