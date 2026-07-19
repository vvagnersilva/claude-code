# Estilos — direções de design e as regras anti-cara-de-IA

O motivo nº 1 de um site "parecer feito por IA" é a ausência de decisão: o mesmo gradiente, os mesmos três cards, a mesma fonte neutra, para qualquer negócio. A Fachada resolve isso com **uma direção de arte nomeada por site**, escolhida pelo mundo real do negócio — e com proibições inegociáveis.

## Proibições (valem para TODAS as direções)

- **Gradiente roxo→azul** (ou rosa→roxo) em hero, botão ou fundo. É a assinatura visual de site genérico de IA.
- **Emoji como elemento de interface** (🚀✅🔥 em títulos, listas, botões). Ícones, quando precisar, em SVG de traço fino embutido — e poucos.
- **Ícone dentro de caixinha com gradiente** repetido em todo card.
- **Toda seção com 3 cards iguais.** Varie o ritmo: uma seção em lista, outra em duas colunas, outra de largura total com fundo alternado.
- **Inter, Roboto, Arial ou fonte de sistema como fonte de título.** No corpo podem servir; o display precisa de personalidade.
- **Frases de enchimento**: "soluções personalizadas", "qualidade e compromisso", "seu parceiro de confiança", "excelência em atendimento", "Bem-vindo ao nosso site". Zero informação = fora.
- **Headline com o nome da empresa.** O hero abre com a dor ou o resultado do cliente ("Vazamento? Chega hoje." e não "Bem-vindo à Hidráulica Silva").
- **Números e provas inventados.** Sem fonte confirmada pelo dono, não existe.
- **Foto de banco de imagens** de aperto de mãos / call center sorridente. Sem foto real, melhor nenhuma foto.
- **Sombras duras e bordas grossas.** Sombra em camadas suaves; borda de 1px em cor quase transparente.

## Obrigações (todas as direções)

- **Fundo dominante que não é branco puro** (`#FFFFFF` cru cansa; use um quase-branco com temperatura: marfim, gelo, areia — ou escuro, se a direção pedir).
- **Fórmula da paleta: 1 fundo dominante + 1 tinta (texto) + 1 acento.** O acento sai do mundo do negócio (o cobre do encanador, o verde-clínica, o âmbar da padaria) e aparece SÓ em CTAs e destaques.
- **Par tipográfico com intenção**: um display com personalidade + um corpo legível, do Google Fonts. Título grande de verdade no hero (clamp 2.4-4rem), `line-height` ~1.05 no display, corpo 16-18px com `line-height` 1.6-1.7.
- **Um elemento-assinatura por site**: a única ousadia memorável (um monograma, um padrão de fundo derivado do ofício, uma tipografia gigante, um recorte diagonal, uma faixa de cor). Uma só — o resto fica quieto e disciplinado.
- **Ritmo de seções**: alterne fundos (claro / tom / escuro), larguras e formatos. Duas seções seguidas nunca são visualmente idênticas.
- **Mobile-first**: perfeito a partir de 360px; toque ≥ 44px; botão de WhatsApp flutuante sempre alcançável.
- **`prefers-reduced-motion`** respeitado se houver animação; animações discretas (fade/slide de entrada, 300-600ms, uma vez).
- **Contraste AA**: texto corrido ≥ 4.5:1 com o fundo (confira com `python3 scripts/fachada.py contraste`).

## As 8 direções

Escolha 2-3 adequadas ao arquétipo e descreva cada uma em uma frase de gente para o dono escolher. **As cores listadas são pontos de partida** — sempre puxe o acento para algo do mundo daquele negócio específico.

### 1. Sob Medida — clássico confiável
- **Para**: advocacia, contabilidade, consultoria, corretores, serviços profissionais sérios.
- **Fontes**: Fraunces (display) + Source Sans 3 (corpo). Alternativa: Playfair Display + DM Sans.
- **Paleta**: marfim `#F7F4EE` + tinta grafite `#22252A` + um acento sóbrio (verde-escritório `#1F4B3F`, vinho `#5C1A2E` ou azul-tinteiro `#1B3A5B`).
- **Assinatura**: monograma tipográfico do nome ou numeração editorial das áreas de atuação.
- **Não usar quando**: o negócio é jovem/descontraído — vira caricatura de banco.

### 2. Oficina — força e trabalho
- **Para**: reformas, elétrica, hidráulica, ar-condicionado, mecânica, serralheria.
- **Fontes**: Archivo Black (display) + Archivo (corpo). Alternativa: Barlow Condensed bold + Barlow.
- **Paleta**: fundo escuro carvão `#17191C` (ou claro cimento `#EEECE6`) + tinta clara/escura + acento de obra (âmbar segurança `#F5A524`, laranja ferramenta `#E8590C`, cobre `#B2622D`).
- **Assinatura**: faixa diagonal tipo sinalização, números grandes de passos ("1. Você chama → 2. A gente vai → 3. Resolvido"), ou textura sutil de grade metálica em CSS.
- **Não usar quando**: saúde, estética — pesado demais.

