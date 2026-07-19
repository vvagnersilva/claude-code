# YouTube Market Research Agent

This repository turns Claude Code into an expert at **YouTube market research**.

## What this project does

Given a niche keyword, it researches YouTube and produces one interactive,
fully self-contained HTML report of the top-performing long videos this month
and this week — with embedded thumbnails, absolute view counts, and a
"views vs channel average" performance score.

## 🌐 Language protocol

Your internal reasoning and these instruction files are in English. **Everything
the end-user sees must be in Brazilian Portuguese** — setup messages, research
progress, questions, the final summary, and the generated HTML report. Technical
identifiers (commands, paths, package names) may stay English. The community
using this repo is Brazilian.

## The two skills

1. **`setup`** — first-time environment setup. Installs and verifies Node.js and
   the Playwright MCP browser, with cascading fallbacks for any OS, even on a
   machine with zero prior setup.
2. **`youtube-niche-research`** — the research workflow that produces the report.

## How to run it

- **First time on a machine:** run the `setup` skill (`/setup`). It installs
  everything and ends with a quick functional test.
- **To research a niche:** tell Claude the niche, e.g. *"pesquise o nicho do
  YouTube 'arquitetura'"*, or `/youtube-niche-research arquitetura`.

The `youtube-niche-research` skill runs a **preflight** first: if the Playwright
browser tools are missing, it routes the user to the `setup` skill instead of
failing. Never fall back to scraping YouTube with `curl`/`fetch`.

## Repo layout

- `.claude/skills/setup/` — environment setup skill (`SKILL.md` +
  `install-commands.md`).
- `.claude/skills/youtube-niche-research/` — research skill: `SKILL.md` workflow,
  `reference.md`, `scripts/*.js` browser snippets, `assets/report-template.html`.
- `.mcp.json` — registers the Playwright MCP browser server.
- `.claude/settings.json` — auto-enables the MCP server and pre-allows its tools.
- `scripts/healthcheck.sh` / `.ps1` — standalone environment health check.
- `reports/` — default output folder for generated reports (inside the repo).
- `docs/SETUP.md` — setup instructions for new users.

## Working rules for the agent

- The research skill **requires** the Playwright MCP browser tools
  (`mcp__playwright__*`). If they are unavailable, run the `setup` skill — do not
  scrape YouTube with `curl`/`fetch`.
- Always parse view counts yourself and sort in code; never trust YouTube's
  on-page ordering.
- Keep the final HTML report 100% self-contained (inline CSS/JS, base64
  thumbnails) — it must work when opened with no internet and no sibling files.
- This repository is fully self-sufficient: never read, write, or reference any
  file or folder outside the repo. Save all reports inside `reports/`.
