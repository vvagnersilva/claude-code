# Install Commands — per-OS reference

Detailed commands for Phase 2 (install Node.js), Phase 3 (Windows MCP fix),
Phase 4 (browser), Phase 5 (Linux deps), plus the common-errors table.
Internal reference — keep user-facing output in Portuguese.

## Network pre-flight (Phase 0)

```bash
# macOS / Linux / WSL / Git Bash
for h in registry.npmjs.org nodejs.org raw.githubusercontent.com; do
  curl -fsS -o /dev/null --max-time 5 "https://$h" && echo "$h OK" || echo "$h FAIL"
done
```
```powershell
# Windows PowerShell
@('registry.npmjs.org','nodejs.org','raw.githubusercontent.com') | ForEach-Object {
  try { Invoke-WebRequest "https://$_" -TimeoutSec 5 -UseBasicParsing | Out-Null; "$_ OK" }
  catch { "$_ FAIL" } }
```
If a host fails, check `HTTP_PROXY`/`HTTPS_PROXY`/`ALL_PROXY`. With a proxy set:
`npm config set proxy "$HTTP_PROXY"` and `npm config set https-proxy "$HTTPS_PROXY"`.
No proxy + failures → corporate firewall; inform the user.

---

## PHASE 2 — Install Node.js

### macOS

**A1 · Homebrew already installed**
```bash
command -v brew && brew install node
# refresh PATH in the current shell:
[ -d /opt/homebrew/bin ] && eval "$(/opt/homebrew/bin/brew shellenv)"   # Apple Silicon
[ -d /usr/local/bin ]   && eval "$(/usr/local/bin/brew shellenv)"       # Intel
hash -r && node --version
```

**A2 · Install Homebrew + Node** (needs the macOS login password once — use 👋
PATIENT HELP, say "~5 minutos"):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
if [ -d /opt/homebrew/bin ]; then eval "$(/opt/homebrew/bin/brew shellenv)";
  else eval "$(/usr/local/bin/brew shellenv)"; fi
brew install node && hash -r && node --version
```

**A3 · nvm** (fallback, no password):
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install --lts && nvm use --lts && hash -r && node --version
```

**A4 · Manual** (last resort): 👋 PATIENT HELP — guide the user to
https://nodejs.org/, download the LTS `.pkg`, click through the installer, then
`/quit` + `claude` and resume from Phase 1.

### Windows

**B1 · winget** (Windows 10 1809+/11) — explain the UAC popup with 👋 PATIENT
HELP ("uma janela azul/amarela vai aparecer, clique em Sim"):
```powershell
winget install -e --id OpenJS.NodeJS.LTS --silent --accept-source-agreements --accept-package-agreements
# refresh PATH (current session won't see Node otherwise):
$env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
            [Environment]::GetEnvironmentVariable("Path","User")
node --version
```

**B2 · Portable Node — PREFERRED when the user lacks admin** (no UAC, no admin):
```powershell
$lts = (Invoke-RestMethod "https://nodejs.org/dist/index.json" -TimeoutSec 10) |
        Where-Object { $_.lts } | Select-Object -First 1
$v = $lts.version.TrimStart('v')
$arch = if ([Environment]::Is64BitOperatingSystem) {"x64"} else {"x86"}
$zip = "node-v$v-win-$arch.zip"
$dest = "$env:USERPROFILE\nodejs-portable"
Invoke-WebRequest "https://nodejs.org/dist/v$v/$zip" -OutFile "$env:TEMP\$zip" -TimeoutSec 60
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
Expand-Archive "$env:TEMP\$zip" -DestinationPath $dest -Force
$nodeDir = (Get-ChildItem $dest -Directory | Select-Object -First 1).FullName
$env:Path = "$nodeDir;$env:Path"
$userPath = [Environment]::GetEnvironmentVariable("Path","User")
if ($userPath -notlike "*$nodeDir*") {
  [Environment]::SetEnvironmentVariable("Path","$nodeDir;$userPath","User") }
node --version; npm --version
```

**B3 · Manual** (last resort): 👋 PATIENT HELP — guide to nodejs.org `.msi`,
click through (UAC popup), then `/quit` + `claude` and resume.

### Linux / WSL

