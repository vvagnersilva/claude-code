// pipeline/lib/verify.js — Stage 5: Playwright QC.
// Proves the 3D + continuity effect is REAL: live WebGL/canvas, an active render
// loop, and rendered pixels that genuinely change across scroll positions.
// Follows correction G001: never use networkidle; domcontentloaded + explicit wait.
import path from 'node:path';
import fs from 'node:fs';
import { serve } from './server.js';
import { ROOT, ensureDir, writeJSON, ok, info, warn, c } from './util.js';

const POSITIONS = [0, 0.25, 0.5, 0.75, 1.0];
const DIFF_THRESHOLD = 8; // mean abs per-channel delta (0..255) between first & last

export async function verify(siteDir, opts = {}) {
  const slug = opts.slug || path.basename(siteDir);
  const shotDir = ensureDir(opts.shotDir || path.join(ROOT, 'qc', 'screenshots'));
  let chromium;
  try { ({ chromium } = await import('playwright')); }
  catch { throw new Error("playwright not installed — run `npm install` then `npx playwright install chromium`"); }

  const { server, url } = await serve(siteDir);
  const browser = await chromium.launch({
    headless: true,
    args: ['--disable-dev-shm-usage', '--disable-background-timer-throttling',
      '--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding',
      '--use-gl=angle', '--enable-webgl', '--ignore-gpu-blocklist'],
  });
  const report = { slug, url, engine: null, checks: {}, samples: [], screenshots: [], pass: false, errors: [] };
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    const consoleErrors = [];
    page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()); });
    page.on('pageerror', (e) => consoleErrors.push(String(e)));

    info(`navigating ${url}`);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

    // engine ready
    await page.waitForFunction('window.__ENGINE_READY__ === true', { timeout: 20000 });
    report.engine = await page.evaluate('window.__STORY__ && window.__STORY__.engine');
    report.checks.engineReady = true;
    ok(`engine ready (${report.engine})`);

    // WebGL support (webgl engine) or 2D canvas (frameseq)
    const gl = await page.evaluate(() => {
      const cv = document.createElement('canvas');
      return !!(cv.getContext('webgl2') || cv.getContext('webgl') || cv.getContext('experimental-webgl'));
    });
    report.checks.webglAvailable = gl;
    if (report.engine === 'webgl' && !gl) report.errors.push('WebGL context not available');
    ok(`WebGL available: ${gl}`);

    // MANDATORY quality bar: real (non-stub) frame sequences must be ≥1280px
    // wide — Retina canvases upscale ~2.2×, anything lower reads as pixelated.
    const frames = await page.evaluate('window.__STORY__ && window.__STORY__.frames');
    if (frames && frames.stubbed === false && typeof frames.width === 'number') {
      report.checks.frameWidth = frames.width;
      if (frames.width < 1280) report.errors.push(`frame quality below mandatory bar: ${frames.width}px < 1280px`);
      else ok(`frame quality: ${frames.width}px wide (bar ≥1280px)`);
    }

    // render loop liveness
    const r1 = await page.evaluate('window.__RENDERED__ || 0');
    await page.waitForTimeout(500);
    const r2 = await page.evaluate('window.__RENDERED__ || 0');
    report.checks.renderLoopActive = r2 > r1;
    report.checks.framesRendered = r2;
    if (r2 <= r1) report.errors.push('render loop not advancing');
    ok(`render loop active: ${r2 > r1} (${r1}→${r2} frames)`);

    // scroll through positions: screenshot + sample the actual rendered canvas
    for (let i = 0; i < POSITIONS.length; i++) {
      const frac = POSITIONS[i];
      await page.evaluate((f) => window.__scrollTo(f), frac);
      await page.waitForTimeout(850);
      const progress = await page.evaluate('window.__PROGRESS__ || 0');
      const sample = await page.evaluate(() => {
        const scene = document.getElementById('scene');
        const c = document.createElement('canvas'); c.width = 32; c.height = 18;
        const ctx = c.getContext('2d');
        try { ctx.drawImage(scene, 0, 0, 32, 18); } catch (e) { return null; }
        const d = ctx.getImageData(0, 0, 32, 18).data;
        let sum = 0; const arr = [];
        for (let k = 0; k < d.length; k += 4) { arr.push(d[k], d[k + 1], d[k + 2]); sum += d[k] + d[k + 1] + d[k + 2]; }
        return { arr, avg: sum / (arr.length) };
      });
      // Engine in the filename: webgl + frameseq runs of the same slug must not
      // overwrite each other's QC evidence.
      const shotPath = path.join(shotDir, `${slug}-${report.engine || 'site'}-${String(i).padStart(2, '0')}-p${Math.round(frac * 100)}.png`);
      await page.screenshot({ path: shotPath });
      report.screenshots.push(shotPath);
      report.samples.push({ frac, progress, avg: sample ? Math.round(sample.avg) : null, _arr: sample?.arr || null });
      info(`scroll ${Math.round(frac * 100)}% → progress=${progress.toFixed(2)} avgLuma=${sample ? Math.round(sample.avg) : 'n/a'} · ${path.basename(shotPath)}`);
    }

    // continuity: rendered pixels must change across scroll
    const first = report.samples[0]?._arr, last = report.samples[report.samples.length - 1]?._arr;
    let meanDelta = 0, maxPairDelta = 0;
    if (first && last) {
      let s = 0; for (let k = 0; k < first.length; k++) s += Math.abs(first[k] - last[k]);
      meanDelta = s / first.length;
    }
    // also the largest delta between any adjacent pair (catches mid-scroll motion)
    for (let i = 1; i < report.samples.length; i++) {
      const a = report.samples[i - 1]._arr, b = report.samples[i]._arr;
      if (!a || !b) continue;
      let s = 0; for (let k = 0; k < a.length; k++) s += Math.abs(a[k] - b[k]);
      maxPairDelta = Math.max(maxPairDelta, s / a.length);
    }
    report.checks.pixelDeltaFirstLast = Math.round(meanDelta * 100) / 100;
    report.checks.pixelDeltaMaxAdjacent = Math.round(maxPairDelta * 100) / 100;
    const continuity = Math.max(meanDelta, maxPairDelta) >= DIFF_THRESHOLD;
    report.checks.continuityAcrossScroll = continuity;
    if (!continuity) report.errors.push(`scene barely changes across scroll (Δ=${meanDelta.toFixed(1)} < ${DIFF_THRESHOLD})`);

    // scroll actually reached the end
    const endProgress = report.samples[report.samples.length - 1]?.progress || 0;
    report.checks.reachedEnd = endProgress > 0.9;
    if (endProgress <= 0.9) report.errors.push(`scroll did not reach end (progress=${endProgress.toFixed(2)})`);

    report.consoleErrors = consoleErrors.slice(0, 10);
    // strip raw arrays from the saved report (keep it small)
    report.samples = report.samples.map(({ _arr, ...rest }) => rest);

    report.pass = report.checks.engineReady && report.checks.renderLoopActive
      && report.checks.continuityAcrossScroll && report.checks.reachedEnd
      && (report.engine !== 'webgl' || report.checks.webglAvailable);

    const line = report.pass ? c.green('QC PASS') : c.red('QC FAIL');
    console.log(`\n  ${line} — continuityΔ=${report.checks.pixelDeltaFirstLast} (min ${DIFF_THRESHOLD}) · frames=${report.checks.framesRendered} · endProgress=${endProgress.toFixed(2)}`);
    if (!report.pass) report.errors.forEach((e) => warn(e));
  } catch (e) {
    report.errors.push(String(e.message || e));
    warn(`verify error: ${e.message || e}`);
  } finally {
    await browser.close();
    server.close();
  }

  writeJSON(path.join(siteDir, 'qc-report.json'), report);
  return report;
}

// CLI: `npm run verify -- output/abyssal`
if (import.meta.url === `file://${process.argv[1]}`) {
  const dir = process.argv[2] || 'output';
  const abs = path.isAbsolute(dir) ? dir : path.join(ROOT, dir);
  verify(abs, { slug: path.basename(abs) }).then((r) => { console.log('\n' + JSON.stringify(r.checks, null, 2)); process.exit(r.pass ? 0 : 1); });
}
