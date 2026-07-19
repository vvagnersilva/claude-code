# PIPELINE.md — The Cinematic 3D-Scroll Website Pipeline

> This document is the **reconciled logic** of two sources, written **before** the
> worker code, exactly as instructed. Every claim is tagged with its origin:
> `[VIDEO]` = a video tutorial on the technique,
> `[PDF]` = a prompt-pack guide for cinematic AI websites,
> `[BOTH]` = stated in both, `[OURS]` = engineering decision made to turn the
> manual, human-in-the-loop method into a runnable, deterministic pipeline.

---

## 0. What the two sources actually describe

Neither source is a "pipeline" in the software sense. They describe a **manual,
conversational workflow**: a human pastes one big prompt into Claude Code (running
the Fable 5 model), Claude talks to the **Higgsfield MCP** to generate cinematic
video clips with **Seedance 2.0**, then Claude hand-writes a website that
scroll-scrubs those clips. `[BOTH]`

Our job was to **operationalize** that into a repeatable worker: a brief goes in,
a finished cinematic 3D-scroll website comes out, through explicit stages, with the
paid generation step cleanly stubbed so the site still renders with real,
working 3D. `[OURS]`

---

## 1. The core idea, extracted verbatim

### 1.1 The "3D scroll" is a scrubbed frame sequence — not a game engine
> *"this scrolling effect that you're seeing here, this is technically a video
> that's separated in multiple frames and then also images as well."* `[VIDEO]`

So the headline effect is **frame-sequence scroll-scrubbing**: a cinematic clip is
decoded to N still frames; scroll progress `p ∈ [0,1]` maps to a frame index; the
frame is painted to a `<canvas>`. Scrolling *is* scrubbing the camera move. `[VIDEO]`

The PDF says the same in build language:
> *"scroll-scrub the hero orbit as a canvas frame sequence so scrolling rotates
> the watch."* `[PDF, Prompt 01]`

### 1.2 Consistency is bought with ONE hero image
> *"Every prompt tells Claude to generate ONE hero image first, then pass it as a
> reference to every video clip. That's what keeps your product, person, or place
> identical across all shots. Don't remove that step."* `[PDF, How-to #2]`
> *"Consistency beats quality... Always use the hero-image reference."* `[PDF, Pro tip #1]`

### 1.3 Continuity = chained clips (final frame → next start frame)
This is the mechanism behind "seamless section-to-section", the whole point of the
build:
> *"Seedance 2.0 accepts a start image and end image. The journey prompts (ocean,
> hypercar) use each clip's final frame as the next clip's start frame — five clips
> that scrub like one unbroken camera move."* `[PDF, How-to #3]`
> *"generate clips in order and use each clip's FINAL frame as the START image of
> the next ... so all five join into one seamless, unbroken descent."* `[PDF, Prompt 02]`

### 1.4 The website layer, every time
Across all 10 PDF prompts the *WEBSITE* half is the same recipe: `[PDF]`
- **scroll-scrub** the hero clip as a canvas frame sequence,
- **Lenis** smooth scroll,
- **text reveals pinned to scroll position** (GSAP ScrollTrigger, implied),
- a **fixed HUD / progress indicator** (depth meter, speed 0→250mph, space names),
- **sections** color-graded and pinned per "zone",
- **dark background + a single accent color**, condensed/serif display type,
- ends with *"Launch on localhost and verify ... before telling me it's done."*

### 1.5 Model & tooling stack
- Claude Code on the **Fable 5** model, effort **extra/max**. `[VIDEO]`
- **Higgsfield MCP** connected as a custom remote connector. `[VIDEO]`
- **Seedance 2.0** for video (`std` mode, 1080p, 16:9, no audio, ~8s/clip). `[BOTH]`
- **Nano Banana Pro / GPT-Image** for the hero image; 4K image quality matters
  because frames are scrubbed at scroll resolution. `[VIDEO]`

### 1.6 Pro tips that shaped our defaults
- *"Generate 2–3 takes of your hero clip only. The hero scrub is 80% of the wow."* `[PDF]`
- *"Ask Claude to compress the videos... cuts file size ~90%, buttery scroll."* `[PDF]`
- *"Going live is one more prompt"* → GitHub + Cloudflare Pages. `[PDF]`

---

## 2. The gap we had to close (why this isn't just the prompt)

The source method needs **Higgsfield credits + a connected MCP + a human iterating**.
A worker can't depend on paid credentials to prove it works. Two decisions: `[OURS]`

1. **Two continuity engines, one interface.**
   - `webgl` (default) — a **real Three.js scene with a scroll-driven camera path**.
     This is genuinely-working 3D with zero external services. It *is* the camera
     move the Seedance clips only *simulate*, so it renders continuity for real.
   - `frameseq` — the exact PDF technique: a **canvas frame-sequence scrubber**. It
     consumes decoded frames. When Higgsfield is wired in, its clips feed this mode.
     Until then, the asset stage renders **procedural placeholder frames** so this
     mode also runs.
