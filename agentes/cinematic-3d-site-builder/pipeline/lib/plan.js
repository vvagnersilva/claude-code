// pipeline/lib/plan.js — Stage 2: brief → storyboard + continuity map.
// This is where the source logic (PDF How-to #2/#3, video "frames") becomes data.
import { mixHex, ok, info } from './util.js';

const ARCHETYPE_CAMERA = {
  descent: { path: 'spline', axis: 'y', dir: -1, lookAhead: 0.05, span: 210 },
  reveal:  { path: 'spline', axis: 'z', dir: -1, lookAhead: 0.04, span: 150 },
  orbit:   { path: 'orbit',  axis: 'angle', dir: 1, lookAhead: 0.02, radius: 46 },
  assemble:{ path: 'dolly',  axis: 'z', dir: -1, lookAhead: 0.03, span: 120 },
};

export function plan({ brief, template }) {
  const arche = brief._archetype;
  const cam = ARCHETYPE_CAMERA[arche] || ARCHETYPE_CAMERA.descent;
  const sections = brief.sections;
  const n = sections.length;

  // ── waypoints: one per section, placed along the camera path ────────────────
  const waypoints = sections.map((s, i) => {
    const p = n > 1 ? i / (n - 1) : 0;
    // fog: explicit per-section, else grade from a lighter top toward the bg
    const topFog = mixHex(brief.palette.background, '#9fc4e6', 0.5);
    const fog = s.fog || mixHex(topFog, brief.palette.background, p);
    // particles get sparser + shift toward the accent with depth/progress
    const particleColor = mixHex(mixHex('#ffffff', brief.palette.text, 0.4), brief.palette.accent, p);
    const style = arche === 'descent'
      ? (p < 0.33 ? 'bubbles' : p < 0.7 ? 'drift' : 'spark')
      : arche === 'assemble' ? 'assemble' : 'dust';
    const count = Math.round(1500 - 700 * p); // thins out with depth

    // position along the path
    let pos;
    if (cam.path === 'orbit') {
      const a = p * Math.PI * 2;
      pos = [Math.cos(a) * cam.radius, 0, Math.sin(a) * cam.radius];
    } else if (cam.axis === 'y') {
      pos = [Math.sin(p * Math.PI * 1.5) * 6, -p * cam.span, 0];
    } else {
      pos = [Math.sin(p * Math.PI) * 8, Math.sin(p * Math.PI * 2) * 3, -p * cam.span];
    }

    const hudValue = (s.depth ?? s.hudValue);
    return {
      id: s.id || `wp${i}`,
      index: i, p, pos, fog,
      particle: { color: particleColor, count, style },
      subject: i === 0 ? brief.subject : null,      // hero subject seeds at wp0
      light: { flood: arche === 'descent' && p >= 0.45, vents: arche === 'descent' && p >= 0.85, rim: arche === 'orbit' },
      hud: hudValue,
    };
  });

  // ── HUD counter values per section ──────────────────────────────────────────
  const hud = brief.hud ? { ...brief.hud } : null;
  const sectionData = sections.map((s, i) => {
    const p = n > 1 ? i / (n - 1) : 0;
    // Same precedence as the waypoints above: depth, then explicit hudValue,
    // then a linear fill from the global HUD range.
    const hudValue = s.depth ?? s.hudValue ?? (hud ? Math.round(hud.from + (hud.to - hud.from) * p) : null);
    return {
      id: s.id || `sec${i}`,
      zone: s.zone || '',
      kicker: s.kicker || '',
      title: s.title || brief.tagline,
      body: s.body || '',
      carry: s.carry || null,
      hudValue,
      start: p,                              // scroll fraction where this section centers
    };
  });

  // ── continuity map: what carries from each section to the next ──────────────
  const chained = brief.generation.chained;
  const continuityMap = [];
  for (let i = 0; i < n - 1; i++) {
    continuityMap.push({
      from: sectionData[i].id,
      to: sectionData[i + 1].id,
      carry: chained ? 'final-frame → start-frame' : 'shared camera path + color-grade cross-fade',
      camera: `spline segment ${i}→${i + 1}`,
      transition: chained
        ? 'seam is a single shared frame (invisible)'                 // [PDF How-to #3]
        : 'continuous camera + fog lerp (no cut)',                    // [OURS/webgl]
      fogFrom: waypoints[i].fog, fogTo: waypoints[i + 1].fog,
    });
  }

  // ── shot list for the ASSETS stage (hero image + clips, referenced/chained) ──
  const shots = [];
  const heroPrompt = brief._heroImagePrompt;
  shots.push({ id: 'hero-image', kind: 'image', prompt: heroPrompt, referenceHero: false });
  (brief._visuals || []).forEach((v, i) => {
    shots.push({
      id: v.id,
      kind: 'clip',
      prompt: v.prompt,
      referenceHero: true,                                            // [PDF How-to #2]
      startFrame: chained && i > 0 ? `${brief._visuals[i - 1].id}:final` : null, // [PDF How-to #3]
      // endFrame: 'hero' pins the clip's LAST frame to the hero image — closes
      // a perfect loop on cyclic narratives (…and it becomes the car again).
      endFrame: v.endFrame || null,
    });
  });

  const storyboard = {
    brand: brief.brand,
    slug: brief.slug,
    tagline: brief.tagline,
    subtitle: brief.subtitle,
    archetype: arche,
    templateId: brief._templateId,
    accent: brief.palette.accent,
    bg: brief.palette.background,
    text: brief.palette.text,
    camera: { path: cam.path, axis: cam.axis, lookAhead: cam.lookAhead, span: cam.span || 0, radius: cam.radius || 0 },
    waypoints,
    hud,
    sections: sectionData,
    continuityMap,
    specs: brief.specs,
    cta: brief.cta,
    lang: brief.lang,
    ui: brief.ui,
    shots,
    generation: brief.generation,
  };

  ok(`plan: archetype=${arche} · ${n} waypoints · ${continuityMap.length} continuity handoffs · ${shots.length} shots`);
  info(`continuity: ${chained ? 'CHAINED (final→start frame)' : 'camera-path color-grade'} · camera=${cam.path}`);
  return storyboard;
}
