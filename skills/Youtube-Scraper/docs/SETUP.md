# Setup & Troubleshooting

The fastest path is the built-in **`setup` skill** — it does everything below
for you, automatically, on any OS.

## Recommended: the automatic setup

1. Install **Claude Code** — https://claude.com/claude-code
2. Unzip this folder, open a terminal in it, and run `claude`.
3. Type `/setup` and let it work.

`/setup` detects your OS, checks for Node.js and the Playwright browser, and
**installs whatever is missing** — with cascading fallbacks (Homebrew, winget,
nvm, portable Node…) and patient, step-by-step help if it needs your system
password. It finishes with a functional test so you know the browser works.

When `/setup` asks you to restart the session, do exactly that: type `/quit`,
then `claude` again. Claude Code only loads the browser tool at startup.

## What `/setup` installs

- **Node.js 18+** — runs the browser automation.
- **Playwright (Chromium) browser** — what the agent uses to view YouTube.
- On Linux, the system libraries Chromium needs.

The Playwright MCP server itself is already registered by the `.mcp.json` file
shipped in this repo — no action needed.

## Verifying your setup any time

Run the health check from the repo root:

```bash
# macOS / Linux / WSL / Git Bash
bash scripts/healthcheck.sh
```
```powershell
# Windows
powershell -File scripts\healthcheck.ps1
```

It reports Node.js, npx, `.mcp.json`, the Playwright browser, and the skill.

## Manual setup (only if you prefer)

1. Install Node.js 18+ from https://nodejs.org (`node --version` to check).
2. Open the folder in Claude Code; approve the `playwright` MCP server when
   asked (or run `/mcp` to enable it).
3. Pre-install the browser: `npx playwright install chromium`.
4. Restart Claude Code (`/quit`, then `claude`).

## Troubleshooting

**"The browser tool is not available" / `/mcp` doesn't show playwright**
Run `/setup` — it diagnoses and fixes this. Or run `/mcp` and enable the
`playwright` server manually.

**Setup needs my password**
That's normal when installing Node.js system-wide. The agent explains exactly
what you'll see and what to type. Nothing shows on screen while you type a
password — that's a security feature, not a bug.

**Corporate / school network**
Firewalls often block the browser download or npm. Try a home connection, or
ask IT to allow `registry.npmjs.org` and the Playwright download. `/setup`
detects proxies and will tell you what's blocked.

**YouTube shows a cookie/consent wall**
The agent dismisses it automatically. If it gets stuck, tell it: "aceite o
aviso de cookies do YouTube e continue."

**Thumbnails are blank in the report**
YouTube lazy-loads images; the skill polls for each one before screenshotting.
If a few are still blank, ask the agent to re-capture them.

**The report didn't open automatically**
Open `reports/youtube-report-<niche>.html` manually in any browser.

## Where reports are saved

Reports are written to the `reports/` folder inside this repository — the agent
keeps everything self-contained, so nothing is written outside the project.
Each report is a single `youtube-report-<niche>.html` file you can move, email,
or host anywhere afterwards.
