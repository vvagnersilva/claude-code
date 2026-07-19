# Tracking Setup Guide

> Claude Code's anchor file — loaded into every conversation in this repo.
> Keep under ~200 lines. Detailed walkthroughs live in `.claude/skills/`,
> browser selector references in `playbook/`, and the deployable code in
> `stack/`.

## What this repo is

A **guided onboarding wrapper** that takes a non-developer from **zero to
working server-side tracking**. It bundles the deployable tracking stack
(in `stack/`) and adds a layer of skills that can either **instruct** the
recipient through each step or **execute** the browser-based steps for them
via the **Playwright MCP** — then **verify** the whole chain end-to-end.

The deployable code in `stack/` is the Cloudflare Pages + D1 tracking stack
(Meta CAPI / GA4 / Google Ads server-side conversions, first-party
attribution, built-in dashboard). It is self-contained and unchanged from its
upstream template — this repo does not fork it, it orchestrates its setup.

### What this adds on top of `stack/`

The stack's own skills (`stack/.claude/skills/deploy-stack`,
`verify-tracking`, `add-page`, `add-sales-platform`) **instruct** the user
through manual dashboard clicking. This wrapper adds:

1. **An execution layer** — every manual dashboard step (Meta Pixel + CAPI
   token, Cloudflare Pages project, D1 binding, env vars, sales-platform
   webhook config) has a Playwright-MCP skill that can drive the browser
   itself instead of just telling the user where to click.
2. **A single orchestrator** (`guided-setup`) that walks the full 0→working
   journey in order, choosing INSTRUCT or EXECUTE per the recipient's
   preference.
3. **A live verification skill** (`check-tracking`) that combines the stack's
   D1 integrity checks with a real Playwright browser visit to prove the
   chain fires on live traffic.

## Two modes — INSTRUCT vs EXECUTE

The recipient chooses up front (and can switch per step):

- **INSTRUCT** — you tell them exactly what to click, one step at a time, and
  wait for them to confirm. This is the safe default for anyone who wants to
  keep their hands on their own infrastructure. It mirrors the stack's
  existing `deploy-stack` skill.
- **EXECUTE** — you drive the browser yourself with the Playwright MCP:
  navigate, fill forms, click. The recipient still **logs in themselves**
  (you never handle their passwords) and still **approves** anything
  irreversible before you commit it.

Ask which mode they want at the start of `guided-setup`. When in doubt,
INSTRUCT.

## Hard rules (security — do not violate)

- **Never handle the recipient's account password.** In EXECUTE mode you
  navigate to the login page and hand control back so *they* type
  credentials. You resume only after they confirm they're logged in.
- **Secrets never touch chat or disk.** Access tokens (Meta CAPI, GA4 API
  secret, Google Ads, webhook slugs) must go straight into Cloudflare's
  **encrypted** environment variables. In EXECUTE mode you may move a token
  browser-to-browser (read it from the source tab, type it into the
  Cloudflare env-var field) but you must **never echo it into the chat, never
  write it to any file, and never log it.** If you cannot avoid surfacing a
  secret, switch that one step to INSTRUCT and let the recipient paste it.
- **Inherit every hard rule from `stack/CLAUDE.md`.** Never commit secrets
  (`wrangler.toml`, `.dev.vars`, `.env*` stay gitignored); never log PageView
  to `event_log`; always parameterized SQL with `.bind()`; hash PII before it
  leaves the recipient's infra; webhook endpoints gated by an obscure UUID
  slug; `DASH_KEY` and `SYNC_SECRET` are never the same value.
- **Approve before irreversible.** Creating the Pages project, pushing to a
  new GitHub repo, applying D1 migrations, triggering a deploy — confirm with
  the recipient before each, even in EXECUTE mode.

## The 0→working journey

`guided-setup` runs these in order. Each browser step links to its execution
skill; CLI steps run directly.

