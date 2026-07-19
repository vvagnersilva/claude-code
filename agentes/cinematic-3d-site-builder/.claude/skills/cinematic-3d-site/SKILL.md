---
name: cinematic-3d-site
description: >
  Turn a brief (topic, brand, sections, vibe) into a finished award-winning-style
  cinematic website with real 3D animation and a scroll-driven continuity effect
  (seamless section-to-section, morphing hero→section, camera-path-on-scroll).
  Use whenever asked to build a "3D scroll", "cinematic", "Higgsfield/Fable5-style",
  or continuity-animation website. Runs a six-stage pipeline end to end and
  Playwright-verifies the result.
---

# Skill: cinematic-3d-site

Operational workflow for the worker. It reifies the method reconciled in
`PIPELINE.md` (from the tutorial video + the Fable5/Higgsfield PDF).

## When to use
Any request to build a cinematic / 3D-scroll / continuity-animation website, a site
"like Higgsfield/Fable 5", a scroll-driven journey, or an award-winning-style landing
page for a product, person, place, or brand.

## The six stages (run in order — never skip verify)

### 1 · INTAKE
Accept a brief as YAML/JSON (`--brief path`) **or** a CLI one-liner
(`--topic "..." --niche restaurant`). Validate + default-fill. Choose a prompt-pack
template by niche (`prompt-pack/templates.js`). Ship `briefs/example.brief.yaml` as
the canonical example.

### 2 · PLAN  ← the source logic lives here
Brief → **storyboard + continuity map**:
- pick a **world archetype** (`descent` / `orbit` / `assemble` / `reveal`) from niche,
- expand the **shot list** (hero image + clips) from the template,
- record the **continuity map** — for each section→next: what carries over
  (`final-frame → start-frame` for chained archetypes), camera segment, transition,
- emit per-**waypoint** design (fog color, particle style, subject, light, HUD, copy).

### 3 · ASSETS  (Higgsfield / Seedance — stub-safe)
For each shot: generate ONE hero image, then each clip **referencing the hero image**
(PDF How-to #2) and, when chained, the prior clip's **final frame as `start_image`**
(PDF How-to #3). Real calls when `HIGGSFIELD_API_KEY` is set; otherwise **procedural
placeholder assets** + `stubbed:true`. Writes `assets/manifest.json`.
NEVER fabricate a successful render.

### 4 · BUILD
Assemble a **self-contained static site** from the storyboard: fixed WebGL canvas,
Three.js camera-path scene, Lenis smooth scroll, GSAP ScrollTrigger pinned reveals,
continuous fog/particle color-grade between waypoints, a fixed HUD counter, dark +
single-accent design. Vendored libs → runs offline.

### 5 · VERIFY (mandatory, Playwright)
Serve the site, drive Playwright: assert a **live WebGL context**, scroll to K
positions, screenshot each, assert **pixels change across scroll** (continuity is
real). Fail loudly if the scene is static or WebGL is dead.

### 6 · DELIVER
Write to `output/<slug>/`, copy screenshots to `qc/`, print the absolute path.

## Guardrails
- Follow `PIPELINE.md`/`docs/logic.md` — do not improvise a generic scroll site.
- The continuity/3D layer must be **genuinely working**, not faked.
- Keep the output **self-contained** (no CDN at view time).
- Always run `verify` before reporting done; attach screenshots as proof.

## Commands
```bash
npm install
npm run build -- --brief briefs/example.brief.yaml     # full pipeline
npm run build -- --topic "a strength gym" --niche fitness
npm run verify -- output/abyssal                        # re-run QC only
```
