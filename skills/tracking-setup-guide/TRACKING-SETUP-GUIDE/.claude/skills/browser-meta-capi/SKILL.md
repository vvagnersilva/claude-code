---
name: browser-meta-capi
description: Drives Meta Events Manager via the Playwright MCP to confirm or create a Pixel, generate a Conversions API (CAPI) access token, and capture the Pixel ID (and optional Test Event Code). Use when the recipient says "do the Meta part", "create my CAPI token", "set up my pixel", "get my conversions API token", or as Step 1 of guided-setup. Has an INSTRUCT fallback that tells the recipient exactly what to click. The CAPI token is a secret — it is never echoed to chat or written to disk; it stays in the browser tab until browser-cloudflare-pages moves it into Cloudflare's encrypted env vars.
---

# Skill: browser-meta-capi

Goal: end with three things in hand for the env-var step —
`META_PIXEL_ID` (numeric, not secret), `META_ACCESS_TOKEN` (CAPI token,
**secret**), and optionally `META_TEST_EVENT_CODE`.

**Mode**: `guided-setup` passes EXECUTE or INSTRUCT. If invoked directly, ask.

## Security guardrail (read before touching the token)

The CAPI access token grants conversion-sending rights to the recipient's ad
account. Treat it like a password:

- **Never print it to chat. Never write it to a file. Never include it in a
  command you run.**
- In EXECUTE mode, once you generate it, **leave it in the Meta browser tab**.
  `browser-cloudflare-pages` will read it from that tab and type it directly
  into the Cloudflare encrypted env-var field. The token travels
  tab→tab and never enters your text output.
- If at any point you cannot avoid surfacing the token in text, **switch to
  INSTRUCT** and have the recipient copy it into their password manager and
  paste it into Cloudflare themselves.

## EXECUTE mode

### 1. Open Events Manager

`browser_navigate` to `https://business.facebook.com/events_manager2/`.
`browser_snapshot`. If a login/2FA wall appears, **stop**: tell the recipient
"Please log into Facebook/Meta in the browser window, then tell me when
you're in." Resume only after they confirm. You never type their password.

### 2. Select or create the Pixel (data source)

From the snapshot, find the data-sources list. If they already have a Pixel,
click it. If not, click **Connect data → Web** and create one named
for their brand. Re-snapshot after each navigation (refs go stale).

### 3. Capture the Pixel ID

The numeric Pixel ID sits at the top of the data source's page (and in
Settings). Read it from the snapshot. This is **not** a secret — keep it in
context as `META_PIXEL_ID` for the env-var step.

### 4. Generate the CAPI access token

Go to the Pixel's **Settings** tab. Scroll to **Conversions API → Generate
access token** (sometimes under "Set up manually" / "Generate access token").
Click it. Meta reveals a long token string.

**Do not read the token into your chat output.** Confirm only that a token
was generated (the field is now populated). Leave the tab open and the token
visible in the field so the Cloudflare step can lift it.

If Meta only shows the token once and the UI forces a copy, in EXECUTE mode
you may use `browser_evaluate` to read it into a Playwright variable and
immediately hand it to `browser-cloudflare-pages` for typing — but it must
never be returned as text to the user. If that handoff isn't possible in one
session, switch to INSTRUCT for the token only.

### 5. (Optional) Test Event Code

If the recipient wants test events isolated, open the **Test Events** tab.
The code (e.g. `TEST12345`) is shown there. It's low-sensitivity; you may
keep it as `META_TEST_EVENT_CODE`.

### 6. Report (names only)

Tell the recipient: "Pixel confirmed (ID captured), Conversions API token
generated and held for the Cloudflare step." Never the token value.

## INSTRUCT mode

Walk them through, one step at a time, waiting for "done" between each:

1. Go to **business.facebook.com/events_manager2** and log in.
2. Pick your Pixel in the left list (or **Connect data → Web** to create one).
3. Copy the **numeric Pixel ID** from the top of the page and paste it to me
   (safe to share — it's public).
4. Open the Pixel's **Settings** tab → **Conversions API** → **Generate
   access token**. Copy the token straight into your password manager. **Do
   not paste it to me** — you'll paste it into Cloudflare yourself in a later
   step.
5. (Optional) **Test Events** tab → copy the test code if you want a separate
   test pipeline.

## Failure / drift

If the Events Manager layout has changed and you can't find "Generate access
token" from the snapshot, fall back to INSTRUCT and note the UI drift in your
report so `playbook/meta-events-manager.md` can be updated.
