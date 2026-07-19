# logic.md — How the continuity / 3D-scroll effect actually works

This is the engineering deep-dive behind `PIPELINE.md`. It explains the two
continuity engines, why they read as "one unbroken camera move," and how the
source method (Seedance chained clips) maps onto real, running code.

---

## 1. The perceptual trick we are reproducing

The source sites feel like **one continuous camera flight** even though they are
built from several 8-second clips. Two things create that illusion: `[PDF]`

1. **Scrubbing, not playing.** The clip is decoded to frames; scroll position
   selects the frame. There are no cuts because the *user's scroll* is the
   playhead — motion is perfectly monotonic with the wheel.
2. **Chaining.** Clip *n*'s last frame is clip *n+1*'s first frame, so the seam
   between two clips is a single shared frame — invisible.

Our engines reproduce both properties, one by rendering the camera move for real,
one by scrubbing frames exactly as the PDF describes.

---

## 2. Engine A — `webgl` (default, zero-dependency, genuinely 3D)

Instead of *scrubbing a pre-rendered camera move*, we **run the camera move live**
in Three.js and drive it with scroll. This is strictly more real than the source
method: there is an actual 3D world and an actual moving camera.

### 2.1 The scroll → camera mapping (the continuity spine)
```
Lenis smooth-scroll ─▶ scrollY ─▶ p = scrollY / (scrollHeight - innerHeight)   // 0..1
p ─▶ camera.position = curve.getPointAt(p)          // CatmullRom spline (descent/reveal)
p ─▶ camera.lookAt( curve.getPointAt(p + lookAhead) )
```
- The **camera path** is a `THREE.CatmullRomCurve3` through the storyboard
  waypoints. For `descent` the waypoints step down in `y` (surface → floor);
  for `orbit` the "path" is a ring and `p` is the orbit angle so scroll *rotates*
  the subject (this is the PDF's "scroll rotates the watch"). `[PDF, Prompt 01]`
- Because `p` is continuous and the spline is C¹-smooth, camera motion is
  seamless across every section boundary — **that is the continuity**.

### 2.2 Seamless section-to-section morph
Each waypoint carries a **fog color**, **particle color/density**, and optional
**subject** and **light**. On every frame we find the two waypoints `p` sits
between and **lerp** their fog + particle colors by the local fraction:
```
scene.fog.color = lerpColor(wp[i].fog, wp[i+1].fog, localT)
particles.material.color = lerpColor(wp[i].pcolor, wp[i+1].pcolor, localT)
```
So the environment *color-grades continuously* as the camera descends — navy →
black in the deep-sea build — with no hard boundary. This is the code embodiment
of *"Background color-grades deep navy → pure black with depth."* `[PDF, Prompt 02]`

### 2.3 Morphing hero → section
The hero subject (e.g. the EREBUS submarine — procedural geometry: hull, conning
tower, emissive viewport ring, floodlight `SpotLight`s) descends *with* the camera
and its floodlights **ignite** when `p` crosses into the dark zones (a ScrollTrigger
range flips `light.intensity` via a tween). The subject is never removed and
re-added; it transforms in place, so hero and sections share one continuous object —
"morphing hero → section." `[PDF, Prompt 02: "the floodlights flicker on"]`

### 2.4 Pinned text reveals
Text sections are normal full-height flow blocks over the fixed canvas. **GSAP
ScrollTrigger** fades/translates each section's inner content as it enters, and
drives the **HUD** counter (`0m → 3,800m`) from `p`. `[PDF, Prompt 02]` The canvas
is `position: fixed` (effectively pinned) so it stays put while text scrolls over
it — the classic Awwwards pinned-hero pattern. `[VIDEO: "award-winning site" refs]`

### 2.5 Extra real-3D touches (per archetype)
- `descent`: god-ray cones near the surface (additive), a drifting particle field
  that becomes sparse bioluminescent sparks at depth, hydrothermal-vent glow at the
  floor.
- `orbit`: a rim-lit hero solid on a turntable; scroll spins it 360°; a faint dust
  field; specular highlight tracks the camera.

None of this is pre-baked video — it is live WebGL, so `verify` can assert the
pixels genuinely change frame-to-frame across scroll.

---

## 3. Engine B — `frameseq` (the exact PDF method, for real Higgsfield clips)

When `HIGGSFIELD_API_KEY` is present, ASSETS renders the chained Seedance clips and
`ffmpeg` decodes them to `frames/####.jpg`. `frameseq` mode then does what the PDF
says verbatim: `[PDF]`
```
onScroll: idx = round(p * (N-1)); ctx.drawImage(frames[idx], ...)   // canvas scrub
```
Chaining is preserved because ASSETS fed each clip's final frame as the next clip's
`start_image`, so the concatenated frame array scrubs as one move. Until real clips
exist, ASSETS writes **procedural placeholder frames** (rendered gradient/parallax
frames) so this mode still runs and `verify` still passes — we never ship an empty
scrubber. `[OURS]`

Both engines expose the same `progress→visual` contract, so the site template is
identical; only the layer that paints the background differs.

---

## 4. Why this is faithful, not a generic guess

| Source claim | Our mechanism |
|---|---|
| "video separated into multiple frames" `[VIDEO]` | `frameseq` canvas scrubber; `webgl` renders the move live |
| "final frame → next start frame … one unbroken move" `[PDF]` | continuous `p`→spline camera + chained `start_image` in ASSETS |
| "hero image referenced on every clip" `[PDF]` | `providers.generateClip({ referenceImage })`; one subject reused across zones in `webgl` |
| "color-grades deep navy → black with depth" `[PDF]` | per-frame fog/particle color lerp between waypoints |
| "fixed HUD depth meter 0→3,800m" `[PDF]` | ScrollTrigger-driven HUD bound to `p` |
| "Lenis smooth scroll, text reveals pinned" `[PDF]` | Lenis + GSAP ScrollTrigger in the template |
| "verify every scroll animation before done" `[BOTH]` | Playwright asserts live WebGL + pixel delta across scroll |

## 5. Data contract (storyboard → engine)
`PLAN` emits `storyboard.json`; the engine reads `window.__STORY__`:
```jsonc
{
  "archetype": "descent",
  "camera": { "path": "spline", "lookAhead": 0.04 },
  "waypoints": [
    { "id":"surface", "y":0,    "fog":"#3f7fbf", "particle":{"color":"#cfeaff","count":1400,"style":"bubbles"},
      "subject":"submarine", "light":{"flood":false}, "hud":0 },
    ...
    { "id":"floor",   "y":-190, "fog":"#01040a", "particle":{"color":"#39e0ff","count":900,"style":"spark"},
      "subject":null, "light":{"flood":true, "vents":true}, "hud":3800 }
  ],
  "hud": { "label":"DEPTH", "unit":"m", "from":0, "to":3800 },
  "accent":"#39e0ff"
}
```
The engine is a pure function of this object, which is why one brief in gives one
finished site out.
