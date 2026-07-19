# 3D-MOTION-WEBSITES — Cinematic 3D-Scroll Website Builder

> 🇧🇷 **Novo por aqui? Rode `npm run setup`** — o assistente em português configura tudo e
> constrói um site de demonstração gratuito e verificado. Guia rápido: [COMECE-AQUI.md](COMECE-AQUI.md).



A self-contained **worker** that turns a **brief** into a finished,
award-winning-style **cinematic website** with genuine 3D animation and a strong
scroll-driven **continuity** effect — seamless section-to-section transitions,
a morphing hero→section, and a camera path driven by scroll (Higgsfield / Fable 5
style).

It operationalizes a manual, human-in-the-loop method for cinematic AI websites
into a **repeatable, verified
pipeline**. The paid AI-video step (Higgsfield / Seedance 2.0) is cleanly stubbed
so the site **always renders with real, working 3D** — see
[`PIPELINE.md`](PIPELINE.md) and [`docs/logic.md`](docs/logic.md).

> **Proof it works:** two demos are generated and Playwright-verified in this repo
> — `output/abyssal/` (deep-sea descent, `webgl`) and `output/aurum-noir/` (luxury
> watch, `orbit`). Both pass QC (live WebGL + pixels that change across scroll).
> Screenshots in `qc/screenshots/`.

---

## Quick start

```bash
npm install                      # js-yaml + playwright
npx playwright install chromium  # one-time, for the VERIFY stage

# build the flagship demo (deep-sea continuity descent) end-to-end
npm run build -- --brief briefs/example.brief.yaml

# or from a one-line topic
npm run build -- --topic "a wood-fire steakhouse in Lisbon" --niche restaurant

# view any built site
node pipeline/lib/server.js output/abyssal 4890   # → http://127.0.0.1:4890
```

The build prints the **absolute path** of the finished site under `output/<slug>/`.

---

## What it does — the six-stage pipeline

`brief ⟶ INTAKE ⟶ PLAN ⟶ ASSETS ⟶ BUILD ⟶ VERIFY ⟶ DELIVER ⟶ site`

| Stage | File | What happens |
|---|---|---|
| **1 · Intake** | `pipeline/lib/intake.js` | Parse a YAML/JSON brief (or `--topic`), pick a prompt-pack template by niche. |
| **2 · Plan** | `pipeline/lib/plan.js` | Brief → **storyboard + continuity map**: world archetype, shot list, per-waypoint fog/particles/subject/HUD, and the section-to-section handoffs. |
| **3 · Assets** | `pipeline/lib/assets.js` + `providers.js` | Generate ONE hero image + clips via **Higgsfield/Seedance** (real if keyed; otherwise clean **procedural placeholders**, `stubbed:true`). |
| **4 · Build** | `pipeline/lib/build.js` | Assemble a **self-contained static site**: fixed WebGL canvas, Three.js camera path, Lenis smooth scroll, GSAP ScrollTrigger reveals, continuous color-grade, fixed HUD. |
| **5 · Verify** | `pipeline/lib/verify.js` | Drive **Playwright**: assert live WebGL + an active render loop + **pixels that change across scroll**; save screenshots. |
| **6 · Deliver** | `pipeline/lib/deliver.js` | Write to `output/<slug>/`, copy QC shots, print the absolute path. |

---

## The continuity / 3D effect (two engines, one interface)

- **`webgl` (default)** — a **real Three.js scene with a scroll-driven camera
  path**. Scroll `p ∈ [0,1]` moves the camera along a CatmullRom spline (descent /
  reveal) or an orbit ring (product / portfolio). Fog + particle colors **lerp
  continuously between waypoints**, so sections morph with no cut. Floodlights
  ignite in dark zones; a HUD counts with scroll. Zero external services — this
  is the genuinely-working 3D layer.
- **`frameseq`** — the exact PDF technique: a **canvas frame-sequence scrubber**
  (`scroll → frame index → drawImage`). It consumes decoded Seedance clips when
  Higgsfield is connected, or the procedural SVG frames the asset stage writes.
  Enable with `--engine frameseq`.

Full explanation: [`docs/logic.md`](docs/logic.md).

---

## Plugging in real AI generation (Higgsfield / Seedance 2.0 / fal.ai)

By default the asset stage is **stubbed** (no credentials required) and the site
still renders in full. Provider priority (first credential found wins), read from
the environment or a repo-root `.env`:

1. **`HIGGSFIELD_API_KEY`** — direct Higgsfield HTTP API (`HIGGSFIELD_BASE_URL`
   optional). Note: the consumer Higgsfield product is **browser-only** (Clerk
   auth, no public REST API) — see the browser session below.
2. **`FAL_KEY`** — fallback via **fal.ai**, same ByteDance models:
   `bytedance/seedance-2.0/{reference,image,text}-to-video` for clips and
   `fal-ai/nano-banana-pro` for the hero image (queue API, submit → poll →
   result; local start-frames are uploaded to fal storage automatically).
