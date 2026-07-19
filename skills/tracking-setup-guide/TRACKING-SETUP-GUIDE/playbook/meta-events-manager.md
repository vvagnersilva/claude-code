# Meta Events Manager — navigation reference

Used by `browser-meta-capi`. Navigation only — never record token values here.

## URLs

- Events Manager: `https://business.facebook.com/events_manager2/`
- Direct data-sources list: `https://business.facebook.com/events_manager2/list/dataset`

## Login / hand-off

A login or 2FA wall means **hand control back to the recipient** — they type
their own credentials. Resume only after they confirm they're in. Never type
a Meta password.

## Path: select or create the Pixel (data source)

1. Left rail → **Data sources**. Existing Pixels are listed; click the one
   the recipient wants.
2. To create: **Connect data** → **Web** → follow the dialog, name it for the
   brand, choose **Conversions API and Meta Pixel** when asked about setup
   method.

## Path: capture the Pixel ID (not a secret)

The numeric ID is shown at the top of the data source overview and under
**Settings** near "Dataset ID" / "Pixel ID". Read it from the snapshot.

## Path: generate the CAPI access token (SECRET)

1. Open the Pixel → **Settings** tab.
2. Scroll to **Conversions API** → **Generate access token** (sometimes under
   "Set up manually" or behind a "Manage integrations" / "..." menu).
3. Clicking reveals the token. **Do not read it into chat.** Leave it in the
   field for the tab-to-tab handoff to Cloudflare, or have the recipient copy
   it to their password manager (INSTRUCT).

## Path: Test Event Code (low sensitivity)

Pixel → **Test Events** tab → the code (e.g. `TEST12345`) is displayed top of
page. Safe to keep as `META_TEST_EVENT_CODE`.

## Known drift points

- Meta periodically moves "Generate access token" between the Settings tab
  and a "Manage" sub-dialog. If absent from the snapshot, expand any
  collapsed "Conversions API" section first; if still absent, fall back to
  INSTRUCT.
- Business vs personal accounts land on different default URLs; if the
  Business URL redirects to a chooser, hand off and let the recipient pick the
  right business.
