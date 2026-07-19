---
name: fachada
description: Constrói o site profissional de uma página do seu negócio — sem "cara de IA". Use quando o usuário quiser criar um site, landing page ou página para a empresa/negócio/serviço dele ("quero um site", "criar um site pro meu negócio", "preciso de uma landing page", "fazer a página da minha empresa", "meu site tá feio/antigo", "site profissional", "site sem cara de IA"), quiser ajustar/melhorar um site feito pela Fachada, passar a vistoria de qualidade ou publicar o site no ar.
---

# Fachada — o site do seu negócio, sem cara de IA

A Fachada transforma uma conversa em português num site profissional de uma página: entrevista o dono, escolhe uma direção de design com personalidade, monta um único arquivo HTML pronto para publicar, passa uma vistoria de qualidade e ensina a colocar no ar — tudo sem o dono escrever uma linha de código.

## Setup de primeira execução

**Se a pasta `setup/` existir nesta skill, este é o primeiro uso.** Antes de qualquer outra coisa, leia `setup/PRIMEIRA_EXECUCAO.md` e siga o passo a passo de lá: colete os dados do negócio em conversa, grave `.fachada/config.md`, adicione `.fachada/` ao `.gitignore` e, ao final, **apague a pasta `setup/` e remova esta seção do SKILL.md** (autodestruição do setup). Se `setup/` não existir, o setup já foi feito — siga direto para os modos abaixo.

## Regras de ouro (valem em todos os modos)

1. **Nunca invente.** Nada de depoimento fictício, número inventado ("+500 clientes" sem fonte), certificação que o dono não citou, prêmio imaginário. Se não existe, a seção sai do site.
2. **Nunca use foto que não existe.** Só imagens que o dono colocou em `fachada-site/imagens/`. Sem foto? O design segue lindo só com tipografia, cor e formas (CSS) — jamais invente URL de imagem ou use foto de banco genérica.
3. **Anti-cara-de-IA é obrigatório.** Antes de escrever qualquer HTML, leia `references/estilos.md` e siga as proibições e a direção escolhida à risca.
4. **Um arquivo só.** O site é um único `index.html` autossuficiente (CSS e JS embutidos; só as fontes do Google como recurso externo). Fácil de hospedar em qualquer lugar.
5. **WhatsApp primeiro.** O caminho de contato principal é o WhatsApp do negócio (botão flutuante + CTAs), com telefone e endereço como apoio.
6. **Tudo local, tudo do dono.** Config em `.fachada/`, site em `fachada-site/`. Nenhum dado sai da máquina; quem publica é o dono, quando quiser.
7. **Português impecável.** Todo texto do site com acentuação e gramática perfeitas.

## Onde ficam as coisas

| Caminho | O que é |
|---|---|
| `.fachada/config.md` | Dados do negócio coletados no setup/entrevista (git-ignored) |
| `fachada-site/index.html` | O site — um único arquivo |
| `fachada-site/imagens/` | Fotos reais que o dono quiser usar (logo, equipe, trabalhos) |

## Modos

Detecte o modo pela intenção da mensagem. Em dúvida, pergunte em uma linha.

### 1. Entrevista — "quero um site", "criar site pro meu negócio"
Leia `references/entrevista.md` e conduza a conversa de lá:
1. Se `.fachada/config.md` existir, **não pergunte de novo o que já está lá** — confirme em uma linha e pergunte só as lacunas.
2. Detecte o **arquétipo** do negócio (tabela na referência) e faça as perguntas específicas dele (3-5, no máximo duas rodadas).
3. Pergunte pelos materiais: logo? fotos reais? cores da marca? Se tiver, peça para colocar em `fachada-site/imagens/`.
4. Apresente **2-3 direções de design** de `references/estilos.md` adequadas ao arquétipo, cada uma descrita em uma frase de gente ("elegante e sóbrio, como escritório de advocacia caro"). O dono escolhe — ou você decide por ele se ele pedir.
5. Grave/atualize tudo em `.fachada/config.md` e siga direto para o modo Montar. Não peça permissão para continuar.

