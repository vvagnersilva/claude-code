# Tracking Setup Guide

Go from **zero to working server-side tracking** — guided by Claude Code,
which can either **tell you what to click** or **do the browser steps for
you**.

This repo wraps a complete self-hosted tracking stack (Meta Conversions API +
GA4 + Google Ads, first-party attribution, a built-in dashboard — all running
in *your own* Cloudflare account, no monthly SaaS) and adds an onboarding
layer that walks you through deploying it and proves it works at the end.

## How it's organized

| Path | What it is |
|---|---|
| `stack/` | The deployable tracking stack (Cloudflare Pages + D1). This is what gets pushed to your GitHub and deployed. Its own `README.md` and `docs/` explain the internals. |
| `.claude/skills/` | The guided-setup skills that drive the onboarding (this repo's value-add). |
| `playbook/` | Browser selector / layout references the skills use to click through Meta, Cloudflare, and sales-platform dashboards. |
| `CLAUDE.md` | The instructions Claude Code reads when you open this folder. |

## What you need before you start

- A **Cloudflare account** (free tier is fine).
- A **GitHub account** with the `gh` CLI installed and authenticated
  (`gh auth login`).
- **Node.js** (so `npx wrangler@latest` works).
- **Claude Code** installed — this whole thing is driven from it.
- A **Meta Business Manager** with a Pixel (or willingness to create one).
- If you'll run a sales page: an **Eduzz, Hotmart, or Kiwify** account.

## How to use it

1. Open this folder in **Claude Code**.
2. Say: **"set up my tracking."** Claude Code runs the `guided-setup` skill.
3. It asks one question first: do you want it to **walk you through each step**
   (you click) or **drive the browser for you** (Playwright)? Either way you
   log into your own accounts and approve anything permanent.
4. It then goes through the journey in order:
   1. Meta Pixel + Conversions API token
   2. Cloudflare database + migrations
   3. Your dashboard key + webhook slugs
   4. Push the stack to a private GitHub repo
   5–8. Cloudflare Pages project, database binding, settings, deploy
   9. Add your first lead form or sales page
   10. Connect your sales-platform webhook
   11. **Verify the whole chain on a real visit**
5. At the end it visits your live page itself, checks every link in the
   chain, and tells you when you're clear to run paid traffic.

You can also ask for just one piece: *"do the Meta part,"* *"set up
Cloudflare,"* *"connect my Hotmart webhook,"* or *"is my tracking working?"*

## Two modes, in plain terms

- **INSTRUCT** — Claude tells you exactly what to click, one step at a time.
  You stay in control of every dashboard.
- **EXECUTE** — Claude opens a browser and does the clicking for you. It still
  pauses for you to log in and to approve anything it can't undo. Your
  passwords and secret tokens are never shown in the chat or saved to any
  file.

## A note on security

Your access tokens and secrets go straight into Cloudflare's **encrypted**
settings. In EXECUTE mode they move directly from one browser tab to another
without ever appearing in the chat or being written to disk. Nothing
sensitive is committed to git — `wrangler.toml`, `.dev.vars`, and `.env*` are
all ignored.

## License

MIT — see [`LICENSE`](LICENSE). Free to use, modify, and redistribute.