3. Neither → clean procedural placeholders, marked `stubbed:true`.

```bash
# .env (gitignored) or exported:
FAL_KEY=<key-id>:<key-secret>               # fallback real generation
# HIGGSFIELD_API_KEY=sk-...                 # primary, if an API key exists
npm run build -- --brief briefs/example.brief.yaml

# Real clips are PAID — force free placeholder assets for layout/QC iterations:
ASSETS_MODE=stub npm run build -- --brief briefs/example.brief.yaml
```

### Higgsfield browser session

```bash
npm run higgsfield:login    # restore saved cookies → verify via Clerk → re-save
```

The saved Playwright storage state lives in `.claude/auth/higgsfield-storage-state.json`
(gitignored). The durable `__client` refresh token (~1 y) re-logs-in with **no 2FA**;
only a fully expired session needs a fresh email + password + emailed-code login
(`HIGGSFIELD_EMAIL` / `HIGGSFIELD_PASSWORD` in `.env`).

The exact request contract (Seedance `std`/1080p/16:9/~8s, hero-image reference on
every clip, `start_image = previous clip's final frame` for chained continuity)
lives in [`pipeline/lib/providers.js`](pipeline/lib/providers.js). `ffmpeg` decodes
the returned clips into the frame sequence for `frameseq` mode. Nothing is ever
faked green: a stubbed asset is explicitly marked `stubbed:true` in
`assets/manifest.json`.

Real-run outputs: `assets/hero.jpg` (downloaded hero), `assets/clips/*.mp4`
(master clips — kept as deliverables, NOT loaded by either engine at runtime;
safe to drop when deploying), `assets/frames/frame-%04d.jpg` (the continuous
sequence `frameseq` scrubs).

**Quality bar (mandatory).** Generation defaults to 1080p; frames decode at the
master's native width up to `generation.frameMaxWidth` (default 1920px) with
lanczos + JPEG `-q:v 2`; the frameseq canvas is devicePixelRatio-aware with
high-quality resampling. VERIFY records the frame width in the manifest and
**fails QC below 1280px**. The resume cache keys on resolution, so lower-quality
assets are never silently reused for a higher-quality build. A paid run builds both engines for one spend:

```bash
node pipeline/run.js --brief briefs/nocturne.brief.yaml                  # pays once (webgl)
node pipeline/run.js --brief briefs/nocturne.brief.yaml \
  --engine frameseq --out output/nocturne-frameseq --reuse-assets output/nocturne
```

---

## Briefs

A brief is YAML or JSON — only `brand` (or `--topic`) is required; everything else
falls back to the niche template. See [`briefs/schema.md`](briefs/schema.md).
Examples: [`briefs/example.brief.yaml`](briefs/example.brief.yaml) (deep-sea) and
[`briefs/watch.brief.json`](briefs/watch.brief.json) (luxury watch).

**Niches** (from the PDF's 10 templates, + aliases like `watch`, `gym`,
`penthouse`, `hypercar`): `luxury-product`, `journey`, `portfolio`, `ecommerce`,
`restaurant`, `real-estate`, `automotive`, `saas`, `agency`, `fitness`.

**Shot prompts & style.** A brief may override the niche template's shot list with
its own `heroImage` (string) and `visuals` (array of `{id, kind, prompt}`). Every
shot prompt then gets the **style preset** appended — the visual DNA (light,
sharpness, atmosphere; never the subject) defined in `prompt-pack/templates.js`
`STYLE_PRESETS`. Default is `cinematic-macro-noir` (near-black void, warm specular
key light, ultra-macro sharpness, drifting dust motes, `{ACCENT}` → the brief's
accent color); set `style: none` to disable. Ready-to-run examples:
`briefs/{kaji,velluto,nocturne,eidolon,thock}.brief.yaml`.

---

## Repo layout

```
.claude/            worker persona (claude.md) + the cinematic-3d-site SKILL
prompt-pack/        the 10 PDF prompt templates as structured data
briefs/             example briefs (YAML/JSON) + schema
pipeline/           run.js orchestrator + lib/ stages + lib/templates/ (engine, css)
vendor/             three.js, gsap, ScrollTrigger, lenis (vendored → offline)
output/<slug>/      generated sites (self-contained)
qc/screenshots/     Playwright QC screenshots
docs/logic.md       deep-dive on the continuity engine
PIPELINE.md         reconciled logic from the video + PDF (cited)
```

## CLI reference

```
node pipeline/run.js --brief <file>            # YAML/JSON brief
                     --topic "<idea>" --niche <n>
                     --engine webgl|frameseq   # default webgl
                     --out <dir>               # default output/<slug>
                     --no-verify               # skip Playwright QC
npm run verify -- output/<slug>                # re-run QC on a built site
npm run serve  -- output/<slug> 4890           # static preview server
```

## Requirements
Node ≥ 18, and (for the VERIFY stage only) Playwright's chromium. Optional:
`ffmpeg` (real-clip decode), `HIGGSFIELD_API_KEY` or `FAL_KEY` (real generation).
