// pipeline/lib/assets.js — Stage 3: generate hero image + clips.
// REAL via Higgsfield when HIGGSFIELD_API_KEY is set; otherwise clean procedural
// placeholders (never fake-green). Placeholders are usable: an SVG hero poster and
// an SVG frame sequence so the `frameseq` engine still scrubs a real continuity.
import path from 'node:path';
import fs from 'node:fs';
import { spawnSync } from 'node:child_process';
import { HAS_CREDENTIALS, PROVIDER, announceMode, generateHeroImage, generateClip, falBalance } from './providers.js';
import { writeFile, writeJSON, ensureDir, mixHex, escapeHtml, ok, info, warn } from './util.js';

const FRAME_COUNT = 48; // placeholder frame-sequence length (kept light)

export async function assets(storyboard, outDir) {
  announceMode();
  // Pre-flight: paid fal runs fail fast on a drained/locked account instead of
  // 15-minute zombie queue timeouts (seen live 2026-07-08, balance -$30.81).
  const balStart = await falBalance();
  if (balStart != null) {
    if (balStart <= 0) {
      throw new Error(`fal.ai account has no balance ($${balStart.toFixed(2)}) — top up at fal.ai/dashboard/billing, or run with ASSETS_MODE=stub`);
    }
    info(`fal balance: $${balStart.toFixed(2)}`);
  }
  const assetDir = ensureDir(path.join(outDir, 'assets'));
  // Resume support: a failed/partial PAID run leaves an incremental manifest
  // behind — reuse any real shot whose prompt is unchanged instead of paying
  // to regenerate it. (Stub mode ignores this: placeholders are free.)
  const manifestPath = path.join(assetDir, 'manifest.json');
  const prev = (HAS_CREDENTIALS && fs.existsSync(manifestPath))
    ? JSON.parse(fs.readFileSync(manifestPath, 'utf8')) : null;
  const manifest = {
    brand: storyboard.brand, slug: storyboard.slug,
    provider: storyboard.generation.provider, model: storyboard.generation.model,
    activeProvider: PROVIDER,
    stubbed: !HAS_CREDENTIALS, generatedRealAssets: HAS_CREDENTIALS,
    heroImage: null, clips: [], frames: null, missing: [],
  };

  // ── ONE hero image first (PDF How-to #2) ────────────────────────────────────
  const heroShot = storyboard.shots.find((s) => s.kind === 'image');
  const prevHero = (prev?.heroImage && !prev.heroImage.stubbed && prev.heroImage.url
    && prev.heroImage.prompt === heroShot.prompt) ? prev.heroImage : null;
  if (prevHero) info('hero image → REUSED from previous run (same prompt, no re-spend)');
  const hero = prevHero
    ? { stubbed: false, url: prevHero.url, prompt: heroShot.prompt }
    : await generateHeroImage({ prompt: heroShot.prompt, gen: storyboard.generation, out: path.join(assetDir, 'hero') });
  const heroSvgPath = path.join(assetDir, 'hero.svg');
  writeFile(heroSvgPath, heroPosterSVG(storyboard));
  // Real hero: download locally so the site stays self-contained/offline.
  let heroOut = 'assets/hero.svg';
  if (!hero.stubbed && hero.url) {
    const ext = path.extname(new URL(hero.url).pathname) || '.jpg';
    if (await download(hero.url, path.join(assetDir, `hero${ext}`))) heroOut = `assets/hero${ext}`;
  }
  manifest.heroImage = { prompt: heroShot.prompt, stubbed: hero.stubbed, output: heroOut, ...(hero.url ? { url: hero.url } : {}) };
  if (hero.stubbed) info('hero image → procedural SVG poster (assets/hero.svg)');
  else ok(`hero image → real render → ${heroOut}`);
  writeJSON(manifestPath, manifest); // incremental: survive a mid-run failure

  // ── clips: each references the hero; chained ones take prior final frame ─────
  const clipShots = storyboard.shots.filter((s) => s.kind === 'clip');
  let prevFinal = null;
  // Chained continuity guard: once ANY clip is regenerated, later chained clips
  // must also regenerate (their start frame changed). Reused clips also require
  // the hero to be reused — it is the visual reference of every clip.
  let chainBroken = !prevHero && !hero.stubbed;
  for (const shot of clipShots) {
    const prevClip = (!chainBroken && prev?.clips?.find((c) =>
      c.id === shot.id && !c.stubbed && c.url && c.prompt === shot.prompt
      && (c.endFrame || null) === (shot.endFrame || null)
      // Quality bar: never silently reuse clips generated at another resolution
      // (legacy manifests without the field still reuse).
      && (!c.resolution || c.resolution === storyboard.generation.resolution))) || null;
    if (prevClip) info(`clip ${shot.id} → REUSED from previous run (no re-spend)`);
    else if (prev) chainBroken = true;
    const res = prevClip
      ? { stubbed: false, url: prevClip.url, prompt: shot.prompt }
      : await generateClip({
          prompt: shot.prompt,
          referenceImage: hero.url || heroSvgPath,
          startImage: shot.startFrame ? prevFinal : null,
          endImage: shot.endFrame === 'hero' ? (hero.url || null) : null,
          gen: storyboard.generation,
          out: path.join(assetDir, shot.id),
        });
    const entry = {
      id: shot.id, prompt: shot.prompt, referenceHero: shot.referenceHero,
      startFrame: shot.startFrame || null, endFrame: shot.endFrame || null,
      resolution: storyboard.generation.resolution,
      stubbed: res.stubbed,
      note: res.note || null, ...(res.url ? { url: res.url } : {}),
    };
    if (!res.stubbed && res.url) {
      // Real path: download the mp4 + decode to frames with ffmpeg (best-effort).
      const dec = await decodeClip(res.url, assetDir, shot.id, storyboard.generation);
      if (dec) { prevFinal = dec.final || prevFinal; entry.file = dec.file; }
    }
    manifest.clips.push(entry);
    writeJSON(manifestPath, manifest); // incremental: survive a mid-run failure
    info(`clip ${shot.id} → ${res.stubbed ? 'stub' : 'real'}${shot.startFrame ? ' (chained: uses prior final frame)' : ''}`);
  }

  // ── frame sequence for `frameseq` mode ──────────────────────────────────────
  // Real assets: ffmpeg already wrote frames above. Stub: synthesize an SVG
  // sequence that color-grades across the waypoints so frameseq scrubs continuity.
  if (manifest.stubbed) {
    const framesDir = ensureDir(path.join(assetDir, 'frames'));
    for (let i = 0; i < FRAME_COUNT; i++) {
      const t = i / (FRAME_COUNT - 1);
      writeFile(path.join(framesDir, `frame-${String(i).padStart(3, '0')}.svg`), journeyFrameSVG(storyboard, t));
    }
    manifest.frames = { count: FRAME_COUNT, dir: 'assets/frames', format: 'svg', pattern: 'frame-%03d.svg', stubbed: true };
    info(`frame sequence → ${FRAME_COUNT} procedural SVG frames (assets/frames/) for frameseq mode`);
  } else {
    // Real path: per-clip decoded frames (<id>-%04d.jpg) become ONE continuous
    // 0-based frame-%04d.jpg sequence — the exact contract frameseq.js scrubs.
    const count = renumberFrames(path.join(assetDir, 'frames'), clipShots.map((s) => s.id));
    if (count) {
      const width = probeFrameWidth(path.join(assetDir, 'frames', 'frame-0000.jpg'));
      manifest.frames = { count, dir: 'assets/frames', format: 'jpg', pattern: 'frame-%04d.jpg', stubbed: false, ...(width ? { width } : {}) };
      info(`frame sequence → ${count} real decoded frames${width ? ` @ ${width}px` : ''} (assets/frames/) for frameseq mode`);
    } else {
      manifest.frames = null;
      warn('no frames decoded (ffmpeg missing or downloads failed) — frameseq engine has nothing to scrub');
    }
  }

  // ── document exactly what to plug in for real generation ─────────────────────
  if (manifest.stubbed) {
    manifest.missing = [
      { what: 'Higgsfield API key', env: 'HIGGSFIELD_API_KEY', why: 'authenticate Seedance 2.0 / Nano-Banana calls' },
      { what: 'Higgsfield base URL (optional)', env: 'HIGGSFIELD_BASE_URL', default: 'https://api.higgsfield.ai/v1' },
      { what: 'fal.ai key (fallback provider)', env: 'FAL_KEY', why: 'same Seedance 2.0 / Nano-Banana models via fal.ai when Higgsfield is absent' },
      { what: 'Higgsfield credits', note: 'Seedance 2.0 std/1080p/~8s clips are credit-metered (see the video)' },
      { what: 'ffmpeg', check: 'installed', note: 'used to decode real clips → frame sequence for frameseq mode' },
    ];
    warn('ASSETS stubbed — site still renders (webgl is procedural). To generate real clips, set HIGGSFIELD_API_KEY or FAL_KEY.');
  }

  writeJSON(manifestPath, manifest);
  ok(`assets: ${manifest.clips.length} clips + hero + ${manifest.frames?.count || 'ffmpeg'} frames · manifest.json written`);
  // Cost transparency: report what this run actually consumed.
  if (balStart != null) {
    const balEnd = await falBalance();
    if (balEnd != null) info(`fal spend this run: $${(balStart - balEnd).toFixed(2)} · balance left $${balEnd.toFixed(2)}`);
  }
  return manifest;
}