| # | Step | Tool | Skill / reference |
|---|---|---|---|
| 0 | Check prerequisites (CF account, GitHub + `gh`, Node, Meta BM, Claude Code) | CLI | `guided-setup` Step 0 |
| 1 | Meta: create/confirm Pixel, generate CAPI token, grab Pixel ID | Browser | `browser-meta-capi` |
| 2 | `wrangler login`, create D1, write `wrangler.toml`, apply migrations | CLI | `stack/.claude/skills/deploy-stack` Steps 1-5 |
| 3 | Generate `DASH_KEY` + webhook slugs locally | CLI | `deploy-stack` Step 6 |
| 4 | Create private GitHub repo from `stack/` and push | CLI (`gh`) | `deploy-stack` Step 7 |
| 5 | Cloudflare: create Pages project, connect GitHub repo | Browser | `browser-cloudflare-pages` |
| 6 | Cloudflare: bind D1 as `DB` | Browser | `browser-cloudflare-pages` |
| 7 | Cloudflare: set env vars (Pixel ID, CAPI token, DASH_KEY, slugs…) | Browser | `browser-cloudflare-pages` |
| 8 | Trigger redeploy, wait for green | Browser/CLI | `browser-cloudflare-pages` |
| 9 | Add first page (lead form or sales page) | CLI | `stack/.claude/skills/add-page` |
| 10 | Sales platform: paste webhook URL into Eduzz/Hotmart/Kiwify | Browser | `browser-sales-webhook` |
| 11 | Verify the whole chain on live traffic | Browser + CLI | `check-tracking` |

## Triage — what to do when a recipient starts a conversation

- "set this up", "get my tracking working", "start from scratch", "I just
  unpacked this" → invoke **`guided-setup`** (the orchestrator).
- "is my tracking working", "check it", "verify", "Meta shows no
  conversions" → invoke **`check-tracking`**.
- "just do the Meta part", "create my CAPI token" → **`browser-meta-capi`**.
- "set up Cloudflare", "create the Pages project", "add my env vars" →
  **`browser-cloudflare-pages`**.
- "connect my Eduzz/Hotmart/Kiwify webhook" → **`browser-sales-webhook`**.
- "add a lead/sales page" → defer to **`stack/.claude/skills/add-page`**.
- "I use a platform that isn't Eduzz/Hotmart/Kiwify" → defer to
  **`stack/.claude/skills/add-sales-platform`**.

For anything about the stack's internals (schema, data flow, identifier
chain, webhook adapters), read `stack/CLAUDE.md` and `stack/docs/`.

## Skills in this wrapper

All under `.claude/skills/<name>/SKILL.md`.

| Skill | Mode | What it does |
|---|---|---|
| `guided-setup` | both | Master orchestrator for the 0→working journey. Picks INSTRUCT/EXECUTE, runs steps in order, hands off to CLI skills in `stack/` and browser skills here. |
| `browser-meta-capi` | EXECUTE (INSTRUCT fallback) | Playwright drive of Meta Events Manager: confirm/create Pixel, generate CAPI access token, capture Pixel ID + optional Test Event Code. |
| `browser-cloudflare-pages` | EXECUTE (INSTRUCT fallback) | Playwright drive of the Cloudflare dashboard: create Pages project from the GitHub repo, bind D1 as `DB`, add env vars, trigger redeploy. |
| `browser-sales-webhook` | EXECUTE (INSTRUCT fallback) | Playwright drive of Eduzz/Hotmart/Kiwify dashboards to register the `/webhook/<platform>/<slug>` URL. |
| `check-tracking` | both | Runs the stack's 6-checkpoint D1 integrity chain AND drives a live Playwright browser visit to prove sessions/events fire on real traffic. |

## How browser skills use the Playwright MCP

The Playwright MCP tools are available in this repo. The pattern for every
browser skill:

1. `browser_navigate` to the dashboard URL.
2. `browser_snapshot` to read the accessibility tree (preferred over
   screenshots for finding elements — it gives stable refs).
3. If a login wall appears, **stop and hand off** to the recipient; resume
   after they confirm.
4. `browser_click` / `browser_type` / `browser_fill_form` against refs from
   the snapshot. Re-snapshot after navigation since refs go stale.
5. Verify each action landed (re-snapshot, check for the expected element)
   before reporting success. Never "fake green".

Selector and layout notes that drift over time live in `playbook/` so the
skills themselves stay stable. If a dashboard's UI has changed and a selector
is gone, fall back to INSTRUCT for that step and note the drift.

## Deep reference

| For… | Read |
|---|---|
| The deployable stack — what it is, file map, identifier chain | `stack/CLAUDE.md` |
| CLI deploy steps (wrangler, gh) in full detail | `stack/.claude/skills/deploy-stack/SKILL.md` |
| The 6-checkpoint integrity chain in full detail | `stack/.claude/skills/verify-tracking/SKILL.md` |
| Architecture / data flow / schema | `stack/docs/` |
| Browser selector references | `playbook/` |
