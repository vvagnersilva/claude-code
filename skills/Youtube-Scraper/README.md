# 📊 YouTube Market Research Agent

A ready-to-use **Claude Code** agent that turns any niche keyword into a
beautiful, interactive HTML report of the top-performing YouTube videos —
this month and this week — with embedded thumbnails, real view counts, and a
"views vs channel average" performance score.

Drop this folder into Claude Code, name a niche, and get a shareable report.
It even **sets up your machine for you** — including installing what's missing.

> The agent talks to you in **Brazilian Portuguese**; this documentation is in
> English.

---

## ✨ What you get

For any keyword (in **any language**), the agent produces a single
self-contained `youtube-report-<niche>.html` file with:

- **📅 Top 30 — This Month** and **🔥 Top 15 — This Week** sections.
- Horizontal video cards: embedded thumbnail, title, channel, and metrics.
- **Absolute view counts** with thousands separators.
- **Performance score** — each video's views ÷ its channel's recent average,
  color-coded (a video doing 3× its channel's norm is a real signal).
- **Interactive ranking** — toggle each section between *Most viewed* and
  *Best performance*; cards reorder and rank badges renumber live.
- **⬇ Download thumbnail** and **🔗 Copy link** buttons on every card.
- A clean dark theme and a summary stat strip. No internet needed to open it.

---

## 🚀 Quick start

### 1. Install Claude Code

Get it at https://claude.com/claude-code. That is the **only** thing you must
install yourself — the agent installs everything else.

### 2. Open this folder in Claude Code

Unzip the folder, then:

```bash
cd Youtube-Scraper
claude
```

### 3. Run setup (first time only)

In Claude Code, type:

```
/setup
```

The agent checks your machine and **installs whatever is missing** — Node.js and
the Playwright browser — with step-by-step help if it needs your password. It
works on macOS, Windows and Linux, even from a completely fresh machine. It ends
with a quick test so you know it works.

> When prompted, **restart the session** (`/quit`, then `claude`) so the browser
> tool loads. Setup tells you exactly when and how.

### 4. Research a niche

Tell the agent what to research:

```
/youtube-niche-research arquitetura
```

It browses YouTube, collects and ranks videos, screenshots thumbnails, computes
performance scores, builds the report, and opens it in your browser. The report
lands in [reports/](reports/).

---

## ✅ Requirements & known limitations

**You need:**

- **Claude Code** — the runtime.
- **An internet connection** — the agent browses live YouTube.
- Everything else (Node.js 18+, the Playwright browser) is installed by `/setup`.

**Good to know:**

- **First run is slower** — `/setup` downloads a browser (~150–300 MB), one time.
- **Corporate / locked-down networks** may block the browser download or show
  CAPTCHAs. A normal home connection is the smoothest experience.
- **EU users** may see a YouTube cookie-consent screen — the agent dismisses it
  automatically.
- **YouTube changes its site** occasionally; if a run extracts fewer videos than
  expected, just run it again or report it.
- Run [`scripts/healthcheck.sh`](scripts/healthcheck.sh) (macOS/Linux) or
  [`scripts/healthcheck.ps1`](scripts/healthcheck.ps1) (Windows) any time to
  verify your setup.

If anything fails, just tell the agent — `/setup` is built to diagnose and fix
it. Full troubleshooting is in [docs/SETUP.md](docs/SETUP.md).

---

## 📁 What's inside

```
Youtube-Scraper/
├── README.md                  ← you are here
├── CLAUDE.md                  ← project context for the agent
├── .mcp.json                  ← registers the Playwright browser tool
├── .claude/
│   ├── settings.json          ← auto-enables the tool, pre-approves permissions
│   └── skills/
│       ├── setup/             ← installs & verifies the environment
│       └── youtube-niche-research/
│           ├── SKILL.md       ← the research workflow
│           ├── reference.md   ← YouTube filter codes & parsing rules
│           ├── scripts/       ← browser extraction snippets
│           └── assets/        ← the HTML report template
├── scripts/                   ← healthcheck.sh / healthcheck.ps1
├── docs/SETUP.md              ← detailed setup & troubleshooting
└── reports/                   ← your generated reports land here
```

---

## 💡 Tips

- Works with niches in any language: `"arquitetura"`, `"cocina italiana"`,
  `"woodworking"`, `"finanças pessoais"`…
- The **performance score** is the most useful column for spotting opportunity:
  a small channel with a 5× video is showing you a winning topic.
- "Channel average" is an estimate from a 12-video sample — a directional
  signal, not an official YouTube metric.
- Reports are fully self-contained `.html` files — email them, host them, or
  open them offline.

---

## 🔒 Notes

This tool only reads **public** YouTube search and channel pages, the same data
any visitor sees. It does not log in or use the YouTube API. Use it responsibly
and within YouTube's Terms of Service.

## 📄 License

MIT — see [LICENSE](LICENSE). Share it freely with your community.
