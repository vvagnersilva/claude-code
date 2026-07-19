# Setup da Claquete — primeira execução

Bem-vindo à **Claquete**: uma equipe de subagentes do Claude Code que toca o seu canal do YouTube de ponta a ponta — pauta, roteiro, thumbnail e título, SEO, pacote de publicação e análise de desempenho.

Este setup roda **uma única vez**. Ele só pergunta sobre o seu canal, grava num arquivo local e ignorado pelo git (`.claquete/config.md`), e depois se autodestrói — deixando só a equipe instalada e limpa.

## Como rodar o setup

Abra o Claude Code na raiz do seu projeto/pasta (onde está a pasta `.claude/`) e diga:

> **"Rode o setup da Claquete."**

O Claude vai conduzir o roteiro em `setup/perguntas.md`, uma pergunta de cada vez, e ao final:
1. Grava suas respostas em `.claquete/config.md` (espelho de `exemplos/config.exemplo.md`).
2. Roda `bash setup/concluir-setup.sh`, que remove este `SETUP.md` e a pasta `setup/`.

Pronto. A partir daí, é só pedir as coisas naturalmente e a equipe certa entra em ação:
- *"Pauteiro, me dá 5 ideias de vídeo pra essa semana"* → **Pauteiro**
- *"Roteirista, escreve o roteiro do vídeo sobre X"* → **Roteirista**
- *"Diretor de arte, cria a thumbnail e os títulos desse vídeo"* → **Diretor de Arte**
- *"Otimizador, monta o SEO (descrição, tags, capítulos)"* → **Otimizador**
- *"Produtor, junta tudo no pacote de publicação"* → **Produtor**
- *"Analista, esse vídeo fez 2.000 views e 4% de CTR — o que eu faço melhor?"* → **Analista**

## Não quer configurar agora?
Tudo bem. A equipe funciona **sem** o `.claquete/config.md` — nesse caso cada agente pergunta o essencial do canal antes de trabalhar. O setup só deixa tudo mais afiado e no seu tom. Se preferir pular, é só apagar `SETUP.md` e a pasta `setup/` à mão.

## Privacidade
Nenhum segredo é necessário para usar a Claquete. O `.claquete/config.md` guarda só informações do seu canal (nicho, público, tom, formato) e fica fora do git. **Nunca** cole chaves de API ou senhas aqui — a Claquete trabalha em texto e quem grava, edita e publica os vídeos é você.
