#!/usr/bin/env node
// pipeline/lib/higgsfield-session.js — restore + verify the Higgsfield browser
// session (Clerk auth). The consumer Higgsfield product has NO public REST API,
// so "logged in" means: valid Clerk cookies in a real browser context.
//
//   npm run higgsfield:login          # restore saved cookies → verify → re-save
//   node pipeline/lib/higgsfield-session.js --headed   # watch it happen
//
// Session file: .claude/auth/higgsfield-storage-state.json (gitignored).
// The durable `__client` Clerk refresh token (~1y) re-mints a fresh `__session`
// on first navigation, so we NEVER inject `__session*` (stale ones make the
// Next.js SSR 500). If the refresh token is dead, this exits 3 and a fresh
// email+password+emailed-code login is required (HIGGSFIELD_EMAIL /
// HIGGSFIELD_PASSWORD in .env; the 6-digit code goes to that inbox).
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';
import { ROOT, ok, info, warn } from './util.js';

const STATE = path.join(ROOT, '.claude', 'auth', 'higgsfield-storage-state.json');
const KEEP = ['name', 'value', 'domain', 'path', 'expires', 'httpOnly', 'secure', 'sameSite'];
const VALID_SS = new Set(['Strict', 'Lax', 'None']);

function loadCookies() {
  if (!fs.existsSync(STATE)) return null;
  const now = Date.now() / 1000;
  return JSON.parse(fs.readFileSync(STATE, 'utf8')).cookies
    .filter((c) => (c.domain || '').includes('higgsfield'))
    .filter((c) => !(c.expires > 0 && c.expires < now))
    .filter((c) => !c.name.startsWith('__session')) // Clerk re-mints from __client
    .map((c) => {
      const cc = Object.fromEntries(KEEP.filter((k) => k in c).map((k) => [k, c[k]]));
      if (!VALID_SS.has(cc.sameSite)) cc.sameSite = 'Lax';
      return cc;
    });
}

async function main() {
  const headed = process.argv.includes('--headed');
  const cookies = loadCookies();
  if (!cookies || !cookies.length) {
    warn(`no saved session at ${STATE} — fresh login required`);
    process.exit(2);
  }
  if (!cookies.some((c) => c.name === '__client')) {
    warn('saved session has no __client refresh token — fresh login required');
    process.exit(3);
  }
  info(`restoring ${cookies.length} higgsfield cookies (no __session — Clerk re-mints from __client)`);

  const browser = await chromium.launch({ headless: !headed });
  try {
    const context = await browser.newContext();
    await context.addCookies(cookies);
    const page = await context.newPage();
    await page.goto('https://higgsfield.ai/', { waitUntil: 'domcontentloaded', timeout: 60_000 });

    // Authoritative check: wait for Clerk to boot and report a user.
    const user = await page.waitForFunction(
      () => (window.Clerk?.loaded && window.Clerk?.user)
        ? { id: window.Clerk.user.id, email: window.Clerk.user.primaryEmailAddress?.emailAddress || null }
        : false,
      null, { timeout: 45_000 },
    ).then((h) => h.jsonValue()).catch(() => null);

    if (!user) {
      warn('Clerk reports NO logged-in user — session expired/revoked → fresh login required');
      process.exit(3);
    }
    // Persist the rotated session (Clerk minted fresh tokens on this navigation).
    await context.storageState({ path: STATE });
    ok(`Higgsfield logged in as ${user.email || user.id} — rotated session saved to ${path.relative(ROOT, STATE)}`);
  } finally {
    await browser.close();
  }
}

main().catch((e) => { warn(`higgsfield session check failed: ${e.message}`); process.exit(1); });