**C1 · nvm** (preferred, no sudo):
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install --lts && nvm use --lts && hash -r && node --version
```
**C2 · apt** (Debian/Ubuntu, needs sudo — use 🔔 QUICK APPROVAL):
`sudo apt-get update && sudo apt-get install -y nodejs npm` (if the distro's
Node is < 18, prefer C1 / NodeSource).

### Post-install — if `node --version` still fails

1. Try absolute paths: macOS brew arm64 `/opt/homebrew/bin/node`, Intel
   `/usr/local/bin/node`, nvm `~/.nvm/versions/node/*/bin/node`, Windows winget
   `C:\Program Files\nodejs\node.exe`, portable
   `$env:USERPROFILE\nodejs-portable\*\node.exe`.
2. Absolute path works but bare `node` doesn't → PATH not refreshed: re-run the
   refresh block, `hash -r`.
3. Absolute path also fails → install failed; try the next method.
4. All exhausted → 👋 PATIENT HELP: `/quit`, `claude`, paste the setup prompt
   again — the state file resumes from Phase 2.

---

## PHASE 3 — Windows-native MCP fix

The repo's `.mcp.json` uses `npx`, which works on macOS/Linux/WSL/Git Bash. On
**Windows native** (PowerShell/cmd) the npx stdio wrapper can break the MCP
connection. If so, install the package locally and rewrite `.mcp.json`:
```powershell
npm install --save-dev @playwright/mcp@latest
$cli = (Resolve-Path .\node_modules\@playwright\mcp\cli.js).Path -replace '\\','/'
```
`.mcp.json` (node-direct form):
```json
{ "mcpServers": { "playwright": {
  "type": "stdio", "command": "node",
  "args": ["C:/absolute/path/to/node_modules/@playwright/mcp/cli.js"] } } }
```

If `.mcp.json` is missing entirely, recreate the default (npx) form:
```json
{ "mcpServers": { "playwright": {
  "command": "npx", "args": ["-y", "@playwright/mcp@latest"] } } }
```

---

## PHASE 4 — Browser binary

```bash
npx playwright install chromium      # ~150–300 MB
npx playwright --version             # verify
```
Disk pre-check: macOS/Linux `df -h ~ | tail -1`; Windows
`(Get-PSDrive (Get-Location).Drive.Name).Free/1GB`.

## PHASE 5 — Linux system deps

```bash
sudo npx playwright install-deps     # user runs this in a separate terminal
```

---

## 🚨 Common errors

| Symptom | Cause | Fix |
|---|---|---|
| `node: command not found` after install | PATH not refreshed | Re-run PATH refresh; `hash -r`; last resort `/quit`+`claude` |
| MCP listed but "failed to connect" on Windows | `npx.cmd` breaks stdio | Apply the Phase 3 node-direct fix |
| `performance is not defined` at start | Node < 18 | Reinstall Node 20 LTS (Phase 2) |
| Browser won't open, `libnss3`/`libatk` errors (Linux) | Missing system deps | `sudo npx playwright install-deps` |
| `Cannot find package @playwright/mcp` | npm fetch failed | `npm cache clean --force`; check proxy |
| Claude answers without opening a browser | Used Bash instead of MCP | Literally say "use o playwright mcp" in the prompt |
| `EACCES` downloading the browser | Cache permissions | `sudo chown -R $USER ~/.npm ~/.cache/ms-playwright` |
| winget "Package not found" | Stale source | `winget source reset --force; winget source update` |
| Brew "shell integration" error | Apple Silicon PATH not set | `eval "$(/opt/homebrew/bin/brew shellenv)"` |
| `.mcp.json` ignored | Wrong directory | Must be at the repo root |
| PowerShell "running scripts is disabled" | Execution Policy Restricted | `Set-ExecutionPolicy -Scope Process Bypass` |
| Proxy intercepting npm (TLS) | Corporate MITM | Set `HTTP_PROXY`/`HTTPS_PROXY`; `npm config set proxy/https-proxy` |
| Portable download fails (TLS) on Windows | Corporate TLS interception | Try winget; else manual via browser |
| `claude mcp` command unknown | Claude Code too old | Update Claude Code |
| State file corrupt | Bad JSON | Delete `.youtube-setup-state.json` and restart |