### 3. Clínica Leve — cuidado e calma
- **Para**: dentista, psicólogo, fisioterapia, nutrição, estética clínica.
- **Fontes**: Sora (display) + Nunito Sans (corpo). Alternativa: Manrope + Mulish.
- **Paleta**: gelo `#F3F6F5` + tinta petróleo suave `#233735` + acento de saúde (verde-sálvia `#5B8A72`, azul-sereno `#4A7C99`, terracota clara `#C46E4F` para estética).
- **Assinatura**: formas orgânicas arredondadas de fundo (blobs discretos em CSS) ou uma linha fina que "respira" conectando as seções.
- **Não usar quando**: ofícios técnicos/urgência — soa mole para quem quer resposta rápida.

### 4. Sabor — apetite na tela
- **Para**: restaurante, cafeteria, confeitaria, marmitas, buffet.
- **Fontes**: Bricolage Grotesque (display) + Karla (corpo). Alternativa: Yeseva One + PT Sans para casas clássicas.
- **Paleta**: creme quente `#FBF3E4` + tinta café `#33261D` + acento do cardápio (tomate `#C4442A`, pistache `#7A8B3F`, caramelo `#B87A2B`).
- **Assinatura**: o cardápio como peça gráfica (itens com linha pontilhada até o preço) ou títulos enormes com nomes de pratos.
- **Regra extra**: comida É visual — sem foto real dos pratos, incentive o dono a tirar 3 fotos com o celular perto da janela; o site fica outro.

### 5. Vitrine Criativa — o trabalho é a estrela
- **Para**: fotógrafo, videomaker, designer, maquiadora, eventos, tatuador.
- **Fontes**: Syne (display) + Work Sans (corpo). Alternativa: Space Grotesk + IBM Plex Sans.
- **Paleta**: quase-preto `#121212` (ou off-white `#F5F3EF`) + tinta oposta + UM acento elétrico usado raríssimo (lima `#C6F432`, coral `#FF5A45`) — o portfólio dá a cor.
- **Assinatura**: tipografia gigante no hero (o nome ou o ofício ocupando a tela) e grade de portfólio assimétrica.
- **Regra extra**: essa direção EXIGE fotos reais do trabalho. Sem portfólio em `imagens/`, ofereça outra direção.

### 6. Energia — movimento e resultado
- **Para**: personal trainer, estúdio de treino, luta, corrida, quadras.
- **Fontes**: Anton (display, caps) + Public Sans (corpo). Alternativa: Archivo Expanded bold.
- **Paleta**: carvão `#141518` + branco-gelo + acento de impacto (verde-sinal `#3EE07A`, amarelo-ácido `#EAF15E`, vermelho `#E23B3B`).
- **Assinatura**: números grandes reais (anos, alunos, kg — só confirmados), palavras em caps com tracking apertado, recortes diagonais entre seções.
- **Não usar quando**: público 50+/saúde clínica — agressivo demais.

### 7. Raiz — tradição e bairro
- **Para**: barbearia, café de bairro, alfaiataria, produtos artesanais, negócios com história.
- **Fontes**: Yeseva One ou Abril Fatface (display) + PT Sans (corpo). Alternativa: Lora + Karla.
- **Paleta**: papel envelhecido `#F2EAD9` + tinta sépia-escura `#2E241C` + acento de ofício (verde-garrafa `#31473A`, bordô `#6B2B2B`, mostarda `#B98A2E`).
- **Assinatura**: selo/brasão tipográfico ("desde 2009"), filetes duplos, ornamentos discretos de rótulo antigo.
- **Não usar quando**: negócio de tecnologia ou inovação — envelhece o posicionamento.

### 8. Traço Firme — clareza técnica
- **Para**: consultoria de TI, automação, agências, engenharia, arquitetura.
- **Fontes**: Space Grotesk (display) + IBM Plex Sans (corpo). Alternativa: Sora + Inter (Inter SÓ no corpo).
- **Paleta**: gelo azulado `#F2F5F8` + tinta azul-noite `#1A2332` + acento técnico (azul-elétrico `#2563EB` com moderação, ou verde-terminal `#0F9D58`).
- **Assinatura**: grade visível (linhas-guia finas de fundo), rótulos monoespaçados discretos (IBM Plex Mono) numerando as seções, diagrama simples do processo.
- **Não usar quando**: negócios calorosos/artesanais — frio demais.

## Checklist anti-cara-de-IA (rodar antes de entregar)

1. A direção escolhida tem nome e foi seguida em TODAS as seções?
2. A fonte de título carrega personalidade (não é Inter/Roboto/Arial/sistema)?
3. O fundo dominante tem temperatura (não é `#FFFFFF` cru)?
4. O acento aparece só em CTA/destaques — e veio do mundo do negócio?
5. Existe UM elemento-assinatura memorável (e só um)?
6. Nenhuma seção repete o layout da anterior?
7. O hero abre com dor/resultado — não com "Bem-vindo" nem o nome da empresa?
8. Zero emoji em interface, zero gradiente roxo→azul, zero ícone-em-caixinha repetido?
9. Toda frase do site diz algo específico DESTE negócio?
10. No celular (360px) tudo funciona e o WhatsApp está a um toque?

Falhou qualquer item → corrigir antes de mostrar ao dono.
