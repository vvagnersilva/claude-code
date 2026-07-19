# Holofote — estúdio de conteúdo no Claude Code

O Holofote é uma **skill do Claude Code** que vira o seu estúdio de conteúdo: define a
estratégia, monta o calendário editorial e cria peças prontas e nativas de cada
plataforma (Reels, carrossel, post, Stories, LinkedIn, e-mail) — tudo **no seu tom de
voz** e sem inventar nada. Você conversa em português normal; o Holofote sugere o
conteúdo, você revisa e publica.

## O que ele faz

- **Estratégia** — nicho, público, tom de voz e os pilares de conteúdo.
- **Calendário** — calendário editorial de 7, 15 ou 30 dias, com as datas reais e os
  pilares/formatos rodando para não ficar tudo igual.
- **Criar** — uma peça pronta no formato que você pedir, com gancho forte e CTA.
- **Reaproveitar** — uma ideia boa vira vários formatos de uma vez.
- **Humanizar** — cola um texto e ele tira a "cara de IA", deixando no seu jeito.
- **Banco / Resumo** — guarda ideias e mostra o raio-x da sua presença.

## Instalação

1. Baixe e descompacte o arquivo.
2. Copie a pasta `Holofote` para dentro de `.claude/skills/` no seu projeto
   (ou em `~/.claude/skills/Holofote` para usar em qualquer projeto):
   ```
   .claude/skills/Holofote/
   ```
3. Abra o Claude Code nesse projeto. A skill é reconhecida sozinha.

## Como usar

1. **Primeira conversa (configuração).** Diga algo como:
   *"Quero configurar meu conteúdo"* ou *"vamos montar minha estratégia de posts"*.
   O Holofote pergunta seu nicho, público, tom de voz, pilares, plataformas e
   frequência, grava tudo em `.holofote/` e some com os arquivos de configuração
   (a skill fica limpa). É uma vez só.

2. **No dia a dia**, fale naturalmente:
   - *"Monta meu calendário de 30 dias, 3 posts por semana."*
   - *"Cria um roteiro de Reels sobre [tema]."*
   - *"Faz um carrossel sobre [tema]."*
   - *"Pega esse Reels e transforma em carrossel, post e Stories."*
   - *"Humaniza esse texto pra ficar com a minha cara."* (cole o texto)
   - *"Como está minha presença? Me dá um resumo."*

## O que esperar

- O Holofote **escreve no seu tom** — quanto melhor você descrever sua voz (ou der um
  exemplo de texto seu), mais parecido com você fica.
- Ele **nunca inventa** número, depoimento, antes/depois ou case. Se a peça precisa de
  prova, ele pede pra você.
- Ele **sugere** o conteúdo; **quem publica é você**.
- Seus dados ficam **100% na sua máquina** (`.holofote/`), fora do controle de versão.

## Requisitos

- Claude Code instalado.
- Python 3 (já vem no Mac e na maioria dos Linux — nada para instalar além disso).

## Privacidade

Tudo (perfil, calendário, banco de ideias) fica só na sua máquina, na pasta
`.holofote/`, que é automaticamente adicionada ao `.gitignore`. Nada é enviado para
fora.
