# 🎬 Claquete — sua equipe de YouTube dentro do Claude Code

A **Claquete** é um time de 6 subagentes do Claude Code que tocam o seu canal do YouTube como um estúdio de verdade: cada um tem uma função, e juntos eles **pesquisam a pauta, escrevem o roteiro, criam a thumbnail e o título, otimizam o SEO, montam o pacote de publicação e analisam o desempenho** — com contexto isolado por função, do jeito que dá mais qualidade.

Feita para quem quer **produzir conteúdo no YouTube com constância** sem montar (e pagar) uma equipe inteira.

## A equipe

| Agente | Função | Quando entra |
|--------|--------|--------------|
| 🔎 **Pauteiro** | Descobre sobre o que gravar: pesquisa demanda real e ângulos | "me dá ideias de vídeo", "pauta da semana", "vale a pena um vídeo sobre X" |
| ✍️ **Roteirista** | Escreve o roteiro: gancho, retenção e CTA na voz do canal | "escreve o roteiro de X", "roteiro de Short sobre Y" |
| 🎨 **Diretor de Arte** | Cria a thumbnail (conceito) e 3–5 títulos clicáveis | "cria a thumbnail", "me dá opções de título" |
| 🔍 **Otimizador** | Monta o SEO: descrição, tags, capítulos, palavras-chave | "monta o SEO", "descrição e tags", "capítulos do vídeo" |
| 🎬 **Produtor** | Coordena tudo e monta o pacote de publicação + checklist | "produz esse vídeo do começo ao fim", "monta o pacote pra publicar" |
| 📊 **Analista** | Lê os números do vídeo no ar e diz o que melhorar | "esse vídeo fez X views e Y% de CTR, o que eu faço melhor?" |

Cada um roda como um **subagente** (contexto próprio), então o trabalho de um não polui o do outro. Você conversa naturalmente com o Claude e o agente certo entra em cena — ou você chama pelo nome.

## O que a Claquete faz (e o que não faz)

A Claquete é a sua **equipe de estratégia e criação de conteúdo**. Ela entrega tudo o que é texto e planejamento, prontinho para você publicar:
- pauta, roteiro, brief de thumbnail, títulos, descrição, tags, capítulos, pacote de publicação e análise.

Ela **não grava, não edita, não gera o vídeo e não publica sozinha** — quem faz isso é você (ou as ferramentas que você já usa). É honesto: a Claquete não precisa de nenhuma chave de API e não promete "canal no automático que posta sozinho". Ela faz o trabalho pesado de cabeça e te entrega o pacote pronto.

## Instalação

1. Descompacte a pasta `Claquete/`.
2. Copie os agentes para o seu projeto (ou para o seu Claude Code global):
   - **Por projeto:** copie a pasta `.claude/agents/` para a raiz do seu projeto.
   - **Global (todos os projetos):** copie os arquivos de `.claude/agents/` para `~/.claude/agents/`.
3. Mantenha a pasta `referencias/` junto (os agentes leem os moldes de gancho, formato, thumbnail e SEO de lá).
4. Abra o Claude Code na raiz da pasta e rode o setup (recomendado):

   > **"Rode o setup da Claquete."**

   Ele pergunta sobre o seu canal (nicho, público, tom, formato, frequência, limites), grava em `.claquete/config.md` (ignorado pelo git) e remove sozinho os arquivos de instalação.

> Sem o setup também funciona — cada agente pergunta o essencial do canal antes de trabalhar. O setup só deixa tudo mais afiado e no seu tom.

## Fluxo recomendado (da ideia ao "publicar")

1. **Pauta** → *"Pauteiro, me dá 5 ideias de vídeo pra essa semana."*
2. **Roteiro** → *"Roteirista, escreve o roteiro da ideia 2."*
3. **Arte** → *"Diretor de Arte, cria a thumbnail e os títulos."*
4. **SEO** → *"Otimizador, monta a descrição, tags e capítulos."*
5. **Pacote** → *"Produtor, junta tudo no pacote de publicação."*
6. **Depois de publicar** → *"Analista, fez 1.500 views e 3% de CTR — o que eu melhoro?"*

Você não precisa seguir tudo sempre — chame só quem o trabalho pede. Ou peça ao **Produtor** para tocar o vídeo inteiro de uma vez.

## Requisitos
- **Claude Code** instalado.
- Uma pasta para o seu canal (qualquer projeto serve). Os agentes se adaptam ao seu nicho.
- **Nenhuma chave de API.** A Claquete trabalha em texto; quem grava e publica é você.

## Privacidade & segurança
- O `.claquete/config.md` e as pastas de trabalho guardam só informações do seu canal e ficam **fora do git**.
- **Nunca** cole segredos (chaves, senhas) no config — a Claquete não precisa disso.
- A Claquete nunca inventa número, depoimento ou resultado, e nunca faz promessa que o vídeo não cumpre.

## Licença
MIT — use, modifique e distribua à vontade.

---
*Feita com 🎬 para a comunidade. Luz, câmera, ação!*
