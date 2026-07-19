// pipeline/lib/providers.js
// ────────────────────────────────────────────────────────────────────────────
// The generation contract — REAL when credentials are present, cleanly STUBBED
// when they are not. This module never fabricates a successful render: a
// stubbed asset is explicitly marked `stubbed: true`.
//
// Provider priority (first match wins):
//   1. higgsfield — HIGGSFIELD_API_KEY set (direct HTTP API; also honours
//      HIGGSFIELD_BASE_URL, default https://api.higgsfield.ai/v1). NOTE: the
//      consumer Higgsfield product is browser-only (no public REST API) — this
//      path is for an API key if/when one exists. Browser login lives in
//      pipeline/lib/higgsfield-session.js (`npm run higgsfield:login`).
//   2. fal — FAL_KEY set. Same ByteDance models via fal.ai:
//        video: bytedance/seedance-2.0/{reference-to-video,image-to-video,text-to-video}
//        image: fal-ai/nano-banana-pro
//      Queue API (submit → poll → result) + fal storage upload for local files.
//   3. stub — no credentials → procedural placeholders, marked stubbed:true.
//
// Credentials are read from the environment or from a repo-root `.env`
// (KEY=VALUE lines; never committed — see .gitignore).
// ────────────────────────────────────────────────────────────────────────────
import fs from 'node:fs';
import path from 'node:path';
import { ROOT, info, warn } from './util.js';

