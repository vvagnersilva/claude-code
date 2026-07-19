# Setup do Rastro — primeira execução (1 minuto)

> Para a IA: execute este setup **apenas na primeira vez** (quando ainda não existe
> `.rastro/config.md` na raiz do projeto). Conduza em PT-BR, uma pergunta de cada vez, de
> forma leve. Ao final, grave o `config.md` na raiz do projeto e **apague a pasta `setup/`**
> desta skill. Se o `.rastro/config.md` já existir, NÃO rode o setup — vá direto ao trabalho.

## Por que este setup existe
O método do Rastro gira em torno de uma coisa: **um teste que o Claude pode rodar sozinho**
para confirmar que o bug morreu. Se a IA já souber, de cara, como rodar os testes, o build e
o app deste projeto, toda depuração fica mais rápida e mais barata. É só isso que coletamos
aqui — nenhum segredo, nenhuma senha, nenhuma chave. Só como o seu projeto roda.

## Perguntas (uma de cada vez)
1. **Como você quer ser chamado?** (nome ou apelido)
2. **Qual a linguagem/stack principal do projeto?** (ex.: Node/React, Python, PHP/Laravel,
   Java/Spring, Flutter, "não sei dizer") — pode listar mais de uma.
3. **Qual o comando para rodar os testes?** (ex.: `npm test`, `pytest`, `php artisan test`).
   Não tem teste ainda? Responda "não tenho" — o Rastro vai trabalhar com verificação manual.
4. **Qual o comando de build / checagem de tipos?** (ex.: `npm run build`, `npm run type-check`,
   `tsc --noEmit`, `mvn compile`). Não tem? "não tenho".
5. **Como você roda o app localmente?** (ex.: `npm run dev`, `python app.py`, `docker compose up`)
6. **Onde ficam os logs / como você vê o erro?** (ex.: terminal, `logs/app.log`, console do
   navegador, "não sei") — ajuda a IA a saber onde procurar evidência.
7. **Tom da conversa:** direto e técnico, ou didático e sem jargão? (o Rastro se adapta)

Se o dono não souber responder algo (ex.: não conhece o comando de teste), tudo bem: registre
"a confirmar" e siga. O Rastro pergunta de novo quando precisar.

## Gravar o config (na RAIZ do projeto, não dentro da skill)
Crie o arquivo `.rastro/config.md` na raiz do projeto com este conteúdo, preenchido:

```markdown
# Config do Rastro

- **Nome:** [nome do dono]
- **Stack principal:** [linguagens/frameworks]
- **Comando de testes:** [comando ou "não tenho"]
- **Comando de build/tipos:** [comando ou "não tenho"]
- **Comando para rodar o app:** [comando]
- **Onde ver logs/erros:** [terminal / arquivo / navegador]
- **Tom:** [direto | didático]
```

Passos exatos (rode a partir da raiz do projeto):
1. Garanta a pasta: crie o diretório `.rastro/` na raiz do projeto se não existir.
2. Escreva o `.rastro/config.md` com os valores coletados.
3. Garanta que o `.rastro/` seja ignorado pelo git: se existir um `.gitignore` na raiz e ele
   ainda não tiver a linha `.rastro/`, adicione `.rastro/` a ele. Se não existir `.gitignore`,
   crie um na raiz com a linha `.rastro/`. (Seu histórico de bugs é seu — não vai para o repositório.)
4. Confirme ao dono, em uma frase, que está pronto e que ele já pode pedir para depurar um bug.

## Autodestruição do setup (obrigatória)
Depois de gravar o config com sucesso, **remova a pasta `setup/` desta skill** para deixar a
instalação limpa:
```
rm -rf setup
```
(Só apague a `setup/`, nunca o `.rastro/` da raiz — lá ficam o config e o diário de bugs.)

Pronto. A partir daqui, é só dizer o bug (ou colar o erro) e pedir para o Rastro depurar.
