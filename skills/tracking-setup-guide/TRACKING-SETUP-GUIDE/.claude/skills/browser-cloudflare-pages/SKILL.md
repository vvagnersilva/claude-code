---
name: browser-cloudflare-pages
description: Drives the Cloudflare dashboard via the Playwright MCP to create a Pages project connected to the recipient's GitHub repo, bind the D1 database as DB, add all environment variables (with the Meta CAPI token moved tab-to-tab without ever hitting chat or disk), and trigger a redeploy. Use when the recipient says "set up Cloudflare", "create the Pages project", "bind my database", "add my env vars", or as Steps 5-8 of guided-setup. Has an INSTRUCT fallback mirroring deploy-stack Steps 8-11. Requires PROJECT_NAME, the GitHub repo URL, the D1 database name, and the env-var checklist from deploy-stack Step 10.
---

# Skill: browser-cloudflare-pages

This is the manual half of `deploy-stack` (its Steps 8-11), but executed for
the recipient. Inputs you must already have (from `guided-setup` /
`deploy-stack`): `PROJECT_NAME`, the **GitHub repo URL**, the D1 database name
(`${PROJECT_NAME}-db`), and the env-var checklist (`META_PIXEL_ID`,
`META_ACCESS_TOKEN`, `DASH_KEY`, plus any optional GA4 / Google Ads / webhook
slugs the recipient chose).

**Mode**: EXECUTE or INSTRUCT (passed by `guided-setup`; ask if invoked
directly).

## Security guardrail

`META_ACCESS_TOKEN`, `GA4_API_SECRET`, Google Ads secrets, `DASH_KEY`,
`SYNC_SECRET`, and webhook slugs are **secrets**. When you type them into
Cloudflare env-var fields:

- Mark them **Encrypt** in the Cloudflare UI (the rows flagged 🔒 in
  deploy-stack Step 10, plus `DASH_KEY` and all slugs).
- **Never echo a secret value into chat, never write it to a file, never put
  it in a shell command.** In EXECUTE mode, read each secret from its source
  (the Meta tab for the CAPI token; your in-context generated values for
  `DASH_KEY`/slugs) and `browser_type` it straight into the field.
- If you can't type a secret without surfacing it, switch that single field
  to INSTRUCT and let the recipient paste it.

`META_PIXEL_ID`, `GA4_MEASUREMENT_ID`, `META_ADS_ACCOUNT_ID`,
`TIMEZONE_OFFSET`, `DEFAULT_COUNTRY_CODE` are **not** secrets — leave them
unencrypted.

## EXECUTE mode

### Step 5 — Create the Pages project

1. `browser_navigate` to `https://dash.cloudflare.com/`. `browser_snapshot`.
   If a login wall appears, **hand off**: "Please log into Cloudflare in the
   browser, then tell me when you're in." Resume after they confirm.
2. Navigate to **Workers & Pages → Create → Pages → Connect to Git**.
3. If Cloudflare prompts to install its GitHub App, **stop and hand off** —
   the recipient must authorize the GitHub App on their account (OAuth, their
   credentials). Tell them to authorize it for the repo `PROJECT_NAME`, then
   confirm. Re-snapshot.
4. Select the repo matching the GitHub URL. Set:
   - **Project name**: `PROJECT_NAME` (controls the `.pages.dev` subdomain)
   - **Production branch**: `main`
   - **Framework preset**: None
   - **Build command**: empty
   - **Build output directory**: `/`
5. **Confirm with the recipient before clicking "Save and Deploy"** — this
   creates real infrastructure. The first deploy will likely fail/blank
   because D1 and env vars aren't set yet; that's expected.

### Step 6 — Bind the D1 database

In the project: **Settings → Bindings → Add → D1 database**.
- **Variable name**: `DB` (exactly — the code reads `env.DB`)
- **D1 database**: `${PROJECT_NAME}-db`
- **Apply to**: Production (repeat for Preview if they use preview deploys)
Save. Re-snapshot to confirm the binding row appears.

### Step 7 — Add environment variables

**Settings → Environment variables → Add variable**, under **Production**.
Add each row from the checklist. For the secret rows, toggle **Encrypt**
before saving.

Required:
- `META_PIXEL_ID` (plain) — from `browser-meta-capi`.
- `META_ACCESS_TOKEN` (🔒) — **switch to the Meta tab** (`browser_tabs` /
  `browser_navigate` back to the Events Manager tab), read the token field,
  switch back to the Cloudflare tab, and `browser_type` it into the value
  field. It never enters chat. Toggle Encrypt. Save.
- `DASH_KEY` (🔒) — type the value generated in deploy-stack Step 6.

Optional (only the ones the recipient asked for): `META_TEST_EVENT_CODE`,
`TIMEZONE_OFFSET`, `DEFAULT_COUNTRY_CODE`, `GA4_MEASUREMENT_ID` +
`GA4_API_SECRET` (🔒), the six `GOOGLE_ADS_*` (secrets 🔒),
`ENCHARGE_API_KEY` (🔒), `MANYCHAT_KEY` (🔒), `SYNC_SECRET` (🔒) +
`META_ADS_ACCESS_TOKEN` (🔒) + `META_ADS_ACCOUNT_ID`, and the webhook slugs
`EDUZZ_WEBHOOK_SLUG` / `HOTMART_WEBHOOK_SLUG` / `KIWIFY_WEBHOOK_SLUG` (🔒).

Re-snapshot and confirm each variable name appears in the list (values for
encrypted ones will be masked — that's correct).

### Step 8 — Trigger a redeploy

Env-var and binding changes don't apply to live deployments. Go to the
**Deployments** tab → most recent deployment → **Retry deployment** (or push
any commit to `main`). Wait ~1-2 min for the status to turn green. Confirm
`https://${PROJECT_NAME}.pages.dev` responds.

## INSTRUCT mode

Hand the recipient deploy-stack's Steps 8-11 text directly, one step at a
time, waiting for confirmation between each. The env-var checklist table
(deploy-stack Step 10) lists every variable, where to get it, and which to
encrypt. Remind them: paste the Meta CAPI token themselves; don't send it to
you.

## Failure / drift

If the Cloudflare dashboard layout has moved (Pages creation flow and
Settings nav change periodically), fall back to INSTRUCT for the affected
step and note the drift so `playbook/cloudflare-dashboard.md` can be updated.

## Common fixes (from deploy-stack troubleshooting)

- `/dash/?key=…` returns 401 → `DASH_KEY` pasted with a trailing
  space/newline. Re-enter carefully.
- Pages return blank/404 → Build output directory wasn't `/`. Fix in
  Settings → Builds.
- `sessions` table empty after a visit → D1 binding name isn't exactly `DB`.
  Re-check Settings → Bindings, then redeploy.
