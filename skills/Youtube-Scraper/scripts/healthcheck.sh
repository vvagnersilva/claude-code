#!/usr/bin/env bash
# Health check for the YouTube Market Research Agent.
# Run from the repository root:  bash scripts/healthcheck.sh
# macOS / Linux / WSL / Git Bash.

cd "$(dirname "$0")/.." || exit 1
echo "=== YouTube Market Research Agent — Health Check ==="

ok=1

node_v=$(node --version 2>/dev/null)
if [ -n "$node_v" ]; then echo "✅ Node.js: $node_v"
else echo "❌ Node.js: NOT FOUND — run /setup in Claude Code"; ok=0; fi

npx_v=$(npx --version 2>/dev/null)
[ -n "$npx_v" ] && echo "✅ npx: $npx_v" || { echo "❌ npx: NOT FOUND"; ok=0; }

if [ -f .mcp.json ] && node -e "JSON.parse(require('fs').readFileSync('.mcp.json'))" 2>/dev/null; then
  echo "✅ .mcp.json: present and valid"
else
  echo "❌ .mcp.json: missing or invalid"; ok=0
fi

pw_v=$(npx playwright --version 2>/dev/null)
if [ -n "$pw_v" ]; then echo "✅ Playwright: $pw_v"
else echo "⚠️  Playwright browser not installed yet — /setup installs it on first run"; fi

if [ -d .claude/skills/youtube-niche-research ]; then echo "✅ Research skill: present"
else echo "❌ Research skill: missing"; ok=0; fi

echo "---"
if [ "$ok" -eq 1 ]; then
  echo "All core checks passed. In Claude Code run:  /youtube-niche-research <niche>"
else
  echo "Some checks failed. Open this folder in Claude Code and run:  /setup"
fi
