# Setup do Estaleiro — primeira execução

Bem-vindo ao **Estaleiro**: uma tripulação de subagentes do Claude Code que planejam, constroem, testam, revisam e blindam o seu código.

Este setup roda **uma única vez**. Ele só pergunta as convenções do seu projeto, grava num arquivo local e ignorado pelo git (`.estaleiro/config.md`), e depois se autodestrói — deixando só a tripulação instalada e limpa.

## Como rodar o setup

Abra o Claude Code na raiz do seu projeto (onde está a pasta `.claude/`) e diga:

> **"Rode o setup do Estaleiro."**

O Claude vai conduzir o roteiro em `setup/perguntas.md`, uma pergunta de cada vez, e ao final:
1. Grava suas respostas em `.estaleiro/config.md` (espelho de `exemplos/config.exemplo.md`).
2. Roda `bash setup/concluir-setup.sh`, que remove este `SETUP.md` e a pasta `setup/`.

Pronto. A partir daí, é só pedir as coisas naturalmente e a tripulação certa entra em ação:
- *"Planeje como adicionar login com Google"* → **Arquiteto**
- *"Implemente o passo 2 do plano"* → **Construtor**
- *"Escreva os testes disso"* → **Testes**
- *"Revise o diff antes de eu commitar"* → **Revisor**
- *"Faz uma revisão de segurança"* → **Sentinela**

## Não quer configurar agora?
Tudo bem. A tripulação funciona **sem** o `.estaleiro/config.md` — nesse caso cada agente descobre a stack lendo seus manifests e arquivos vizinhos. O setup só deixa tudo mais afiado. Se preferir pular, é só apagar `SETUP.md` e a pasta `setup/` à mão.

## Privacidade
Nenhum segredo é necessário para usar o Estaleiro. O `.estaleiro/config.md` guarda só convenções do seu projeto (linguagem, comandos, estilo) e fica fora do git. **Nunca** cole chaves de API ou senhas aqui.
