# Setup da Fisga (1 minuto, só na primeira vez)

A Fisga funciona melhor quando ela já sabe **quem você é e o que você vende** — assim ela
personaliza pesquisa e mensagens sem te perguntar de novo toda vez.

## Como rodar

Abra o Claude Code na pasta do seu projeto e diga:

> **"Rode o setup da Fisga."**

O Claude vai te fazer ~9 perguntas rápidas (seu nome, sua oferta, seu diferencial, seu nicho-alvo,
porte, região, ticket, canais preferidos e tom de voz). Ao terminar, ele:

1. Grava suas respostas em **`.fisga/config.md`** na raiz do projeto (esse arquivo é ignorado pelo
   git — não vai pra lugar nenhum, fica só com você).
2. **Remove sozinho** os arquivos de instalação (este `SETUP.md` e a pasta `setup/`).

Depois disso é só usar: *"Pesquisa essa empresa pra mim"*, *"escreve a abordagem pra esse cliente"*,
*"esse lead vale a pena?"*.

## Sem setup também funciona
Se você pular o setup, a Fisga só vai te perguntar nome, oferta e canal na hora — funciona igual,
só pergunta mais. O setup é conveniência, não obrigação.

## Privacidade
Tudo que a Fisga sabe sobre você fica em `.fisga/config.md`, na sua máquina. Nenhuma credencial,
nenhum dado de cliente sai do seu computador.
