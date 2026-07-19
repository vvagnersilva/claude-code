---
name: browser-sales-webhook
description: Drives the Eduzz, Hotmart, or Kiwify dashboard via the Playwright MCP to register the stack's webhook URL so completed purchases POST back to the tracking stack. Use when the recipient says "connect my webhook", "set up my Eduzz/Hotmart/Kiwify webhook", "register the purchase callback", or as Step 10 of guided-setup. Has an INSTRUCT fallback. Requires the platform name and the full webhook URL (https://PROJECT_NAME.pages.dev/webhook/<platform>/<slug>). The slug is the only thing gating the endpoint, so treat the URL as a secret.
---

# Skill: browser-sales-webhook

Goal: the sales platform fires a webhook to
`https://${PROJECT_NAME}.pages.dev/webhook/<platform>/<slug>` on every
completed purchase, AND forwards the `trk` custom field so the stack can
match the purchase to its originating session.

Inputs from `guided-setup`: `PLATFORM` (`eduzz` | `hotmart` | `kiwify`) and
the full webhook URL (slug included).

**Mode**: EXECUTE or INSTRUCT.

## Security guardrail

The webhook URL contains the per-recipient UUID slug — it is the only thing
standing between a public endpoint and arbitrary fake-purchase injection.
**Treat the full URL as a secret**: never paste it into chat output, never
write it to a file. In EXECUTE mode type it directly into the platform's
field; in INSTRUCT mode the recipient already has it from their password
manager (deploy-stack Step 10 told them to save it there).

## Per-platform field that carries `trk`

The stack reads the tracker from a platform-specific custom field. Confirm
the recipient's sales page passes `trk` into the right checkout parameter
(see `stack/docs/platforms/<platform>.md`):

| Platform | Webhook config location | Custom field the stack reads | Checkout URL param |
|---|---|---|---|
| Eduzz | Ferramentas → Webhooks / Notificações (My Eduzz → integrations) | `tracker.code1` | `?trk=<uuid>` |
| Hotmart | Ferramentas → Webhook (Postback) | `xcod` (top-level or `offer.xcod`) | `?xcod=<uuid>` |
| Kiwify | Apps / Configurações → Webhooks | `sck` | `?sck=<uuid>` |

Read `stack/docs/platforms/<platform>.md` for the exact payload spot before
configuring — each platform has gotchas.

## EXECUTE mode

1. `browser_navigate` to the platform dashboard
   (`app.eduzz.com`, `app-vlc.hotmart.com`, or `dashboard.kiwify.com.br`).
   `browser_snapshot`. Login wall → **hand off**, resume after they confirm.
2. Navigate to the webhook/postback configuration section (see table). Re-
   snapshot.
3. Create a new webhook. Paste the full webhook URL into the endpoint field
   via `browser_type` (do not surface it in chat). Select the purchase /
   "compra aprovada" / "order paid" event so it fires on completed sales.
4. Save. Re-snapshot to confirm the webhook row was created.
5. If the platform offers a **"send test webhook"** button, trigger it — then
   the recipient can run `check-tracking` Checkpoint 4 to confirm the row
   landed in `purchase_log`.

## INSTRUCT mode

Walk them through, one step at a time:

1. Log into your `PLATFORM` dashboard.
2. Go to the webhook/postback section (Eduzz: Ferramentas → Webhooks;
   Hotmart: Ferramentas → Webhook/Postback; Kiwify: Configurações →
   Webhooks).
3. Add a new webhook. Paste **your** saved webhook URL (the one with the long
   slug from your password manager) into the URL field.
4. Choose the **purchase approved / order paid** event.
5. Save. If there's a "test webhook" button, click it.

## Verify

After configuring, point the recipient to `check-tracking` Checkpoint 4 (a
real or test purchase should produce a `purchase_log` row with a matching
`trk`). Don't claim the webhook works until that row exists.

## Failure / drift

If the platform dashboard has moved its webhook settings, fall back to
INSTRUCT and note the drift so `playbook/sales-platforms.md` can be updated.
Per-platform signature verification (HMAC/hottok) is deliberately deferred to
the stack's post-launch `harden-tracking` step — do not block setup on it.