2. **The generation step is a documented stub, never faked.** `providers.js` exposes
   `generateHeroImage()` and `generateClip()` with the real Higgsfield/Seedance
   contract (endpoint, env var, params). With no `HIGGSFIELD_API_KEY` it returns
   **procedural placeholder assets** and records `stubbed: true` in the manifest —
   it never pretends a real render happened.

---

## 3. The pipeline — six stages

Brief ⟶ **INTAKE** ⟶ **PLAN** ⟶ **ASSETS** ⟶ **BUILD** ⟶ **VERIFY** ⟶ **DELIVER** ⟶ Site

### Stage 1 — INTAKE  (`pipeline/lib/intake.js`)
Accept a brief as **YAML or JSON**, or a **`--topic`/`--niche` CLI one-liner**.
Validate required fields, fill defaults, choose a **prompt-pack template** by niche.
Mirrors *"Paste the whole prompt, unedited, the first time."* `[PDF]` — the brief
*is* that paste, structured.

### Stage 2 — PLAN  (`pipeline/lib/plan.js`)  ← where the source logic lives
Turn the brief into a **storyboard + continuity map**:
- Pick a **world archetype** from the niche → camera-path shape:
  - `descent` (journey/experience — deep-sea, ascent, rocket), `[PDF Prompt 02/06/07]`
  - `orbit` (product / portfolio — watch, person), `[PDF Prompt 01/03]`
  - `assemble` (SaaS particle build), `[PDF Prompt 08]`
  - `reveal` (local business / agency single hero clip). `[PDF Prompt 05/09/10]`
- Expand the niche's **shot list** (hero + N clips) — straight from the PDF template.
- Build the **continuity map**: for each section→next, record *what carries over*
  (`carry: final-frame→start-frame`), the camera segment, and the transition. This
  is §1.3 encoded as data.
- Emit per-**waypoint** design: fog/zone color, particle style, subject, light,
  HUD value, and the copy — so BUILD is pure templating.

### Stage 3 — ASSETS  (`pipeline/lib/assets.js` + `providers.js`)
For each storyboard shot: `generateHeroImage()` once, then `generateClip()` per clip
**passing the hero image as reference** (§1.2) and, for chained archetypes, the prior
clip's **final frame as `start_image`** (§1.3). Real call if `HIGGSFIELD_API_KEY` is
set; otherwise a **procedural placeholder** (SVG gradient hero + a rendered frame
sequence) and `stubbed:true`. Writes `assets/manifest.json`.

### Stage 4 — BUILD  (`pipeline/lib/build.js` + `templates/`)
Assemble a **self-contained static site** from the storyboard:
- fixed full-viewport `<canvas>`; **Three.js** scene; **camera path** = CatmullRom
  spline (`descent`/`reveal`) or orbit ring (`orbit`); scroll drives camera `t`.
- **Lenis** smooth scroll + **GSAP ScrollTrigger** pinned text reveals (§1.4).
- fog/particle color **lerps continuously** between waypoints → seamless morph (§1.3).
- fixed **HUD** counting the brief's metric; per-section copy; dark + single accent.
- vendored libs in `/vendor` → runs offline, no CDN. `[OURS]`

### Stage 5 — VERIFY  (`pipeline/lib/verify.js`)
Boot a static server, drive **Playwright** headless: assert a **live WebGL context**
on the canvas, scroll to K positions, screenshot each, and assert the **rendered
pixels change across scroll** (continuity is really happening, not a static image).
Mirrors *"verify every scroll animation works before telling me it's done."* `[BOTH]`

### Stage 6 — DELIVER  (`pipeline/lib/deliver.js`)
Write the finished site to `output/<slug>/`, copy QC screenshots to `qc/`, print the
**absolute path**. (Going live = the one extra deploy prompt from Pro-tip #4. `[PDF]`)

---

## 4. Source → stage traceability

| Pipeline element | Source | Where |
|---|---|---|
| One structured brief = "one prompt, unedited" | `[PDF]` | How-to #1 |
| Hero-image reference on every clip | `[PDF]` | How-to #2, Pro-tip #1 |
| Chained final-frame→start-frame continuity | `[PDF]` | How-to #3, Prompts 02/06/07 |
| Frame-sequence canvas scrub = the "3D scroll" | `[VIDEO]` | "video separated in multiple frames" |
| Lenis + pinned text + HUD + dark/single-accent | `[PDF]` | Website half of all 10 prompts |
| Seedance `std`/1080p/16:9/~8s params | `[BOTH]` | VISUALS blocks |
| Compress clips for web | `[PDF]` | Pro-tip #3 |
| Launch on localhost + verify before "done" | `[BOTH]` | every prompt's last line |
| 10 niche templates (product…gym) | `[PDF]` | Prompts 01–10 |
| WebGL camera-path engine as the working stand-in | `[OURS]` | — |
| Clean Higgsfield stub, never fake-green | `[OURS]` | — |

See `docs/logic.md` for the deep technical explanation of the continuity engine.