/** Fetch a remote asset to disk (self-contained output). Returns dest or null. */
async function download(url, dest) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    writeFile(dest, Buffer.from(await res.arrayBuffer()));
    return dest;
  } catch (e) { warn(`download failed (${url}): ${e.message}`); return null; }
}

// Best-effort real-clip decode (only runs when a real URL exists + ffmpeg present).
// Keeps the mp4 in assets/clips/ (deliverable) and decodes frames to assets/frames/.
async function decodeClip(url, assetDir, id, gen) {
  try {
    const mp4 = await download(url, path.join(assetDir, 'clips', `${id}.mp4`));
    if (!mp4) return null;
    const framesDir = ensureDir(path.join(assetDir, 'frames'));
    // [PDF Pro-tip #3] -vf fps controls frame density. Frames keep the clip's
    // native width up to frameMaxWidth (Retina canvases upscale 1280px frames
    // ~2.2× and look pixelated) with lanczos + high JPEG quality (-q:v 2).
    const maxW = gen?.frameMaxWidth || 1920;
    const ff = spawnSync('ffmpeg', ['-y', '-i', mp4, '-vf', `fps=6,scale='min(${maxW},iw)':-2:flags=lanczos`, '-q:v', '2', path.join(framesDir, `${id}-%04d.jpg`)], { stdio: 'ignore' });
    if (ff.error) warn(`ffmpeg unavailable for ${id}: ${ff.error.message}`);
    // The clip's LAST decoded frame feeds the next chained clip as its start image.
    const frames = fs.readdirSync(framesDir).filter((f) => f.startsWith(`${id}-`) && f.endsWith('.jpg')).sort();
    return {
      file: `assets/clips/${id}.mp4`,
      final: frames.length ? path.join(framesDir, frames[frames.length - 1]) : null,
    };
  } catch (e) { warn(`clip decode failed for ${id}: ${e.message}`); return null; }
}

