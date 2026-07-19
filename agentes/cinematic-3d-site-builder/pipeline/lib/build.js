// pipeline/lib/build.js — Stage 4: assemble a self-contained static site.
import fs from 'node:fs';
import path from 'node:path';
import { ROOT, __dirname, ensureDir, writeFile, writeJSON, copyFile, escapeHtml, ok, info } from './util.js';

const TPL = path.join(__dirname, 'templates');
const VENDOR = path.join(ROOT, 'vendor');
const VENDOR_FILES = ['three.min.js', 'gsap.min.js', 'ScrollTrigger.min.js', 'lenis.min.js'];

export function build(storyboard, manifest, outDir, opts = {}) {
  const engine = opts.engine === 'frameseq' ? 'frameseq' : 'webgl';
  ensureDir(outDir);

  // 1) vendor libs → self-contained, no CDN at view time
  const vOut = ensureDir(path.join(outDir, 'vendor'));
  for (const f of VENDOR_FILES) {
    const src = path.join(VENDOR, f);
    if (!fs.existsSync(src)) throw new Error(`missing vendored lib: ${f} — run the vendor download`);
    copyFile(src, path.join(vOut, f));
  }

  // 2) engine + css
  copyFile(path.join(TPL, engine === 'frameseq' ? 'frameseq.js' : 'engine.js'), path.join(outDir, 'engine.js'));
  copyFile(path.join(TPL, 'site.css'), path.join(outDir, 'site.css'));

  // 3) storyboard for the browser + a copy for reference
  const story = {
    ...storyboard, engine,
    frames: manifest?.frames || null,
    heroImage: manifest?.heroImage?.output || 'assets/hero.svg',
  };
  writeJSON(path.join(outDir, 'storyboard.json'), story);

  // 4) index.html
  writeFile(path.join(outDir, 'index.html'), renderHTML(story));

  ok(`build: site assembled (engine=${engine}) → ${path.relative(ROOT, outDir)}/index.html`);
  return { indexPath: path.join(outDir, 'index.html'), engine };
}

function renderHTML(s) {
  const fontSerif = s.archetype === 'saas'
    ? '"Helvetica Neue", Inter, Arial, sans-serif'
    : '"Times New Roman", Georgia, serif';
  const chapters = renderChapters(s);
  const hud = s.hud ? `
  <aside class="hud" aria-hidden="true">
    <span class="label">${escapeHtml(s.hud.label || '')}</span>
    <div class="rail"><div id="hud-bar"></div></div>
    <span id="hud-value">${escapeHtml(String(s.hud.from))}${s.hud.unit ? ' ' + escapeHtml(s.hud.unit) : ''}</span>
  </aside>` : '';

  const scripts = [
    'vendor/three.min.js', 'vendor/gsap.min.js', 'vendor/ScrollTrigger.min.js', 'vendor/lenis.min.js',
  ].map((src) => `<script src="${src}"></script>`).join('\n  ');

  return `<!doctype html>
<html lang="${s.lang || 'en'}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>${escapeHtml(s.brand)} — ${escapeHtml(s.tagline)}</title>
<meta name="description" content="${escapeHtml(s.subtitle || s.tagline)}"/>
<meta property="og:title" content="${escapeHtml(s.brand)}"/>
<meta property="og:image" content="${s.heroImage || 'assets/hero.svg'}"/>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 8'%3E%3Crect width='8' height='8' fill='${encodeURIComponent(s.bg)}'/%3E%3Ccircle cx='4' cy='4' r='2' fill='${encodeURIComponent(s.accent)}'/%3E%3C/svg%3E"/>
<link rel="stylesheet" href="site.css"/>
<style>
  :root {
    --bg: ${s.bg}; --accent: ${s.accent}; --text: ${s.text};
    --serif: ${fontSerif};
  }
</style>
</head>
<body>
  <div id="veil"><div class="mark">${escapeHtml(s.brand)}</div><div class="bar"><i></i></div></div>

  <canvas id="scene"></canvas>
  <div class="vignette"></div>
  <div class="grain"></div>

  <header class="topbar">
    <span>${escapeHtml(s.brand)}</span>
    <span>${escapeHtml((s.templateId || '') && 'NO. ' + s.templateId)}</span>
  </header>
  ${hud}

  <main>
${chapters}
  </main>

  <div class="scrollcue">${escapeHtml(s.ui?.scroll || 'scroll ↓')}</div>

  <script>window.__STORY__ = ${JSON.stringify(s)};</script>
  ${scripts}
  <script src="engine.js"></script>
  <script>
    (function () {
      var veil = document.getElementById('veil');
      var t = setInterval(function () {
        if (window.__ENGINE_READY__) { veil.classList.add('gone'); clearInterval(t); }
      }, 60);
      setTimeout(function () { veil.classList.add('gone'); }, 4000); // safety
    })();
  </script>
</body>
</html>`;
}

function renderChapters(s) {
  const out = [];
  const sections = s.sections || [];
  sections.forEach((sec, i) => {
    if (i === 0) {
      // hero
      out.push(`    <section class="chapter" data-align="left" data-id="${escapeHtml(sec.id)}">
      <div class="chapter-inner">
        ${sec.kicker ? `<div class="kicker">${escapeHtml(sec.kicker)}</div>` : ''}
        <h1>${escapeHtml(sec.title || s.tagline)}</h1>
        ${s.subtitle ? `<div class="hero-sub">${escapeHtml(s.subtitle)}</div>` : ''}
      </div>
    </section>`);
    } else {
      const align = i % 2 === 0 ? 'right' : 'left';
      out.push(`    <section class="chapter" data-align="${align}" data-id="${escapeHtml(sec.id)}">
      <div class="chapter-inner">
        ${sec.kicker ? `<div class="kicker">${escapeHtml(sec.kicker)}</div>` : ''}
        <h2>${escapeHtml(sec.title)}</h2>
        ${sec.body ? `<p class="lead">${escapeHtml(sec.body)}</p>` : ''}
      </div>
    </section>`);
    }
  });

  // specs strip (if any)
  if (s.specs && s.specs.length) {
    out.push(`    <section class="chapter" data-align="left" data-id="specs">
      <div class="chapter-inner">
        <div class="kicker">${escapeHtml(s.ui?.specification || 'Specification')}</div>
        <div class="specs">
          ${s.specs.map(([k, v]) => `<div class="spec"><div class="k">${escapeHtml(k)}</div><div class="v">${escapeHtml(v)}</div></div>`).join('\n          ')}
        </div>
      </div>
    </section>`);
  }

  // CTA
  if (s.cta) {
    out.push(`    <section class="chapter cta" data-align="center" data-id="cta">
      <div class="chapter-inner">
        <h2>${escapeHtml(s.cta.headline || s.tagline)}</h2>
        <a class="btn" href="#">${escapeHtml(s.cta.button || 'Get in touch')}</a>
      </div>
    </section>`);
  }
  return out.join('\n');
}
