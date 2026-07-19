/**
 * prompt-pack/templates.js
 * ────────────────────────────────────────────────────────────────────────────
 * The 10 niche templates of the cinematic prompt pack,
 * encoded as structured data so the PLAN stage can operationalize them.
 *
 * Each template preserves the source's TWO halves:
 *   visuals[] — the Seedance 2.0 shot list (hero image + clips)
 *   website   — the scroll build recipe (archetype, sections, HUD, design)
 *
 * `archetype` and `chained` are the load-bearing fields:
 *   - archetype maps a niche to a camera-path world (see docs/logic.md)
 *   - chained:true means "final frame → next start frame" continuity (PDF How-to #3)
 *
 * Source tags in comments: [PDF] = prompt pack, [VIDEO] = tutorial.
 */

export const SEEDANCE_DEFAULTS = {
  model: 'seedance-2.0',            // [VIDEO] "C Dance 2.0" on the Higgsfield MCP
  mode: 'std',                      // [PDF] "All prompts default to std mode"
  resolution: '1080p',
  aspect: '16:9',
  audio: false,
  durationSec: 8,                   // [PDF] "~8 seconds"
  heroImage: { model: 'nano-banana-pro', quality: '4k' }, // [VIDEO] 4K image quality matters
};

/**
 * STYLE PRESETS — the visual DNA appended to EVERY shot prompt (hero + clips).
 * Theme-agnostic on purpose: they encode light, sharpness, atmosphere and
 * material response — never the subject. `{ACCENT}` is replaced with the
 * brief's accent color at intake. Select per-brief with `style: <key>`
 * (default `cinematic-macro-noir`; `style: none` disables).
 *
 * `cinematic-macro-noir` is reverse-engineered from the reference frames
 * (2026-07-08): ultra-macro luxury-watch shots — near-black void, warm golden
 * key light, razor-sharp micro-detail, shallow DOF, drifting gold dust motes.
 */
export const STYLE_PRESETS = {
  'cinematic-macro-noir':
    'ultra-detailed macro product cinematography, razor-sharp focus on machined micro-detail, ' +
    'shallow depth of field with creamy bokeh, subject suspended in a near-black void, ' +
    'fine dust motes drifting through the light, warm specular key light with soft falloff, ' +
    'accent glints of {ACCENT}, physically accurate materials, high dynamic range, ' +
    'subtle volumetric haze, gentle film grain, photorealistic, 8K sharpness, no text, no watermark',
  'clean-studio':
    'clean studio product photography, seamless dark backdrop, single soft key light, ' +
    'accurate materials, crisp edge highlights of {ACCENT}, photorealistic, no text, no watermark',
};

/** Compose a shot prompt with the resolved style suffix (accent substituted). */
export function applyStyle(prompt, styleKey, accent) {
  if (!styleKey || styleKey === 'none') return prompt;
  const suffix = STYLE_PRESETS[styleKey];
  if (!suffix) return prompt;
  return `${prompt} — ${suffix.replaceAll('{ACCENT}', accent)}`;
}

/** @typedef {'descent'|'orbit'|'assemble'|'reveal'} Archetype */