// ── tiny .env loader (no deps; existing env vars win) ────────────────────────
function loadDotEnv() {
  const p = path.join(ROOT, '.env');
  if (!fs.existsSync(p)) return;
  for (const line of fs.readFileSync(p, 'utf8').split('\n')) {
    const m = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
    if (!m || line.trim().startsWith('#')) continue;
    const val = m[2].replace(/^["']|["']$/g, '');
    if (!(m[1] in process.env)) process.env[m[1]] = val;
  }
}
loadDotEnv();

const BASE_URL = process.env.HIGGSFIELD_BASE_URL || 'https://api.higgsfield.ai/v1';
const API_KEY = process.env.HIGGSFIELD_API_KEY || '';
const FAL_KEY = process.env.FAL_KEY || '';

// ASSETS_MODE=stub forces placeholder assets even when credentials exist
// (real Seedance clips are paid — use this for free layout/QC iterations).
export const PROVIDER = process.env.ASSETS_MODE === 'stub' ? 'stub'
  : API_KEY ? 'higgsfield' : FAL_KEY ? 'fal' : 'stub';
export const HAS_CREDENTIALS = PROVIDER !== 'stub';

/**
 * The exact request the real Seedance 2.0 image-to-video call expects.
 * Documented here so a future integrator has the whole contract in one place.
 */
function seedancePayload({ prompt, referenceImage, startImage, endImage, gen }) {
  return {
    model: gen.model || 'seedance-2.0',        // [VIDEO] "C Dance 2.0"
    mode: gen.mode || 'std',                    // [PDF] std mode is the sweet spot
    resolution: gen.resolution || '1080p',
    aspect_ratio: gen.aspect || '16:9',
    duration: gen.durationSec || 8,             // [PDF] ~8s per clip
    audio: false,
    prompt,
    // [PDF How-to #2] the hero image is referenced on EVERY clip → consistency
    reference_images: referenceImage ? [referenceImage] : [],
    // [PDF How-to #3] chained clips: previous clip's final frame as start image
    start_image: startImage || null,
    end_image: endImage || null,
  };
}

async function callHiggsfield(pathname, payload) {
  // Real network call. Only reached when PROVIDER === 'higgsfield'.
  const res = await fetch(`${BASE_URL}${pathname}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${API_KEY}` },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Higgsfield ${pathname} → ${res.status} ${await res.text()}`);
  return res.json();
}

// ── fal.ai fallback ──────────────────────────────────────────────────────────
const FAL_QUEUE = 'https://queue.fal.run';
const FAL_STORAGE_INITIATE = 'https://rest.alpha.fal.ai/storage/upload/initiate';
const FAL_BALANCE = 'https://rest.alpha.fal.ai/billing/user_balance';
const falHeaders = { 'Content-Type': 'application/json', Authorization: `Key ${FAL_KEY}` };

/** Current fal.ai account balance in USD, or null if unavailable. */
export async function falBalance() {
  if (PROVIDER !== 'fal') return null;
  try {
    const r = await fetch(FAL_BALANCE, { headers: falHeaders });
    if (!r.ok) return null;
    const v = parseFloat((await r.text()).trim());
    return Number.isFinite(v) ? v : null;
  } catch { return null; }
}

/** Submit to the fal queue, poll status, return the final result JSON. */
async function falQueueRun(endpoint, input, { pollMs = 5000, timeoutMs = 15 * 60_000 } = {}) {
  const submit = await fetch(`${FAL_QUEUE}/${endpoint}`, {
    method: 'POST', headers: falHeaders, body: JSON.stringify(input),
  });
  if (!submit.ok) throw new Error(`fal submit ${endpoint} → ${submit.status} ${await submit.text()}`);
  const { request_id, status_url, response_url } = await submit.json();

  const deadline = Date.now() + timeoutMs;
  const started = Date.now();
  let last = '';
  let probed = false;
  for (;;) {
    const st = await fetch(status_url, { headers: falHeaders });
    if (!st.ok) throw new Error(`fal status ${endpoint} → ${st.status} ${await st.text()}`);
    const { status, queue_position } = await st.json();
    if (status !== last) { info(`fal ${endpoint} → ${status}${queue_position != null ? ` (queue #${queue_position})` : ''}`); last = status; }
    // The status endpoint can report IN_QUEUE forever on a locked account
    // (seen live 2026-07-08: exhausted balance). After 90s stuck, probe the
    // result endpoint once — it surfaces the real account error.
    if (status === 'IN_QUEUE' && !probed && Date.now() - started > 90_000) {
      probed = true;
      const peek = await fetch(response_url, { headers: falHeaders }).then((r) => r.json()).catch(() => null);
      if (peek?.detail && /locked|balance|billing|payment/i.test(String(peek.detail))) {
        await fetch(`${FAL_QUEUE}/${endpoint}/requests/${request_id}/cancel`, { method: 'PUT', headers: falHeaders }).catch(() => {});
        throw new Error(`fal account error: ${peek.detail}`);
      }
    }
    if (status === 'COMPLETED') break;
    if (status !== 'IN_QUEUE' && status !== 'IN_PROGRESS') {
      throw new Error(`fal ${endpoint} → status ${status} (request ${request_id})`);
    }
    if (Date.now() > deadline) {
      // Cancel before abandoning — a zombie request left IN_QUEUE may still be
      // billed if it eventually completes.
      await fetch(`${FAL_QUEUE}/${endpoint}/requests/${request_id}/cancel`, { method: 'PUT', headers: falHeaders }).catch(() => {});
      throw new Error(`fal ${endpoint} → timed out after ${timeoutMs / 1000}s (last status ${last || 'unknown'}, request ${request_id}, cancelled)`);
    }
    await new Promise((r) => setTimeout(r, pollMs));
  }
  const res = await fetch(response_url, { headers: falHeaders });
  if (!res.ok) throw new Error(`fal result ${endpoint} → ${res.status} ${await res.text()}`);
  return res.json();
}

/** Retry a flaky remote call with a fresh submission (queue hangs, 5xx). */
async function withRetry(fn, label, attempts = 2) {
  let lastErr;
  for (let i = 1; i <= attempts; i++) {
    try { return await fn(); } catch (e) {
      lastErr = e;
      warn(`${label} — attempt ${i}/${attempts} failed: ${e.message}`);
      if (i < attempts) await new Promise((r) => setTimeout(r, 5000));
    }
  }
  throw lastErr;
}

const MIME = { '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.mp4': 'video/mp4' };

/** Upload a local file to fal storage → CDN URL (initiate → PUT → file_url). */
async function falUpload(filePath) {
  const contentType = MIME[path.extname(filePath).toLowerCase()];
  if (!contentType) return null; // e.g. SVG placeholders — not a usable video reference
  const init = await fetch(FAL_STORAGE_INITIATE, {
    method: 'POST', headers: falHeaders,
    body: JSON.stringify({ content_type: contentType, file_name: path.basename(filePath) }),
  });
  if (!init.ok) throw new Error(`fal storage initiate → ${init.status} ${await init.text()}`);
  const { upload_url, file_url } = await init.json();
  const put = await fetch(upload_url, {
    method: 'PUT', headers: { 'Content-Type': contentType }, body: fs.readFileSync(filePath),
  });
  if (!put.ok) throw new Error(`fal storage upload → ${put.status} ${await put.text()}`);
  return file_url;
}

/** http(s) URL → as-is; local raster/video file → uploaded CDN URL; else null. */
async function asRemoteUrl(ref) {
  if (!ref) return null;
  if (/^https?:\/\//i.test(ref)) return ref;
  if (fs.existsSync(ref)) return falUpload(ref);
  return null;
}

/**
 * Generate ONE hero image (Nano-Banana-Pro via Higgsfield or fal.ai).
 * Returns { url|path, stubbed }.
 */
export async function generateHeroImage({ prompt, gen, out }) {
  if (PROVIDER === 'stub') {
    return { stubbed: true, note: 'no HIGGSFIELD_API_KEY / FAL_KEY — hero image is a procedural placeholder', prompt };
  }
  if (PROVIDER === 'fal') {
    // Endpoint fallback chain — nano-banana-pro can sit stuck IN_QUEUE at peak
    // times (seen live 2026-07-08: 2× 900s at queue #0). An image should land
    // in minutes, so each endpoint gets a short window before falling through.
    const chain = ['fal-ai/nano-banana-pro', 'fal-ai/nano-banana-2', 'fal-ai/bytedance/seedream/v4.5/text-to-image'];
    const aspect = gen?.aspect || '16:9';
    const res = gen?.heroImage?.resolution || '2K';
    let lastErr;
    for (const endpoint of chain) {
      const input = endpoint.includes('seedream')
        ? (() => {
            const [aw, ah] = aspect.split(':').map(Number);
            const base = { '1K': 1280, '2K': 2560, '4K': 3840 }[res] || 2560;
            return { prompt, image_size: { width: base, height: Math.round(base * (ah / aw)) }, num_images: 1 };
          })()
        : { prompt, aspect_ratio: aspect, resolution: res, num_images: 1, output_format: 'jpeg' };
      try {
        const data = await falQueueRun(endpoint, input, { timeoutMs: 5 * 60_000 });
        return { stubbed: false, url: data.images?.[0]?.url, prompt, out };
      } catch (e) {
        lastErr = e;
        warn(`hero endpoint ${endpoint} failed: ${e.message} — falling through`);
      }
    }
    throw lastErr;
  }
  const data = await callHiggsfield('/images/generations', {
    model: gen?.heroImage?.model || 'nano-banana-pro',
    quality: '4k', prompt, aspect_ratio: '16:9',
  });
  return { stubbed: false, url: data.data?.[0]?.url, prompt, out };
}

/**
 * Generate ONE Seedance clip. `referenceImage` = hero (always), `startImage` =
 * previous clip's final frame (chained builds). Returns { url, stubbed }.
 */
export async function generateClip({ prompt, referenceImage, startImage, endImage, gen, out }) {
  if (PROVIDER === 'stub') {
    return { stubbed: true, note: 'no HIGGSFIELD_API_KEY / FAL_KEY — clip replaced by procedural frames', prompt };
  }
  if (PROVIDER === 'fal') {
    const common = {
      prompt,
      aspect_ratio: gen.aspect || '16:9',
      resolution: gen.resolution || '1080p',
      duration: String(gen.durationSec || 8),
      generate_audio: false,
    };
    const startUrl = await asRemoteUrl(startImage);
    const refUrl = await asRemoteUrl(referenceImage);
    let endpoint, input;
    if (startUrl) {
      // [PDF How-to #3] chained clip: previous final frame drives the start
      const endUrl = await asRemoteUrl(endImage);
      endpoint = 'bytedance/seedance-2.0/image-to-video';
      input = { ...common, image_url: startUrl, ...(endUrl ? { end_image_url: endUrl } : {}) };
    } else if (refUrl) {
      // [PDF How-to #2] hero referenced on every clip → consistency
      endpoint = 'bytedance/seedance-2.0/reference-to-video';
      input = { ...common, image_urls: [refUrl] };
    } else {
      endpoint = 'bytedance/seedance-2.0/text-to-video';
      input = common;
    }
    const data = await withRetry(() => falQueueRun(endpoint, input), `fal clip (${endpoint})`);
    return { stubbed: false, url: data.video?.url, prompt, out };
  }
  const data = await callHiggsfield('/videos/generations', seedancePayload({ prompt, referenceImage, startImage, endImage, gen }));
  return { stubbed: false, url: data.data?.[0]?.url, prompt, out };
}

export function announceMode() {
  if (PROVIDER === 'higgsfield') info('Higgsfield credentials found → REAL Seedance 2.0 generation.');
  else if (PROVIDER === 'fal') info('FAL_KEY found → REAL generation via fal.ai (Seedance 2.0 + Nano-Banana-Pro fallback).');
  else warn('No HIGGSFIELD_API_KEY / FAL_KEY → ASSETS runs in STUB mode (clean procedural placeholders).');
}