### 2. Montar — gerar o site
1. Leia `.fachada/config.md`, `references/estilos.md` (direção escolhida + proibições), `references/secoes.md` (plano de seções por arquétipo) e `references/seo_local.md` (title, meta, JSON-LD).
2. Planeje antes de codar: direção nomeada, par tipográfico, paleta (fundo dominante + tinta + 1 acento tirado do mundo do negócio), elemento-assinatura, ordem das seções. Escreva o plano em 5 linhas para o dono ver.
3. Gere `fachada-site/index.html` completo: um arquivo, mobile-first, seções conforme o plano, botão flutuante de WhatsApp, links `tel:` e `wa.me`, endereço linkado no Google Maps, JSON-LD LocalBusiness, meta tags e OG tags.
4. Rode a vistoria: `python3 scripts/fachada.py checar fachada-site/index.html`. Corrija todo ❌ e avalie cada ⚠️. Só apresente o site ao dono com a vistoria limpa.
5. Mostre o resultado: diga o caminho do arquivo e peça para abrir com dois cliques no navegador. Sugira os ajustes mais prováveis ("quer trocar alguma cor? algum texto?").

### 3. Ajustar — "troca a cor", "muda o texto", "adiciona uma seção"
1. Edite `fachada-site/index.html` conforme o pedido, mantendo a direção de design coerente (não vire colcha de retalhos).
2. Mudou informação do negócio (horário, serviço, telefone)? Atualize também `.fachada/config.md`.
3. Re-rode a vistoria após qualquer mudança e mantenha-a limpa.

### 4. Vistoria — "confere meu site", "tá bom pra publicar?"
1. Rode `python3 scripts/fachada.py checar fachada-site/index.html` e traduza o resultado em português de gente: o que está ✅, o que precisa de atenção e por quê.
2. Complete com a leitura humana: os textos estão específicos do negócio (sem frase de enchimento)? A direção de design está sendo honrada? Checklist anti-cara-de-IA de `references/estilos.md` passou?
3. Para conferir legibilidade de uma combinação de cores: `python3 scripts/fachada.py contraste "#cor-do-texto" "#cor-do-fundo"`.

### 5. Publicar — "como coloco no ar?", "publica meu site"
Leia `references/publicar.md` e guie o dono pelo caminho mais simples para o caso dele (arrastar a pasta no Netlify Drop é o padrão para quem não tem nada; cPanel/hospedagem própria para quem já tem; GitHub Pages para quem usa GitHub). Inclua: domínio próprio (registro.br), teste no celular, botão do WhatsApp funcionando, e onde divulgar o link (Google Meu Negócio, bio do Instagram).

### 6. Renovar — "já tenho site, quero um novo"
1. Peça o endereço do site atual ou os textos dele (colados na conversa).
2. Aproveite o que é fato (serviços, endereço, história) — **nunca** os defeitos (textos genéricos, visual datado).
3. Siga o fluxo Entrevista (só lacunas) → Montar. Diga explicitamente o que você melhorou em relação ao site antigo.

## Motor de vistoria (scripts/fachada.py)

100% biblioteca padrão do Python — nenhuma instalação necessária.

```bash
python3 scripts/fachada.py checar fachada-site/index.html   # vistoria completa do site
python3 scripts/fachada.py contraste "#1A1A1A" "#F5F0E8"    # legibilidade de um par de cores (WCAG)
```

A vistoria confere: title e meta description (presença e tamanho), viewport, um único H1, `alt` em todas as imagens, link de WhatsApp/telefone, JSON-LD LocalBusiness, OG tags, `lang="pt-BR"`, texto placeholder esquecido, emoji em título/botão, scripts externos indevidos e peso do arquivo. Saída em PT-BR com ✅/⚠️/❌; código de saída 1 se houver erro.

## O que a Fachada NÃO faz

- Não cria sistema, loja virtual com carrinho, área de login nem blog com painel — é a página profissional do negócio (e faz isso muito bem).
- Não registra domínio nem contrata hospedagem pelo dono — ensina o caminho, quem contrata é ele.
- Não publica nada sozinha: o site só vai ao ar pelas mãos do dono.
