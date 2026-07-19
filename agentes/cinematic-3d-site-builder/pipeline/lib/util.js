// pipeline/lib/util.js — small shared helpers (no external deps)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const ROOT = path.resolve(__dirname, '..', '..'); // repo root

export const c = {
  dim: (s) => `\x1b[2m${s}\x1b[0m`,
  cyan: (s) => `\x1b[36m${s}\x1b[0m`,
  green: (s) => `\x1b[32m${s}\x1b[0m`,
  yellow: (s) => `\x1b[33m${s}\x1b[0m`,
  red: (s) => `\x1b[31m${s}\x1b[0m`,
  bold: (s) => `\x1b[1m${s}\x1b[0m`,
};

let stageN = 0;
export function stage(name, detail = '') {
  stageN += 1;
  console.log(`\n${c.cyan(`▸ STAGE ${stageN} · ${name}`)} ${c.dim(detail)}`);
}
export function ok(msg) { console.log(`  ${c.green('✓')} ${msg}`); }
export function info(msg) { console.log(`  ${c.dim('·')} ${msg}`); }
export function warn(msg) { console.log(`  ${c.yellow('!')} ${msg}`); }

export function slugify(s) {
  return String(s || 'site')
    .toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') || 'site';
}

export function ensureDir(p) { fs.mkdirSync(p, { recursive: true }); return p; }
export function writeFile(p, data) { ensureDir(path.dirname(p)); fs.writeFileSync(p, data); return p; }
export function writeJSON(p, obj) { return writeFile(p, JSON.stringify(obj, null, 2)); }
export function copyFile(src, dst) { ensureDir(path.dirname(dst)); fs.copyFileSync(src, dst); return dst; }

// ── color math (hex ↔ rgb, mix) — used by plan + placeholder frames ───────────
export function hexToRgb(hex) {
  const h = String(hex).replace('#', '');
  const n = parseInt(h.length === 3 ? h.split('').map((x) => x + x).join('') : h, 16);
  return { r: (n >> 16) & 255, g: (n >> 8) & 255, b: n & 255 };
}
export function rgbToHex({ r, g, b }) {
  const to = (v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0');
  return `#${to(r)}${to(g)}${to(b)}`;
}
export function mixHex(a, b, t) {
  const A = hexToRgb(a), B = hexToRgb(b);
  return rgbToHex({ r: A.r + (B.r - A.r) * t, g: A.g + (B.g - A.g) * t, b: A.b + (B.b - A.b) * t });
}
export function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, (ch) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]
  ));
}