export const TEMPLATES = {
  // 01 · LUXURY PRODUCT — orbit; scroll rotates the product. [PDF Prompt 01]
  'luxury-product': {
    id: '01', niche: 'luxury-product', archetype: 'orbit', chained: false,
    exampleBrand: 'AURUM & NOIR', tagline: 'Crafted in Darkness',
    palette: { bg: '#0a0a0a', accent: '#c8a84b', text: '#f2ede1' }, // off-black + gold
    heroImage: 'the product in a black void, dramatic rim lighting, faint gold dust',
    visuals: [
      { id: 'hero', kind: 'orbit', prompt: 'slow perfectly smooth 360° studio turntable of the product floating in a black void, dramatic rim lighting, faint gold dust drifting' },
      { id: 'macro', kind: 'macro', prompt: 'extreme close-up glide across the surface, light rippling across brushed metal' },
      { id: 'exploded', kind: 'assembly', prompt: 'the product assembling itself from floating components converging into the finished piece' },
    ],
    sections: ['hero', 'story', 'macro-details', 'engineering', 'edition', 'waitlist-cta'],
    hud: null, subject: 'faceted-solid',
    copyTone: 'quiet, expensive, very few words',
  },

  // 02 · EXPERIENCE / JOURNEY — descent; 5 CHAINED clips. The flagship continuity build. [PDF Prompt 02]
  'journey': {
    id: '02', niche: 'journey', archetype: 'descent', chained: true,
    exampleBrand: 'ABYSSAL', tagline: 'How deep will you go?',
    palette: { bg: '#060d18', accent: '#39e0ff', text: '#dfeaf5' }, // deep navy→black, cyan
    heroImage: 'the vehicle — sleek deep-black hull, glowing cyan viewport ring, twin floodlights',
    visuals: [
      { id: 'surface',  kind: 'chain', prompt: 'aerial dawn over open ocean; the vehicle slips beneath the waves, ending fully submerged in sunlit blue' },
      { id: 'sunlit',   kind: 'chain', prompt: 'descent through god rays and bubble columns, a whale silhouette gliding past; the blue deepens' },
      { id: 'twilight', kind: 'chain', prompt: 'light dies to near-black, ghostly jellyfish drift, the floodlights flicker on' },
      { id: 'midnight', kind: 'chain', prompt: 'total darkness; bioluminescent creatures spark around the hull like a starfield' },
      { id: 'floor',    kind: 'chain', prompt: 'floodlights sweep across hydrothermal vents; the vehicle holds on a final hero frame' },
    ],
    sections: ['hero', 'zone-fact', 'zone-fact', 'zone-fact', 'specs', 'cta'],
    hud: { label: 'DEPTH', unit: 'm', from: 0, to: 3800 }, subject: 'submarine',
    copyTone: 'thin technical sans with HUD micro-details',
  },

  // 03 · PERSONAL PORTFOLIO — orbit around the person. [PDF Prompt 03]
  'portfolio': {
    id: '03', niche: 'portfolio', archetype: 'orbit', chained: false,
    exampleBrand: '[YOUR NAME]', tagline: 'what you do in one line',
    palette: { bg: '#08080a', accent: '#12c07a', text: '#efe9dd' }, // ink black, emerald, cream
    heroImage: 'the person, arms crossed, black-void studio with emerald rim lighting',
    visuals: [
      { id: 'hero',    kind: 'orbit', prompt: 'person stands confident, arms crossed, black-void studio with emerald rim lighting; camera does one slow 360° orbit' },
      { id: 'builder', kind: 'push',  prompt: 'person at a dark desk surrounded by floating holographic screens; slow cinematic push-in' },
      { id: 'closer',  kind: 'walk',  prompt: 'person walks toward camera down a dark gallery lined with glowing screens, stopping in a hero pose' },
    ],
    sections: ['hero', 'stats', 'pillars', 'work', 'finale-cta'],
    hud: null, subject: 'figure',
    copyTone: 'bold condensed display, kinetic type',
  },

  // 04 · E-COMMERCE — reveal hero walk + product spins (hover). [PDF Prompt 04]
  'ecommerce': {
    id: '04', niche: 'ecommerce', archetype: 'reveal', chained: false,
    exampleBrand: 'ONYX SUPPLY', tagline: 'MIDNIGHT DROP',
    palette: { bg: '#141414', accent: '#a6ff00', text: '#ededed' }, // concrete gray, acid green
    heroImage: 'a model wearing the full fit — matte black garments, chrome accents, foggy rooftop at night',
    visuals: [
      { id: 'hero',   kind: 'walk',  prompt: 'model walks slowly toward camera through rooftop fog, neon city glow, wind moving the fabric' },
      { id: 'spins',  kind: 'orbit', prompt: 'each garment on an invisible mannequin doing a clean 360° turntable on concrete-gray' },
      { id: 'macro',  kind: 'macro', prompt: 'extreme close-up traveling across stitching, zipper teeth, embossed logo' },
    ],
    sections: ['hero', 'product-grid', 'fabric-macro', 'notify-cta'],
    hud: { label: 'DROPS IN', unit: '', from: 0, to: 0, countdown: true }, subject: 'faceted-solid',
    copyTone: 'brutalist condensed type',
  },

  // 05 · LOCAL BUSINESS / RESTAURANT — reveal single fire hero. [PDF Prompt 05]
  'restaurant': {
    id: '05', niche: 'restaurant', archetype: 'reveal', chained: false,
    exampleBrand: 'EMBER & OAK', tagline: 'Wood fire. Nothing else.',
    palette: { bg: '#0b0806', accent: '#e8681e', text: '#efe6d6' }, // near-black, ember orange
    heroImage: 'a ribeye searing over open flame, embers rising into darkness, amber light',
    visuals: [
      { id: 'hero',  kind: 'macro', prompt: 'slow-motion macro of a ribeye searing over open flame, embers rising into darkness, cinematic amber light' },
      { id: 'room',  kind: 'dolly', prompt: 'slow dolly through a moody dining room at golden hour: leather booths, candlelight' },
      { id: 'craft', kind: 'macro', prompt: 'overhead shot of a chef’s hands plating a dish, steam curling up, dark slate table' },
    ],
    sections: ['hero', 'story', 'menu', 'private-dining', 'reserve-cta'],
    hud: null, subject: 'embers',
    copyTone: 'sparse, confident, sensory',
  },

  // 06 · REAL ESTATE — descent-style continuous tour (chained clips 2-4). [PDF Prompt 06]
  'real-estate': {
    id: '06', niche: 'real-estate', archetype: 'descent', chained: true,
    exampleBrand: 'THE MERIDIAN', tagline: 'Sixty floors above everything',
    palette: { bg: '#0a0a0c', accent: '#d9c38a', text: '#efe9df' }, // ink, champagne gold
    heroImage: 'the glass tower at dusk, city lights igniting below',
    visuals: [
      { id: 'approach', kind: 'chain', prompt: 'aerial drone curving around the glass tower at dusk, city lights igniting below' },
      { id: 'arrival',  kind: 'chain', prompt: 'camera glides from private elevator into a vast living room, floor-to-ceiling windows, marble, fireplace' },
      { id: 'flow',     kind: 'chain', prompt: 'continuous move through chef’s kitchen and primary suite toward glowing terrace doors' },
      { id: 'terrace',  kind: 'chain', prompt: 'out onto the wraparound terrace at night: infinity pool reflecting the skyline, timelapse clouds' },
    ],
    sections: ['hero', 'facts', 'gallery', 'amenities', 'price', 'showing-cta'],
    hud: { label: 'FLOOR', unit: '', from: 60, to: 60, spaces: true }, subject: 'tower',
    copyTone: 'thin elegant serif, generous whitespace',
  },

  // 07 · AUTOMOTIVE — drive; chained clips; speed HUD. [PDF Prompt 07]
  'automotive': {
    id: '07', niche: 'automotive', archetype: 'descent', chained: true, // horizontal spline via plan
    exampleBrand: 'VANTA', tagline: '1,200 horsepower, electric',
    palette: { bg: '#050505', accent: '#00d4ff', text: '#eaeaea' }, // black on black, electric cyan
    heroImage: 'the car — low, wide, matte obsidian body, thin light-bar face',
    visuals: [
      { id: 'reveal', kind: 'chain', prompt: 'dust settles in a white-sand desert at dawn to reveal the car motionless; light-bar ignites' },
      { id: 'run',    kind: 'chain', prompt: 'low tracking shot as it launches across the desert flats, sand ribboning off the wheels' },
      { id: 'canyon', kind: 'chain', prompt: 'it threads a red-rock canyon at speed, camera whipping around a corner' },
      { id: 'night',  kind: 'chain', prompt: 'full dark; only its light signature and taillight trails carving through dunes under stars' },
    ],
    sections: ['hero', 'performance', 'design', 'night-mode', 'configurator', 'reserve-cta'],
    hud: { label: 'SPEED', unit: 'mph', from: 0, to: 250 }, subject: 'hypercar',
    copyTone: 'ultrawide condensed type, subtle motion blur',
  },

  // 08 · SAAS / APP — assemble; particles build a dashboard. [PDF Prompt 08]
  'saas': {
    id: '08', niche: 'saas', archetype: 'assemble', chained: false,
    exampleBrand: 'PULSE', tagline: 'See churn coming.',
    palette: { bg: '#0b0b12', accent: '#8b5cf6', text: '#ecebf5' }, // near-black→white, violet
    heroImage: 'thousands of glowing data particles assembling into a floating dashboard UI',
    visuals: [
      { id: 'hero',   kind: 'assemble', prompt: 'a dark void where thousands of glowing data particles swirl and assemble into a clean floating dashboard UI, graph pulsing like a heartbeat' },
      { id: 'signal', kind: 'macro',    prompt: 'macro glide across holographic charts and streaming numbers, one red anomaly lighting up' },
      { id: 'calm',   kind: 'push',     prompt: 'the dashboard on a laptop in a bright minimal office, coffee steam drifting' },
    ],
    sections: ['hero', 'logos', 'features', 'metrics', 'screenshot', 'pricing', 'faq', 'cta'],
    hud: null, subject: 'particle-dashboard',
    copyTone: 'crisp geometric sans, glassmorphism cards',
  },

  // 09 · AGENCY / STUDIO — reveal ink bloom; kinetic manifesto. [PDF Prompt 09]
  'agency': {
    id: '09', niche: 'agency', archetype: 'reveal', chained: false,
    exampleBrand: 'NOIR&CO', tagline: 'For companies that refuse to be ignored.',
    palette: { bg: '#000000', accent: '#c8a84b', text: '#f4f0e6' }, // pure black + bone, gold x3
    heroImage: 'black ink blooming and morphing through water in extreme slow motion, flashing into gold',
    visuals: [
      { id: 'hero',   kind: 'morph', prompt: 'black ink blooming and morphing through water in extreme slow motion, occasionally flashing into gold' },
      { id: 'work',   kind: 'dolly', prompt: 'oversized posters and screens with bold typography sliding past on gallery walls, camera dollying sideways' },
      { id: 'people', kind: 'push',  prompt: 'silhouettes of a small team working late in a moody studio, city bokeh through the window' },
    ],
    sections: ['hero', 'manifesto', 'work-grid', 'services', 'team', 'contact-cta'],
    hud: null, subject: 'ink-bloom',
    copyTone: 'brutalist display + refined serif, gold used exactly three times',
  },

  // 10 · FITNESS / GYM — reveal chalk cloud. [PDF Prompt 10]
  'fitness': {
    id: '10', niche: 'fitness', archetype: 'reveal', chained: false,
    exampleBrand: 'FORGE', tagline: 'Earn it.',
    palette: { bg: '#111113', accent: '#c81e2b', text: '#eee9e2' }, // charcoal, bone, blood red
    heroImage: 'an athlete claps chalked hands in a dark gym, chalk cloud blooming through a shaft of light',
    visuals: [
      { id: 'hero',  kind: 'macro', prompt: 'slow motion: an athlete claps chalked hands in a dark gym, chalk cloud blooming through a single overhead shaft of light' },
      { id: 'iron',  kind: 'macro', prompt: 'macro tracking along a loaded barbell as hands grip it, knurling and chalk in sharp detail' },
      { id: 'grind', kind: 'walk',  prompt: 'a runner sprinting on an outdoor track at dawn, breath visible, camera tracking low and fast' },
    ],
    sections: ['hero', 'philosophy', 'programs', 'coaches', 'results', 'pricing', 'signup-cta'],
    hud: null, subject: 'chalk-cloud',
    copyTone: 'heavy condensed display, grain and vignette',
  },
};

