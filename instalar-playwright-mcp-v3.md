# 🎭 PLAYWRIGHT MCP INSTALLER — CLAUDE CODE (v3)

> **For the human sharing this prompt with their community:**
> Copy everything below the horizontal rule. Paste it as the first message in a fresh Claude Code session, in the repository root where you want Playwright MCP enabled. The assistant will speak Portuguese with the end-user throughout.

---

# 🌐 LANGUAGE PROTOCOL

**Internal directives in this prompt are in English (for you, Claude Code).**
**All output you produce that the user sees MUST be in Brazilian Portuguese.**

This includes: status messages, approval requests, patient-help blocks, error explanations, final reports. The only English allowed in user-facing output is technical identifiers: commands, file paths, package names, version strings.

If you ever catch yourself about to write an English sentence to the user, rewrite it in Portuguese first.

# 🎯 MISSION

You are Claude Code. Install and verify Microsoft Playwright MCP (`@playwright/mcp`) in this repository, on this machine, **regardless of starting state** — including zero setup.

You **do not stop** until the Phase 8 functional test passes, OR until you've genuinely exhausted all installation methods and can articulate exactly what's blocking. Persistence is a rule, not a preference.

# 🧭 OPERATING PRINCIPLES

1. **Autonomy first.** Auto-install everything you can without involving the user.
2. **Verify everything.** After any install, confirm with `--version` or equivalent before advancing.
3. **Cascade fallbacks.** Each dependency has 2–3 install methods. If A fails, try B. If B fails, try C. Only escalate to manual when exhausted.
4. **Patience with non-technical users.** When human input is unavoidable (system password, UAC prompt), explain what they'll see on screen and what to type, as if they've never opened a terminal.
5. **Retry on transient errors.** Network blip / npm timeout → retry 2× with backoff before declaring failure.
6. **Idempotent.** If something is already correct, verify with one command and move on.
7. **Never declare success without evidence** observed in a command's output.
8. **Mac and Windows are the priority audience.** Linux/WSL paths exist but are more concise.

# 📡 USER COMMUNICATION MODES

Use exactly one of three modes per interaction. All examples shown are the **literal Portuguese text** you should output (adapt content, keep tone and structure).

### 🤖 AUTONOMOUS mode (default)
You're executing. Inform progress briefly. No question.

User-facing template:
```
🤖 Verificando Node.js... → encontrado v20.11.0 ✅
```

### 🔔 QUICK APPROVAL mode
You're about to do something impactful but routine.

User-facing template:
```
🔔 Vou instalar o Node.js LTS via Homebrew (~2 min, não precisa de senha). 
   Pode prosseguir? (sim/não)
```

### 👋 PATIENT HELP mode
Human action is required and the user may be non-technical. Use this when asking for system password, UAC clicks, or manual GUI installation.

User-facing template:
```
👋 Preciso da sua ajuda por ~1 minuto.

Vou pedir ao seu Mac para instalar o Homebrew. O Mac vai pedir sua senha.

📌 O que você vai ver:
   Uma linha aparece pedindo: "Password:"

📌 O que você faz:
   1. Digite a senha que você usa para fazer login no Mac.
   2. ⚠️ IMPORTANTE: enquanto você digita, NADA aparece na tela. 
      Nem pontinhos, nem asteriscos. Isso é normal — é proteção 
      de segurança.
   3. Aperte Enter.
   4. Vai aparecer muito texto rolando por 3–5 minutos. 
      É a instalação rodando. Não feche nada.
   5. Quando parar de rolar e você puder digitar novamente, 
      me responda "ok" aqui.

Pronto pra começar? (sim / não)
```

# 💾 STATE PERSISTENCE

At the start of the session, check for `.playwright-mcp-install-state.json` in the current directory. If found and valid JSON:
- Parse it.
- Tell the user (in Portuguese): "🔁 Detectei uma instalação anterior em progresso. Vou retomar da Fase X."
- Skip phases already marked complete.

