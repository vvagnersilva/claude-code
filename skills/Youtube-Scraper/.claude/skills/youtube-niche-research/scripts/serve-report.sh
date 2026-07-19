#!/usr/bin/env bash
# Start a tiny static HTTP server on $PORT (default 8765) serving the given
# directory, so Playwright can load the report (file:// is blocked by the
# Playwright MCP server). Idempotent: re-running kills any previous instance
# bound to the port.
#
# Usage: serve-report.sh <directory> [port]
set -euo pipefail
DIR="${1:-reports}"
PORT="${2:-8765}"

# Kill anything already bound to this port (best-effort).
if command -v lsof >/dev/null 2>&1; then
  EXISTING=$(lsof -ti ":${PORT}" 2>/dev/null || true)
  if [ -n "${EXISTING}" ]; then
    kill -9 ${EXISTING} 2>/dev/null || true
    sleep 0.3
  fi
fi

cd "${DIR}"
nohup python3 -m http.server "${PORT}" >"/tmp/yt-report-server-${PORT}.log" 2>&1 &
PID=$!
# Wait briefly for the server to bind.
for i in 1 2 3 4 5 6 7 8 9 10; do
  if curl -s -o /dev/null -w '' "http://localhost:${PORT}/" 2>/dev/null; then
    break
  fi
  sleep 0.2
done

echo "PID=${PID}"
echo "URL_BASE=http://localhost:${PORT}"
