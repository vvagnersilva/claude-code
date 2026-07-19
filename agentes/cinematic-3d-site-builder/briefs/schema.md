# Brief schema

A brief is YAML or JSON. Only `brand` (or `--topic`) is strictly required — every
other field falls back to the niche template in `prompt-pack/templates.js`.

| Field | Type | Default | Notes |
|---|---|---|---|
| `brand` | string | from `--topic` | Site name shown in the hero. |
| `niche` | string | `journey` | One of the 10 templates or an alias (`watch`, `gym`, `penthouse`, …). Picks the world archetype. |
| `tagline` | string | template tagline | Hero subline. |
| `subtitle` | string | "" | Small hero descriptor. |
| `subject` | enum | template subject | `submarine \| hypercar \| tower \| faceted-solid \| figure`. The procedural 3D hero (placeholder for the Seedance clip). |
| `vibe.accent` | hex | template accent | Single accent color. |
| `vibe.background` | hex | template bg | Base background / deepest fog. |
| `vibe.text` | hex | template text | Body text color. |
| `hud` | object\|null | template hud | `{label, unit, from, to}`. A fixed scroll-counter (depth/speed/floor). `null` = no HUD. |
| `sections[]` | array | template sections | Each: `{id, zone?, depth?, fog?, kicker, title, body, carry?}`. Order = scroll order. |
| `sections[].fog` | hex | interpolated | Zone color at that waypoint; the engine lerps between them. |
| `sections[].carry` | string | — | Documents the continuity handoff, e.g. `final-frame→start-frame`. |
| `specs[]` | `[label,value][]` | [] | Spec callouts strip. |
| `cta` | object | template | `{headline, button}`. |
| `generation` | object | template | `{provider, model, mode, resolution, chained, frameMaxWidth?}`. Consumed by ASSETS; stubbed without `HIGGSFIELD_API_KEY`/`FAL_KEY`. Quality bar (mandatory): `resolution: 1080p`, decode keeps native width up to `frameMaxWidth` (default 1920, lanczos + `-q:v 2`); VERIFY fails real frames <1280px. |
| `style` | string | `cinematic-macro-noir` | Style preset appended to EVERY shot prompt (see `STYLE_PRESETS` in `prompt-pack/templates.js`). `none` disables. |
| `lang` | string | `en` | `<html lang>` of the built site (e.g. `pt-BR`). |
| `ui` | object | en strings | Fixed UI strings: `{scroll, specification}` (scroll cue + specs kicker). |
| `heroImage` | string | template heroImage | Override the hero-image prompt (subject only — the style preset is appended automatically). |
| `visuals[]` | array | template visuals | Override the clip shot list: `{id, kind, prompt, endFrame?}`. `kind: chain` + `generation.chained: true` = final-frame→start-frame continuity. `endFrame: hero` pins a clip's last frame to the hero image (perfect loop for cyclic stories). |

## CLI equivalent
```bash
npm run build -- --topic "a wood-fire steakhouse in Lisbon" --niche restaurant
npm run build -- --brief briefs/example.brief.yaml
npm run build -- --brief briefs/watch.brief.json --engine frameseq
```
Flags: `--engine webgl|frameseq` (default `webgl`), `--out <dir>`, `--no-verify`,
`--open` (print a serve command).
