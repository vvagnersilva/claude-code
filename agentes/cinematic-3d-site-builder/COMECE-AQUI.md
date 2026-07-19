# 🎬 Comece aqui

Este kit transforma um **brief** (uma ideia + algumas seções em YAML) num
**site cinematográfico completo**, com animação 3D real e o efeito de
continuidade no scroll — seção fluindo para seção sem cortes, estilo
Higgsfield / Awwwards.

## Configuração em 1 comando

```bash
npm run setup
```

O assistente (em português) faz tudo:

1. Verifica o Node (≥ 18) e instala as dependências.
2. Instala o Chromium do Playwright — o QC automático que **prova** que o 3D renderiza.
3. Verifica o ffmpeg (opcional; só para clipes reais).
4. Pede suas credenciais e **valida a chave ao vivo** (mostra até o saldo da fal.ai).
5. Constrói um site de demonstração **gratuito** e verificado, de ponta a ponta.

## Os dois modos

| Modo | Custo | O que gera |
|---|---|---|
| **Gratuito (stub)** | R$ 0 | O site 3D completo com assets procedurais — perfeito para aprender, iterar layout e copy. |
| **Real (fal.ai)** | ~US$ 10–30/site | Imagens (Nano-Banana) e clipes de vídeo (Seedance 2.0) gerados por IA, encadeados frame-a-frame. O gasto é medido e mostrado em cada build. |

Sem chave nenhuma, **tudo funciona** no modo gratuito.

## Comandos essenciais

```bash
# site gratuito a partir de uma ideia de uma linha:
ASSETS_MODE=stub npm run build -- --topic "uma cafeteria artesanal" --niche restaurant

# site a partir de um brief completo (6 exemplos prontos em briefs/):
npm run build -- --brief briefs/nocturne.brief.yaml

# abrir o resultado no navegador:
npm run serve -- output/<slug> 4890     # → http://127.0.0.1:4890

# variante frame-scrubber (usa os MESMOS assets, sem custo extra):
npm run build -- --brief briefs/nocturne.brief.yaml --engine frameseq \
  --out output/nocturne-frameseq --reuse-assets output/nocturne
```

## Onde mexer

- **`briefs/*.brief.yaml`** — os briefs de exemplo (faca damasco, espresso,
  perfume, hypercar, teclado, carro elétrico circular). Copie um e troque o
  conteúdo pela sua marca.
- **`briefs/schema.md`** — todos os campos do brief, incluindo `style`
  (o preset visual `cinematic-macro-noir`), `lang`/`ui` (localização) e
  `visuals` (os prompts dos clipes).
- **`README.md` / `PIPELINE.md` / `docs/logic.md`** — como o pipeline funciona
  por dentro (6 estágios: intake → plan → assets → build → verify → deliver).

## Garantias do pipeline

- **Nunca finge sucesso**: sem credenciais, os assets são marcados
  `stubbed: true` — jamais "verde falso".
- **QC de verdade**: o Playwright abre o site, confirma o contexto WebGL vivo,
  rola a página e verifica que os pixels mudam (continuidade), salvando
  screenshots em `qc/screenshots/`.
- **Barra de qualidade obrigatória**: geração 1080p, frames decodificados até
  1920px (lanczos, JPEG de alta qualidade) — o QC reprova frames reais abaixo
  de 1280px.
- **Custo transparente**: builds reais mostram o gasto medido (`fal spend this
  run: $X`) e há resume automático — um build interrompido nunca paga duas
  vezes pelo mesmo asset.

Bom scroll! 🚀
