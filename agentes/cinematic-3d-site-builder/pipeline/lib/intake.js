// pipeline/lib/intake.js — Stage 1: accept + normalize a brief (YAML/JSON/CLI)
import fs from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';
import { resolveTemplate, applyStyle, STYLE_PRESETS } from '../../prompt-pack/templates.js';
import { ROOT, slugify, ok, info, warn } from './util.js';

/** Parse a brief file (yaml or json) or synthesize one from CLI --topic/--niche. */
export function intake(opts) {
  let brief = {};
  if (opts.brief) {
    const p = path.isAbsolute(opts.brief) ? opts.brief : path.join(ROOT, opts.brief);
    if (!fs.existsSync(p)) throw new Error(`brief not found: ${p}`);
    const raw = fs.readFileSync(p, 'utf8');
    brief = p.endsWith('.json') ? JSON.parse(raw) : yaml.load(raw);
    info(`brief: ${path.relative(ROOT, p)}`);
  } else if (opts.topic) {
    brief = { brand: titleize(opts.topic), niche: opts.niche, subtitle: opts.topic };
    info(`brief synthesized from --topic "${opts.topic}"`);
  } else {
    throw new Error('provide --brief <file> or --topic "<idea>" [--niche <n>]');
  }

  if (opts.niche) brief.niche = opts.niche; // CLI override wins
  if (!brief.brand && opts.topic) brief.brand = titleize(opts.topic);
  if (!brief.brand) throw new Error('brief needs a `brand` (or pass --topic)');

  const template = resolveTemplate(brief.niche);
  const merged = normalize(brief, template);
  ok(`intake: "${merged.brand}" · niche=${merged.niche} · template=${template.id} (${template.archetype})`);
  return { brief: merged, template };
}

function titleize(s) {
  return String(s).replace(/^(a|an|the)\s+/i, '').replace(/\b\w/g, (m) => m.toUpperCase()).slice(0, 40).trim();
}

/** Fill defaults from the niche template so downstream stages are pure. */
function normalize(brief, t) {
  const vibe = brief.vibe || {};
  const palette = {
    accent: vibe.accent || t.palette.accent,
    background: vibe.background || t.palette.bg,
    text: vibe.text || t.palette.text,
  };
  const sections = (brief.sections && brief.sections.length)
    ? brief.sections
    : t.sections.map((id, i) => ({ id: `${id}-${i}`, kicker: t.exampleBrand, title: t.tagline, body: '' }));

  // Visual style preset (see prompt-pack STYLE_PRESETS). Unknown keys warn + disable.
  let style = brief.style ?? t.style ?? 'cinematic-macro-noir';
  if (style !== 'none' && !STYLE_PRESETS[style]) {
    warn(`unknown style "${style}" — prompts will carry no style suffix`);
    style = 'none';
  }

  if (!brief.sections?.length) warn('brief has no sections — using template defaults');

  return {
    brand: brief.brand,
    niche: brief.niche || t.niche,
    tagline: brief.tagline || t.tagline,
    subtitle: brief.subtitle || '',
    subject: brief.subject || t.subject,
    slug: slugify(brief.slug || brief.brand),
    palette,
    hud: brief.hud === null ? null : (brief.hud || t.hud || null),
    sections,
    specs: brief.specs || [],
    cta: brief.cta || { headline: t.tagline, button: 'Get in touch' },
    // Localization: page language + the few fixed UI strings the build emits.
    lang: brief.lang || 'en',
    ui: { scroll: 'scroll ↓', specification: 'Specification', ...(brief.ui || {}) },
    generation: {
      provider: 'higgsfield', model: 'seedance-2.0', mode: 'std',
      resolution: '1080p', aspect: '16:9', durationSec: 8, chained: !!t.chained,
      ...(brief.generation || {}),
    },
    _templateId: t.id,
    _archetype: t.archetype,
    _copyTone: t.copyTone,
    // Shot prompts: brief-level overrides win over the niche template, then the
    // style preset (visual DNA: light/sharpness/atmosphere) is appended to all.
    _heroImagePrompt: applyStyle(brief.heroImage || t.heroImage, style, palette.accent),
    _visuals: (brief.visuals?.length ? brief.visuals : t.visuals).map((v) => ({
      ...v, prompt: applyStyle(v.prompt, style, palette.accent),
    })),
    _style: style,
  };
}