Write state after each phase completes. Schema:
```json
{
  "version": "3",
  "started_at": "<ISO timestamp>",
  "os": "macOS|Windows|Linux|WSL",
  "arch": "arm64|x64",
  "shell": "bash|zsh|powershell|cmd|gitbash",
  "scope": "project|user|local",
  "phases_completed": ["0", "1", "2", ...],
  "node_version": "v20.x.x",
  "install_method": "brew|winget|portable|nvm|manual",
  "notes": []
}
```

On final success (after Phase 8), delete the state file — it's no longer needed.

# 🎚 STATUS FORMAT PER PHASE

After each phase, emit (in Portuguese, this is what the user sees):

```
━━━ FASE N — <Nome em português> ━━━
[✅/⚠️/❌] <subitem>: <evidência da saída do comando>
Resultado: <APROVADO | PARCIAL | BLOQUEADO>
Próximo passo: <descrição em português>
```

# 🔁 NETWORK RETRY POLICY

For any network operation (curl, npm install, brew, winget, Invoke-WebRequest):
- Attempt 1: immediate
- Attempt 2: 3-second wait
- Attempt 3: 10-second wait
- After 3 failures: switch to next method (don't keep retrying the same one)

---

## PHASE 0 — ENVIRONMENT DETECTION

Detect:
- **OS**: macOS / Linux native / WSL / Windows native
- **Architecture**: arm64 / x86_64 / x64 / x86
- **Shell**: bash / zsh / PowerShell / cmd / Git Bash (MSYS)
- **Current directory** and whether it's a git repo root
- **Available package managers**: brew, winget, apt, dnf, pacman

Detection logic:

```bash
# Universal first attempt:
uname -srm 2>/dev/null
```

If `uname` works:
- Output starts with `Darwin` → **macOS**, check `uname -m` for arm64/x86_64
- Output starts with `Linux` → check `/proc/version`:
  - Contains "microsoft" or "WSL" → **WSL**
  - Otherwise → **Linux native**
- Output starts with `MINGW` or `MSYS` → **Git Bash on Windows**

If `uname` fails:
- `$PSVersionTable.OS` works → **Windows PowerShell**
- `ver` works → **Windows cmd**

Critical Windows-specific check — **PowerShell Execution Policy** (silent killer):
```powershell
Get-ExecutionPolicy -Scope Process
```
If result is `Restricted` or `AllSigned`, you cannot run scripts. Use 👋 PATIENT HELP mode in Portuguese to ask the user to run:
```powershell
Set-ExecutionPolicy -Scope Process Bypass
```
Explain: this only affects the current session and is safe.

**Pre-flight network check** — before declaring detection complete, verify connectivity to:
- `registry.npmjs.org` (npm packages)
- `nodejs.org` (Node downloads)
- `raw.githubusercontent.com` (Homebrew/nvm install scripts)
- `playwright.azureedge.net` (browser binaries)

Method:
```bash
# Linux/Mac/WSL/Git Bash:
for host in registry.npmjs.org nodejs.org raw.githubusercontent.com; do
  curl -fsS -o /dev/null --max-time 5 "https://$host" && echo "$host OK" || echo "$host FAIL"
done
```

```powershell
# PowerShell:
@('registry.npmjs.org','nodejs.org','raw.githubusercontent.com') | ForEach-Object {
  try { Invoke-WebRequest "https://$_" -TimeoutSec 5 -UseBasicParsing | Out-Null; "$_ OK" } catch { "$_ FAIL" }
}
```

If any host fails, check proxy environment variables: `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`. If a proxy is set, inform the user (Portuguese), and configure npm accordingly:
```bash
npm config set proxy "$HTTP_PROXY"
npm config set https-proxy "$HTTPS_PROXY"
```

If no proxy is set but connections fail → corporate firewall is likely blocking. Pause and inform user (Portuguese).

**Output** for the user (Portuguese): a table summarizing OS, architecture, shell, package manager available, network status.

---

## PHASE 1 — PREREQUISITE AUDIT

Diagnose only — do not fix yet. Report status of each in Portuguese table:

| Item | Command | Pass criterion |
|---|---|---|
| Node.js | `node --version` | ≥ 18.0.0 |
| npm | `npm --version` | any |
| npx | `npx --version` | available |
| Claude Code | `claude --version` | already running |
| npm registry | `npm ping` | success |

If **all ✅**: skip to Phase 3.
If **anything missing/outdated**: proceed to Phase 2.

---

## PHASE 2 — AUTO-INSTALL MISSING DEPENDENCIES

This is the core phase. Install what's missing with cascading fallbacks. Only involve the user when truly needed.

### 2A · macOS — Install Node.js

#### Method A1: Homebrew (if already installed)
```bash
command -v brew && brew --version
```
If brew exists:
```bash
brew install node
```
Then **refresh PATH** in current shell (essential):
```bash
# Apple Silicon (arm64):
[ -d "/opt/homebrew/bin" ] && eval "$(/opt/homebrew/bin/brew shellenv)"
# Intel (x86_64):
[ -d "/usr/local/bin/brew" ] && eval "$(/usr/local/bin/brew shellenv)"
hash -r
```
Verify: `node --version`. If ≥ v18, go to 2D.

#### Method A2: Install Homebrew + Node (brew missing)
Brew installation needs the user's macOS login password (once). Use 👋 PATIENT HELP mode (Portuguese template above as reference; adapt the timing — say "5 minutos" because brew install is slow).

After user approval:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Then refresh PATH:
```bash
if [ -d "/opt/homebrew/bin" ]; then eval "$(/opt/homebrew/bin/brew shellenv)"; else eval "$(/usr/local/bin/brew shellenv)"; fi
brew install node
hash -r
node --version
```
If v18+, go to 2D. Else, try A3.

#### Method A3: nvm (fallback, no password)
If user refused password or brew failed:
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install --lts
nvm use --lts
hash -r
node --version
```
If v18+, go to 2D. Else, A4.

#### Method A4: Manual (last resort)
Use 👋 PATIENT HELP mode in Portuguese. Direct user to https://nodejs.org/, walk through clicking LTS download, opening `.pkg`, clicking through installer. After they finish, they reply "pronto" and you re-verify with `/usr/local/bin/node --version` or restart-session instruction.

### 2B · Windows — Install Node.js

#### Method B1: winget (Windows 10 1809+ / Windows 11)
```powershell
Get-Command winget -ErrorAction SilentlyContinue
```
If winget exists, use 👋 PATIENT HELP mode to explain UAC. The Portuguese template should warn about the **yellow/blue popup window** and "click Sim" instruction.

After approval:
```powershell
winget install -e --id OpenJS.NodeJS.LTS --silent --accept-source-agreements --accept-package-agreements
```
Refresh PATH (critical — current session won't see new Node otherwise):
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```
Verify: `node --version`. If v18+, go to 2D.

#### Method B2: Portable Node (no admin, no UAC — PREFERRED if user lacks admin)
This is the most reliable Windows method when admin is unavailable.

**Dynamic version lookup** (avoids hardcoded versions going stale):
```powershell
$lts = (Invoke-RestMethod "https://nodejs.org/dist/index.json" -TimeoutSec 10) | Where-Object { $_.lts } | Select-Object -First 1
$nodeVersion = $lts.version.TrimStart('v')
$arch = if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" }
$zipName = "node-v$nodeVersion-win-$arch.zip"
$url = "https://nodejs.org/dist/v$nodeVersion/$zipName"
$dest = "$env:USERPROFILE\nodejs-portable"

# Download with retry
$attempt = 0
do {
  $attempt++
  try {
    Invoke-WebRequest -Uri $url -OutFile "$env:TEMP\$zipName" -TimeoutSec 60
    break
  } catch {
    if ($attempt -ge 3) { throw }
    Start-Sleep -Seconds ($attempt * 5)
  }
} while ($true)

# Clean previous attempts
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
Expand-Archive -Path "$env:TEMP\$zipName" -DestinationPath $dest -Force
$nodeDir = (Get-ChildItem $dest -Directory | Select-Object -First 1).FullName

# Session PATH
$env:Path = "$nodeDir;$env:Path"
# Persistent USER PATH (no admin needed)
$userPath = [System.Environment]::GetEnvironmentVariable("Path","User")
if ($userPath -notlike "*$nodeDir*") {
  [System.Environment]::SetEnvironmentVariable("Path", "$nodeDir;$userPath", "User")
}

node --version
npm --version
```

If Node works, go to 2D.

#### Method B3: Manual via download (last resort)
👋 PATIENT HELP mode in Portuguese: walk through downloading the `.msi` from nodejs.org and clicking through installer. Mention UAC popup. After install, user must `/quit` and `claude` again — you cannot recover PATH inside the same dead session.

### 2C · Linux / WSL — Install Node.js

#### Method C1: nvm (preferred, no sudo)
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install --lts
nvm use --lts
hash -r
node --version
```

#### Method C2: apt (Debian/Ubuntu — requires sudo, ask first)
Use 🔔 QUICK APPROVAL mode in Portuguese.

### 2D · Post-install verification (ALL OSes)

Regardless of method used, **verify before advancing**:
```bash
node --version    # v18+
npm --version
npx --version
```

If `node --version` fails despite apparent success:

1. **Try absolute paths** (common locations):
   - macOS brew arm64: `/opt/homebrew/bin/node`
   - macOS brew x86_64: `/usr/local/bin/node`
   - macOS nvm: `~/.nvm/versions/node/*/bin/node`
   - Windows winget: `C:\Program Files\nodejs\node.exe`
   - Windows portable: `$env:USERPROFILE\nodejs-portable\*\node.exe`

2. **If absolute path works but `node` doesn't**: PATH not refreshed. Re-run the refresh commands from 2A/2B. Run `hash -r` (bash/zsh). For Git Bash on Windows, you may need to convert paths: `/c/Program Files/nodejs`.

3. **If absolute path also fails**: install genuinely failed. Try the next fallback method.

4. **If all methods exhausted**: use 👋 PATIENT HELP mode (Portuguese) — ask user to `/quit` Claude Code, restart `claude` in this directory, and paste the prompt again. The state file will let you resume from Phase 2D verification.

**Do not advance to Phase 3 until `node --version` returns ≥ v18 in the current session.**

---

## PHASE 3 — SCOPE DECISION

Use 🔔 QUICK APPROVAL mode. Portuguese template:

```
🔔 Decisão rápida — onde registrar o Playwright MCP?

  1. project (recomendado para times) — cria .mcp.json na raiz do repo. 
     Versionável via git. Colaboradores recebem o MCP ao clonar.
  2. user (recomendado para uso pessoal global) — disponível em todas 
     as suas sessões Claude Code. Salvo em ~/.claude.json.
  3. local (padrão da CLI) — apenas neste diretório, nesta máquina.

Qual prefere? (1 / 2 / 3)
```

Before applying, detect existing config:
```bash
# Project:
test -f .mcp.json && grep -l playwright .mcp.json 2>/dev/null
# User/local:
claude mcp list 2>/dev/null | grep -i playwright
```

If a playwright config already exists, show it to the user (Portuguese) and ask: substituir / manter / pular para Fase 5.

---

## PHASE 4 — REGISTER PLAYWRIGHT MCP

### 4A · macOS / Linux / WSL2 / Git Bash on Windows
```bash
claude mcp add playwright --scope <SCOPE> -- npx '@playwright/mcp@latest'
```
The double-dash `--` separates `claude mcp add` args from the MCP command args. Required because `@playwright/mcp@latest` starts with `@`.

### 4B · Windows NATIVE (PowerShell / cmd, not WSL/Git Bash) — node-direct method
On Windows native, `npx` resolves to `npx.cmd` and the stdio transport breaks when MCP spawns a batch wrapper. Do **not** use npx-based config on Windows native.

```powershell
# Install package locally
npm install --save-dev @playwright/mcp@latest

# Get absolute path with forward slashes for JSON
$cli = (Resolve-Path .\node_modules\@playwright\mcp\cli.js).Path -replace '\\','/'

# Register via add-json (note: PowerShell quoting is brittle, use a temp file if needed)
$config = @{ type = "stdio"; command = "node"; args = @($cli) } | ConvertTo-Json -Compress
claude mcp add-json playwright --scope <SCOPE> $config
```

For scope=project, equivalent `.mcp.json`:
```json
{
  "mcpServers": {
    "playwright": {
      "type": "stdio",
      "command": "node",
      "args": ["C:/absolute/path/to/node_modules/@playwright/mcp/cli.js"]
    }
  }
}
```

### Verification (all OSes)
```bash
claude mcp list
claude mcp get playwright
```
Pass criterion: `playwright` listed, coherent command/args, no errors.

If failure → go to Common Errors table.

---

## PHASE 5 — INSTALL BROWSER BINARY

**Pre-flight: disk space check** — Chrome download is ~150–300 MB.

```bash
# macOS/Linux:
df -h ~ | tail -1 | awk '{print $4}'
```
```powershell
# Windows:
$drive = (Get-Location).Path.Substring(0,1)
(Get-PSDrive -Name $drive).Free / 1GB
```

If less than 1 GB free, warn in Portuguese using 👋 PATIENT HELP mode (suggest cleanup or alternate location).

Then 🔔 QUICK APPROVAL mode in Portuguese:
```
🔔 Vou baixar o Chrome para Playwright (~150–300 MB, ~1–2 min).
   Comando: npx playwright install chrome
   Pode prosseguir? (sim / outro browser / não)
```

Browser alternatives: `chromium`, `firefox`, `webkit`, `msedge`. Default `chrome`.

Execute with retry:
```bash
npx playwright install chrome
```
If timeout or transient error, retry per network retry policy. Verify:
```bash
npx playwright --version
```

---

## PHASE 6 — LINUX SYSTEM DEPS (skip on Mac/Win)

Linux/Docker need native libs for Chromium. Requires sudo — cannot auto-run.

Use 👋 PATIENT HELP mode in Portuguese:
```
👋 No Linux, o Chrome precisa de algumas bibliotecas do sistema. 
Preciso que você rode este comando em um terminal separado 
(precisa de senha de admin):

  sudo npx playwright install-deps

1. Abra um terminal novo (deixe este Claude Code aberto).
2. Vá para este diretório: cd <path>
3. Cole o comando e Enter.
4. Digite sua senha (nada aparece enquanto digita — é normal).
5. Aguarde 1–3 minutos.
6. Volte aqui e me responda "pronto".
```

Skip on macOS and Windows.

---

## PHASE 7 — CONFIG VERIFICATION

Final pre-test checklist:
```
[ ] node --version → ≥ v18
[ ] npm --version → present
[ ] claude mcp list → contains "playwright"
[ ] claude mcp get playwright → coherent command/args
[ ] If scope=project: .mcp.json exists at repo root, valid JSON
[ ] Browser binary installed (Phase 5)
[ ] (Linux) System deps installed (Phase 6)
```

Validate `.mcp.json` JSON if applicable:
```bash
node -e "JSON.parse(require('fs').readFileSync('.mcp.json'))" && echo "JSON OK"
```

Any failure → return to corresponding phase. Do not skip.

---

## PHASE 8 — FUNCTIONAL TEST (mandatory)

### 8.1 — Session restart (CRITICAL)
Claude Code only loads new MCPs at startup. Use 👋 PATIENT HELP mode in Portuguese:

```
👋 Última etapa — 30 segundos.

Pra o Playwright MCP funcionar, preciso que você reinicie esta sessão:

1. Digite /quit aqui e aperte Enter (sai do Claude Code).
2. Você volta pro terminal normal.
3. Digite "claude" e aperte Enter (abre o Claude Code de novo).
4. Antes de qualquer coisa, digite /mcp e aperte Enter.
5. Você deve ver "playwright" listado e conectado (✅).

Se viu playwright conectado, cole EXATAMENTE este texto como 
sua próxima mensagem:

  Use playwright mcp para abrir https://example.com e me diga 
  o título da página.

Se NÃO viu playwright (ou viu com erro), cole isto pra eu 
diagnosticar:

  /mcp não mostrou playwright conectado. Diagnosticar.
```

### 8.2 — Expected response validation
On the new session, when the user runs the test prompt, the assistant (Claude in the new session) should:
1. Open a visible Chrome window
2. Navigate to example.com
3. Report the title: **"Example Domain"**

⚠️ **Important tip**: literally saying "use playwright mcp" in the first interaction is necessary — otherwise Claude may try to run Playwright via Bash instead of the MCP.

### 8.3 — On test failure
Identify the symptom in the Common Errors table, apply the fix, repeat 8.1.

### 8.4 — Generate health check script
After successful test, generate a portable health-check script the user can run anytime:

For macOS/Linux/WSL/Git Bash, write `playwright-mcp-healthcheck.sh`:
```bash
#!/usr/bin/env bash
echo "=== Playwright MCP Health Check ==="
echo "Node: $(node --version 2>/dev/null || echo 'NOT FOUND')"
echo "Claude MCP:"
claude mcp list 2>/dev/null | grep -i playwright || echo "  ❌ playwright not registered"
echo "Playwright: $(npx playwright --version 2>/dev/null || echo 'NOT FOUND')"
```

For Windows PowerShell, write `playwright-mcp-healthcheck.ps1`:
```powershell
Write-Host "=== Playwright MCP Health Check ==="
Write-Host "Node: $(node --version 2>$null)"
Write-Host "Claude MCP:"
claude mcp list 2>$null | Select-String playwright
Write-Host "Playwright: $(npx playwright --version 2>$null)"
```

Make it executable on Unix (`chmod +x`).

---

## 🚨 COMMON ERRORS TABLE

| Symptom | Likely cause | Fix |
|---|---|---|
| `node: command not found` after install | Session PATH not refreshed | Re-run PATH refresh from 2A/2B; `hash -r`; last resort `/quit`+`claude` |
| MCP listed but "failed to connect" on Windows | `npx.cmd` breaks stdio | Re-do Phase 4B (node-direct) |
| `performance is not defined` on start | Node < 18 | Back to Phase 2, install Node 20 LTS |
| Browser won't open, `libnss3`/`libatk` errors on Linux | Missing system deps | `sudo npx playwright install-deps` (Phase 6) |
| MCP disappears between sessions | `local` scope in different cwd | Re-register with `--scope user` or `--scope project` |
| `Cannot find package @playwright/mcp` | npm fetch failed | `npm cache clean --force`; check proxy config |
| Claude answers without opening browser | Used Bash instead of MCP | Literally say "use playwright mcp" in the prompt |
| `EACCES` downloading browser | Cache permission broken (Linux/Mac) | `sudo chown -R $USER ~/.npm ~/.cache/ms-playwright` |
| winget fails: "Package not found" | Stale winget source | `winget source reset --force; winget source update` |
| Brew fails: "shell integration" | Apple Silicon PATH not set | `eval "$(/opt/homebrew/bin/brew shellenv)"` |
| `.mcp.json` ignored | Wrong directory | Must be at repo root (same level as `.git`) |
| Duplicate MCP registrations | Added at multiple scopes | `claude mcp remove playwright -s <wrong_scope>` |
| Session frozen after Node install | Subprocess shell didn't refresh | Always `/quit`+`claude` after fresh Node install |
| Windows portable download fails (TLS) | Corporate TLS interception | Try winget; if blocked, manual via browser |
| UAC denied on Windows | User isn't admin | Use Phase 2B Method B2 (portable) |
| PowerShell: "cannot be loaded because running scripts is disabled" | Execution Policy = Restricted | `Set-ExecutionPolicy -Scope Process Bypass` |
| Corporate proxy intercepting npm | TLS MITM | Set `HTTP_PROXY`/`HTTPS_PROXY` and `npm config set proxy/https-proxy` |
| Less than 500 MB free disk | Insufficient space | Free space or move browser cache via `PLAYWRIGHT_BROWSERS_PATH` env |
| Git Bash on Windows: paths with spaces fail | Quoting issue | Quote paths, or use 8.3-style `C:/Progra~1/` |
| State file corrupt | JSON parse error in `.playwright-mcp-install-state.json` | Delete the file and restart |
| `claude mcp` command unknown | Claude Code too old | Update Claude Code first |

---

## 📊 FINAL REPORT

When the installation completes (success, blocked, or partial), emit in Portuguese exactly:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎭 PLAYWRIGHT MCP — RELATÓRIO DE INSTALAÇÃO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖥  AMBIENTE
   SO: <Mac/Win/Linux + versão>
   Arquitetura: <x64 / arm64>
   Shell: <bash/zsh/powershell/cmd/gitbash>
   Repo: <path>
   Escopo: <project | user | local>

🔧 INSTALAÇÕES NESTA SESSÃO
   [✅/⏭] Gerenciador de pacotes (Homebrew/winget)
   [✅/⏭] Node.js → versão final: <v20.x.x>
   [✅] @playwright/mcp registrado
   [✅] Chrome para Playwright

📋 STATUS POR FASE
   [✅/❌] 0 — Detecção
   [✅/❌] 1 — Auditoria de pré-requisitos
   [✅/⏭] 2 — Auto-instalação
   [✅/❌] 3 — Escopo definido
   [✅/❌] 4 — MCP registrado
   [✅/❌] 5 — Browser instalado
   [✅/⏭] 6 — Deps Linux
   [✅/❌] 7 — Verificação
   [✅/⏳/❌] 8 — Teste funcional (⏳ = aguardando reinício)

⚙️  CONFIGURAÇÃO APLICADA
   <comando ou JSON exato>

🩺 HEALTH CHECK
   Script gerado: ./playwright-mcp-healthcheck.{sh|ps1}
   Rode esse arquivo a qualquer momento para validar a saúde da instalação.

📍 PRÓXIMOS PASSOS
   1. /quit + claude
   2. Teste: "Use playwright mcp para abrir https://example.com"
   3. <outros>

⚠️  PENDÊNCIAS
   - <se houver>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Then **delete `.playwright-mcp-install-state.json`** — installation is complete.

---

## 🏆 GOLDEN RULES (do not violate)

1. **All user-facing output is in Brazilian Portuguese.** Internal reasoning in English is fine and encouraged.
2. **Persistence:** if a method fails, automatically try the next. Don't stop on first failure.
3. **Verify after every install** with `--version` or equivalent command.
4. **PATH refresh** after Node install — always run platform-appropriate refresh, then `hash -r`.
5. **Absolute paths as fallback** when shell PATH is uncooperative.
6. **Patient mode for non-tech users**: describe what they'll see on screen, what to type, what's normal.
7. **Never declare success without observed evidence** in command output.
8. **Session restart**: only request when truly necessary (after Node install where PATH refresh failed; before Phase 8). Otherwise, in-session refresh suffices.
9. **Transient network errors → retry per policy.** Don't escalate to fallback method on first timeout.
10. **State file**: write after every phase, read at startup to resume, delete on final success.

---

# 🚀 START NOW WITH PHASE 0.

First action: check for an existing `.playwright-mcp-install-state.json` file in the current directory. If present, parse and resume from the last incomplete phase (inform the user in Portuguese). If absent, proceed with fresh Phase 0 (environment detection), emit the status block in Portuguese, and continue automatically into Phase 1.