/** Aliases so a brief can say niche:"watch" and hit the right template. */
export const NICHE_ALIASES = {
  watch: 'luxury-product', jewelry: 'luxury-product', product: 'luxury-product', audio: 'luxury-product',
  experience: 'journey', tourism: 'journey', expedition: 'journey', 'deep-sea': 'journey', submarine: 'journey',
  personal: 'portfolio', creator: 'portfolio', freelancer: 'portfolio',
  store: 'ecommerce', fashion: 'ecommerce', streetwear: 'ecommerce', merch: 'ecommerce',
  cafe: 'restaurant', bar: 'restaurant', steakhouse: 'restaurant', food: 'restaurant',
  realtor: 'real-estate', property: 'real-estate', penthouse: 'real-estate', hotel: 'real-estate',
  car: 'automotive', vehicle: 'automotive', hypercar: 'automotive', ev: 'automotive', drone: 'automotive',
  app: 'saas', software: 'saas', startup: 'saas', 'ai-tool': 'saas',
  studio: 'agency', 'design-studio': 'agency', consultancy: 'agency',
  gym: 'fitness', coach: 'fitness', 'martial-arts': 'fitness', sports: 'fitness',
};

export function resolveTemplate(niche) {
  if (!niche) return TEMPLATES['journey'];
  const key = String(niche).toLowerCase().trim();
  if (TEMPLATES[key]) return TEMPLATES[key];
  if (NICHE_ALIASES[key]) return TEMPLATES[NICHE_ALIASES[key]];
  return TEMPLATES['journey']; // default to the flagship continuity build
}
