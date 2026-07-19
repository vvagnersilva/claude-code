---
name: guided-setup
description: Master orchestrator that takes a non-developer from zero to working server-side tracking. Use when the recipient says "set this up", "get my tracking working", "start from scratch", "deploy this", "I just unpacked this", "onboard me", or "do the whole thing". Runs the 11-step 0→working journey in order, choosing INSTRUCT (tell them what to click) or EXECUTE (drive the browser via Playwright MCP) per the recipient's preference. Delegates CLI steps to stack/.claude/skills/deploy-stack and browser steps to the browser-* skills in this repo, then verifies with check-tracking.
---

# Skill: guided-setup

You are onboarding a recipient from nothing to a live, verified tracking
stack. They are almost certainly a non-developer. Talk plainly, explain *why*
each step matters in one sentence, never dump raw command output — summarize.

This skill is the conductor. It does not re-implement the CLI deploy steps or
the browser steps — it runs them in the right order, in the recipient's chosen
mode, and keeps a running checklist so you can resume if the conversation is
interrupted.

## Step 0 — Choose a mode and check prerequisites

First ask: **"Do you want me to walk you through each step so you click the
buttons yourself (INSTRUCT), or should I drive the browser for you where I
can (EXECUTE)? You can switch any time, and even in EXECUTE mode you'll log
into your own accounts and approve anything permanent."**

Record the choice as `MODE`. Default to INSTRUCT if unsure.

Then verify prerequisites (run these regardless of mode):

```bash
gh auth status            # GitHub CLI authenticated?
npx wrangler@latest --version   # wrangler reachable (Node installed)?
node --version
```

Confirm verbally that they have: a Cloudflare account (free tier fine), a
Meta Business Manager with a Pixel (or willingness to create one), and — if
they'll run a sales page — an Eduzz / Hotmart / Kiwify account. If `gh` isn't
authenticated, have them run `gh auth login`. If Node/wrangler is missing,
point them at nodejs.org and stop.

Print the journey so they know the shape of what's coming:

```
We'll do this in order. ✓ = done.
  1. Meta: Pixel + conversions API token
  2. Cloudflare D1 database + migrations (CLI)
  3. Generate your dashboard key + webhook slugs (CLI)
  4. Push the stack to a private GitHub repo (CLI)
  5. Cloudflare: create the Pages project
  6. Cloudflare: connect the database
  7. Cloudflare: add your settings (env vars)
  8. Deploy and wait for green
  9. Add your first page
 10. Connect your sales platform webhook (if you have one)
 11. Verify the whole chain on a real visit
```

## Running the steps

For each step, state which one you're on, do it in `MODE`, confirm it landed,
then move to the next. Keep the checklist updated in your replies so a
resumed conversation can see progress.

### Step 1 — Meta Pixel + CAPI token  → skill `browser-meta-capi`

Invoke `browser-meta-capi` in `MODE`. Outcome you need before moving on:
- `META_PIXEL_ID` (numeric) — keep in context, it's not a secret.
- `META_ACCESS_TOKEN` (CAPI token) — **a secret**. In EXECUTE mode, leave it
  in the source browser tab; you'll move it into Cloudflare in Step 7 without
  echoing it. In INSTRUCT mode, tell the recipient to copy it into their
  password manager now.
- Optional `META_TEST_EVENT_CODE` for the Test Events tab.

### Steps 2-4 — D1, local secrets, GitHub push  → `stack/.claude/skills/deploy-stack`

These are CLI-only and identical in both modes. Run **deploy-stack Steps 1
through 7** verbatim against the **`stack/` subfolder** (cd into `stack/`
first — that's the deployable repo that gets its own GitHub remote). That
covers: `wrangler login`, pick `PROJECT_NAME`, `d1 create`, write
`wrangler.toml`, `d1 migrations apply --remote`, generate `DASH_KEY` and
per-platform webhook slugs, `gh repo create … --source=. --push`.

Carry forward into your context: `PROJECT_NAME`, the D1 `database_id`, the
GitHub repo URL, `DASH_KEY`, and any webhook slugs. You'll need them in the
browser steps. Do **not** write the secrets to any file.

### Steps 5-8 — Cloudflare Pages, D1 binding, env vars, deploy  → skill `browser-cloudflare-pages`

Invoke `browser-cloudflare-pages` in `MODE`, passing it: `PROJECT_NAME`, the
GitHub repo URL, the D1 database name (`${PROJECT_NAME}-db`), and the full
env-var checklist (from deploy-stack Step 10) — `META_PIXEL_ID`,
`META_ACCESS_TOKEN`, `DASH_KEY`, plus any optional GA4/Google Ads/webhook
slugs the recipient wants. In EXECUTE mode this is where the Meta token moves
from the Meta tab into the Cloudflare encrypted env-var field without ever
hitting chat or disk.

### Step 9 — First page  → `stack/.claude/skills/add-page`

Ask whether they want a lead form, a sales page, or both. Run `add-page` from
`stack/`. They must visit the deployed page at least once before Step 11 —
verification needs real traffic in D1.

### Step 10 — Sales platform webhook  → skill `browser-sales-webhook`

Skip if they have no sales page. Otherwise invoke `browser-sales-webhook` in
`MODE` with the platform name and the full webhook URL
(`https://${PROJECT_NAME}.pages.dev/webhook/<platform>/<slug>`).

### Step 11 — Verify  → skill `check-tracking`

Invoke `check-tracking`. It runs the 6-checkpoint D1 chain and a live
Playwright visit. Only declare success when every checkpoint is PASS or a
justified SKIP.

## Finishing

When the chain is green, hand over the summary block from deploy-stack Step
12 (project URL, GitHub URL, dashboard URL with `DASH_KEY`, env vars set —
**names only, never values**) and tell them they can start running paid
traffic. Remind them the `DASH_KEY` lives only in their password manager.

## Resuming an interrupted setup

If the recipient comes back mid-journey, ask which steps are already done (or
infer: does `stack/wrangler.toml` exist? does the GitHub repo exist? does
`https://${PROJECT_NAME}.pages.dev` respond?) and pick up at the first
incomplete step. Never re-run `d1 create` or `gh repo create` blindly — check
first (`wrangler d1 list`, `gh repo view`).