/** Frame width via ffprobe — recorded in the manifest so VERIFY can enforce
 *  the mandatory quality bar (≥1280px). Returns null if ffprobe is missing. */
function probeFrameWidth(framePath) {
  try {
    const r = spawnSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width', '-of', 'csv=p=0', framePath], { encoding: 'utf8' });
    const w = parseInt(String(r.stdout).trim(), 10);
    return Number.isFinite(w) ? w : null;
  } catch { return null; }
}

/** Merge per-clip frame files into one continuous 0-based frame-%04d.jpg run. */
function renumberFrames(framesDir, clipIds) {
  if (!fs.existsSync(framesDir)) return 0;
  let n = 0;
  for (const id of clipIds) {
    const frames = fs.readdirSync(framesDir).filter((f) => f.startsWith(`${id}-`) && f.endsWith('.jpg')).sort();
    for (const f of frames) {
      fs.renameSync(path.join(framesDir, f), path.join(framesDir, `frame-${String(n).padStart(4, '0')}.jpg`));
      n++;
    }
  }
  return n;
}

// ── procedural placeholder generators (SVG, self-contained) ───────────────────
function heroPosterSVG(sb) {
  const top = mixHex(sb.bg, '#a9cdee', 0.45);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <defs>
    <radialGradient id="g" cx="50%" cy="30%" r="90%">
      <stop offset="0%" stop-color="${top}"/><stop offset="60%" stop-color="${sb.bg}"/><stop offset="100%" stop-color="#000"/>
    </radialGradient>
    <linearGradient id="a" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${sb.accent}"/><stop offset="100%" stop-color="${sb.text}"/>
    </linearGradient>
  </defs>
  <rect width="1600" height="900" fill="url(#g)"/>
  ${subjectSilhouette(sb.waypoints?.[0]?.subject || 'faceted-solid', sb.accent)}
  <text x="80" y="760" font-family="Georgia,serif" font-size="120" fill="url(#a)" letter-spacing="6">${escapeHtml(sb.brand)}</text>
  <text x="86" y="820" font-family="Helvetica,Arial,sans-serif" font-size="30" fill="${sb.text}" opacity="0.7">${escapeHtml(sb.tagline)}</text>
</svg>`;
}

function subjectSilhouette(subject, accent) {
  const x = 800, y = 380;
  switch (subject) {
    case 'submarine':
      return `<g transform="translate(${x},${y})" opacity="0.92">
        <ellipse cx="0" cy="0" rx="260" ry="70" fill="#0c1622" stroke="${accent}" stroke-width="2"/>
        <rect x="-40" y="-120" width="90" height="70" rx="18" fill="#0c1622" stroke="${accent}" stroke-width="2"/>
        <circle cx="150" cy="0" r="26" fill="none" stroke="${accent}" stroke-width="5"/>
        <circle cx="150" cy="0" r="10" fill="${accent}"/>
        <polygon points="240,-50 340,-16 340,16 240,50" fill="${accent}" opacity="0.25"/>
      </g>`;
    case 'hypercar':
      return `<g transform="translate(${x},${y})" opacity="0.92">
        <polygon points="-300,40 -180,-40 180,-40 300,40 -300,40" fill="#0a0a0a" stroke="${accent}" stroke-width="2"/>
        <rect x="-260" y="38" width="520" height="8" fill="${accent}"/>
        <circle cx="-160" cy="55" r="36" fill="#111" stroke="${accent}" stroke-width="3"/>
        <circle cx="160" cy="55" r="36" fill="#111" stroke="${accent}" stroke-width="3"/></g>`;
    case 'tower':
      return `<g transform="translate(${x},${y})" opacity="0.9">
        <rect x="-70" y="-260" width="140" height="520" fill="#0b0b12" stroke="${accent}" stroke-width="2"/>
        ${Array.from({ length: 10 }).map((_, i) => `<line x1="-70" y1="${-240 + i * 50}" x2="70" y2="${-240 + i * 50}" stroke="${accent}" stroke-width="1" opacity="0.35"/>`).join('')}</g>`;
    case 'figure':
      return `<g transform="translate(${x},${y})" opacity="0.9">
        <circle cx="0" cy="-150" r="60" fill="#0c0c0e" stroke="${accent}" stroke-width="2"/>
        <path d="M -110 200 Q 0 -80 110 200 Z" fill="#0c0c0e" stroke="${accent}" stroke-width="2"/></g>`;
    default: // faceted-solid
      return `<g transform="translate(${x},${y})" opacity="0.92">
        <polygon points="0,-180 150,-60 120,150 -120,150 -150,-60" fill="#0c0c0c" stroke="${accent}" stroke-width="3"/>
        <polygon points="0,-180 150,-60 0,20 -150,-60" fill="${accent}" opacity="0.18"/></g>`;
  }
}

// One frame of the "chained journey": fog color-grades across waypoints + a moving
// light band — proves the frameseq scrubber shows continuity across scroll.
function journeyFrameSVG(sb, t) {
  const wps = sb.waypoints;
  const n = wps.length;
  const f = t * (n - 1);
  const i = Math.min(n - 2, Math.floor(f));
  const lt = f - i;
  const fog = mixHex(wps[i]?.fog || sb.bg, wps[i + 1]?.fog || sb.bg, lt);
  const pc = mixHex(wps[i]?.particle.color || sb.accent, wps[i + 1]?.particle.color || sb.accent, lt);
  const bandY = 900 * t;
  const dots = Array.from({ length: 60 }).map((_, k) => {
    const px = (k * 137.5) % 1600;
    const py = ((k * 311 + t * 900) % 900);
    const r = 1 + ((k % 4));
    return `<circle cx="${px.toFixed(0)}" cy="${py.toFixed(0)}" r="${r}" fill="${pc}" opacity="${(0.15 + (k % 5) * 0.12).toFixed(2)}"/>`;
  }).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <defs><linearGradient id="fg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="${mixHex(fog, '#ffffff', 0.12)}"/><stop offset="100%" stop-color="${mixHex(fog, '#000000', 0.4)}"/>
  </linearGradient></defs>
  <rect width="1600" height="900" fill="url(#fg)"/>
  <rect x="0" y="${(bandY - 40).toFixed(0)}" width="1600" height="80" fill="${pc}" opacity="0.10"/>
  ${dots}
  <text x="60" y="80" font-family="monospace" font-size="26" fill="${sb.accent}" opacity="0.8">DEPTH ${(t * (sb.hud?.to || 100)).toFixed(0)}${sb.hud?.unit || ''}</text>
</svg>`;
}
