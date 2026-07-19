---
name: check-tracking
description: Confirms the deployed tracking stack actually works end-to-end. Use when the recipient says "is my tracking working", "check it", "verify the chain", "test it", "did the setup work", "why aren't my events firing", or as Step 11 of guided-setup. Combines the stack's 6-checkpoint D1 integrity chain (verify-tracking) with a LIVE Playwright MCP browser visit that generates real traffic, so you can prove the cookie→session→event chain fires on a real page load instead of waiting for the recipient to visit manually. Reports PASS / FAIL / SKIPPED per checkpoint with specific evidence.
---

# Skill: check-tracking

This skill proves the stack works. It does two things the stack's own
`verify-tracking` skill can't do alone:

1. It can **generate the traffic itself** via the Playwright MCP — visit the
   live page, submit the lead form — so verification doesn't stall waiting for
   the recipient to "go visit your page."
2. It then runs the **6-checkpoint D1 integrity chain** from
   `stack/.claude/skills/verify-tracking` against that fresh traffic.

## Prerequisites

You need (ask if not already in context):
- `SITE_URL` — the deployed Pages URL (`https://${PROJECT_NAME}.pages.dev`).
- `PROJECT_NAME` and `DB_NAME` (`${PROJECT_NAME}-db`) for wrangler queries.
- At least one live page (lead form or sales page) from `add-page`.
- For sales-page checkpoints: which `PLATFORM` (eduzz/hotmart/kiwify).

If nothing is deployed yet, stop and send them to `guided-setup`.

## Phase 1 — Generate live traffic (Playwright MCP)

This is the value-add over plain `verify-tracking`. Drive a real visit:

1. `browser_navigate` to
   `${SITE_URL}/?utm_source=verify&utm_medium=check-tracking&utm_campaign=setup-test`.
   The UTMs let Checkpoint 1 prove UTM capture, not just session creation.
2. `browser_snapshot`. Confirm the page rendered (you should see the lead
   form or sales-page content, not a Cloudflare error or blank body). A blank
   page here usually means the Build output directory wasn't `/` or the
   deploy is still building.
3. If it's a **lead form**: fill the email field with a clearly-marked test
   address (e.g. `verify+<timestamp>@example.com`) via `browser_fill_form` /
   `browser_type`, then submit. Watch for the network POST to `/tracker`
   (use `browser_network_requests` to confirm a 200). This creates the `Lead`
   event for Checkpoint 2.
4. If it's a **sales page**: the page should auto-POST to `/checkout-session`
   on load. Confirm via `browser_network_requests`. Then click the checkout
   button and capture the destination URL — it must contain `?trk=`
   (Eduzz/`xcod`/`sck` per platform) for Checkpoints 3-4.

Give D1 a few seconds to settle, then move to Phase 2.

## Phase 2 — Run the 6-checkpoint D1 chain

Run the checks exactly as defined in
`stack/.claude/skills/verify-tracking/SKILL.md` — read that file for the full
PASS/FAIL/SKIPPED criteria and fix-modes for each checkpoint. In brief:

| # | Checks | Query target |
|---|---|---|
| 1 | Middleware sets `_trk_sid`, writes `sessions` with `fbp`/UTMs | `sessions` |
| 2 | `/tracker` logs the Lead/InitiateCheckout, Meta+GA4 responded ok | `event_log` |
| 3 | Sales page wrote `checkout_sessions` with a UUID `trk` | `checkout_sessions` |
| 4 | Sales platform webhook arrived with matching `trk` | `purchase_log` |
| 5 | Webhook enriched the conversion (`fbp`/`fbc`/UTMs populated) | `purchase_log` |
| 6 | Meta/GA4/Google Ads `*_response_ok = 1` | `purchase_log` |

Run each query from inside `stack/` so wrangler finds `wrangler.toml`:

```bash
cd stack && npx wrangler@latest d1 execute ${DB_NAME} --remote --command \
  "SELECT session_id, fbp, utm_source, created_at FROM sessions ORDER BY created_at DESC LIMIT 5"
```

Because Phase 1 just generated a visit with `utm_source=verify`, Checkpoint 1
should now show a fresh row with `utm_source = "verify"` — that's strong
evidence the live chain works, not just stale data.

Checkpoints 3-6 require a sales flow and a real/test purchase. If the
recipient only has a lead form, report 3-6 as `SKIPPED — no sales flow`. For
Checkpoint 4 you can also trigger the platform's "send test webhook" button
(see `browser-sales-webhook`) instead of a real purchase.

## Reporting

Give the scorecard (same format as verify-tracking) plus a note on what
traffic produced it:

```
Live visit:  ${SITE_URL}/?utm_source=verify…  →  page rendered, /tracker 200

Checkpoint 1 — Middleware → sessions          [PASS — row with utm_source=verify]
Checkpoint 2 — /tracker → event_log           [PASS / FAIL: <reason>]
Checkpoint 3 — Sales page → checkout_sessions [PASS / FAIL / SKIPPED]
Checkpoint 4 — Sales platform → webhook       [PASS / FAIL / SKIPPED]
Checkpoint 5 — Webhook enrichment             [PASS / FAIL / SKIPPED]
Checkpoint 6 — Ad platform receipt            [PASS / FAIL / SKIPPED]
```

If all are PASS or justified-SKIP: **"Your tracking is healthy — you can
start running paid traffic."** If anything FAILs, fix the earliest failing
checkpoint first (each has a fix-mode in `verify-tracking`), then re-run from
there. Never report green when a query shows otherwise.
