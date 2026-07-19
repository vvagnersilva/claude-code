# Sales platforms — webhook navigation reference

Used by `browser-sales-webhook`. Navigation only — never record the webhook
URL (it contains the secret slug) here.

For payload-shape details (where each platform puts the `trk` field), read
`stack/docs/platforms/<platform>.md` — that is the authoritative source.

## Eduzz

- Dashboard: `https://app.eduzz.com/`
- Webhook config: **Ferramentas → Webhooks** (a.k.a. Notificações /
  integrations). Some accounts: **Minha Eduzz → Integrações → Webhook**.
- Event to enable: **Fatura Paga** / compra aprovada.
- Custom field the stack reads: `tracker.code1`. Sales-page checkout URL must
  carry `?trk=<uuid>`.

## Hotmart

- Dashboard: `https://app-vlc.hotmart.com/`
- Webhook config: **Ferramentas → Webhook (Postback)** →
  **Configurar / Adicionar Webhook**.
- Event to enable: **Compra aprovada** (purchase approved).
- Custom field the stack reads: `xcod` (top-level or inside `offer.xcod`).
  Checkout URL must carry `?xcod=<uuid>`.

## Kiwify

- Dashboard: `https://dashboard.kiwify.com.br/`
- Webhook config: **Apps / Configurações → Webhooks → Criar webhook**.
- Event to enable: **Compra aprovada** / order paid.
- Custom field the stack reads: `sck`. Checkout URL must carry `?sck=<uuid>`.

## Login / hand-off

Every platform login is a hand-off — the recipient types their own
credentials. Resume after they confirm.

## Test

Most platforms offer a **"send test webhook"** button next to the saved
webhook. Trigger it, then run `check-tracking` Checkpoint 4 to confirm a row
landed in `purchase_log`. Platform-native signature verification (HMAC /
Hotmart hottok) is deferred to the stack's post-launch `harden-tracking`
step — don't block setup on it.

## Known drift points

- Eduzz has two generations of dashboard ("Eduzz" vs "Minha Eduzz");
  webhook location differs between them.
- Hotmart sometimes nests Postback under **Ferramentas → Webhook** vs a
  legacy **Configurações → Postback (HotConnect)**.
