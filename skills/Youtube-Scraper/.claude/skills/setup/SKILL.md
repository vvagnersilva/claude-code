---
name: setup
description: First-time environment setup for this repository. Installs and verifies everything the YouTube market-research agent needs to run — Node.js and the Playwright MCP browser — with cascading fallbacks for macOS, Windows and Linux, even on a machine with ZERO prior setup. Use this before the first research run, or whenever the Playwright browser tools are missing or disconnected, a research run fails because the browser tool is unavailable, or the user says setup/install is not working.
---

# Environment Setup — YouTube Market Research Agent

Install and verify everything this repository needs so the
`youtube-niche-research` skill can run: **Node.js** and the **Playwright MCP
browser**. Work **regardless of the machine's starting state — including zero
setup**.

## 🌐 Language protocol

- **Internal directives (this file) are English — for you, the agent.**
- **Everything the user sees MUST be in Brazilian Portuguese**: status lines,
  approval requests, patient-help blocks, errors, the final report. The only
  English allowed in user-facing text is technical identifiers (commands, paths,
  package names, versions).

## 🎯 Mission rules

1. **Autonomy first.** Auto-install everything you can without involving the user.
2. **Verify everything.** After any install, confirm with `--version` (or
   equivalent) before advancing.
3. **Cascade fallbacks.** Each dependency has 2–3 install methods — if A fails,
   try B, then C. Escalate to manual only when genuinely exhausted.
4. **Patience with non-technical users.** When human action is unavoidable
   (system password, UAC click), explain what they will see and what to type, as
   if they have never opened a terminal.
5. **Retry transient errors.** Network blip / npm timeout → retry per the policy
   below before switching method.
6. **Idempotent.** If something is already correct, verify once and move on.
7. **Never declare success without evidence** seen in a command's output.
8. **Do not stop** until the Phase 7 functional test passes, or until every
   method is exhausted and you can state exactly what is blocking.

Detailed OS-specific commands and the error table live in
**`install-commands.md`** — read it when you reach Phase 2.

## 📡 Communication modes

Use exactly one per interaction. Output is **Portuguese**.

**🤖 AUTONOMOUS** (default) — executing; report progress briefly, no question:
```
🤖 Verificando Node.js... → encontrado v20.11.0 ✅
```

**🔔 QUICK APPROVAL** — about to do something impactful but routine:
```
🔔 Vou instalar o Node.js LTS via Homebrew (~2 min, não precisa de senha).
   Posso prosseguir? (sim/não)
```

**👋 PATIENT HELP** — human action required, user may be non-technical:
```
👋 Preciso da sua ajuda por ~1 minuto.

Vou pedir ao seu computador para instalar uma ferramenta. Vai aparecer
um pedido de senha.

📌 O que você vai ver: uma linha pedindo "Password:".
📌 O que você faz:
   1. Digite a senha de login do seu computador.
   2. ⚠️ Nada aparece na tela enquanto você digita — nem pontinhos.
      Isso é normal, é segurança.
   3. Aperte Enter e aguarde.
   4. Quando puder digitar de novo, me responda "ok".

Pronto pra começar? (sim/não)
```

## 🔁 Network retry policy

For any network operation (`curl`, `npm install`, `brew`, `winget`, downloads):
attempt 1 immediate · attempt 2 after 3 s · attempt 3 after 10 s · after 3
failures switch to the next method (do not keep retrying the same one).

## 💾 State persistence

At session start, look for `.youtube-setup-state.json` in the repo root. If found
and valid JSON, tell the user (Portuguese) "🔁 Detectei uma configuração anterior
em progresso. Vou retomar da Fase X." and skip completed phases. Write the file
after each phase. Delete it after Phase 7 succeeds. Schema:
```json
{ "version": "1", "os": "macOS|Windows|Linux|WSL", "arch": "arm64|x64",
  "shell": "bash|zsh|powershell|cmd|gitbash", "phases_completed": [],
  "node_version": "", "notes": [] }
```

## Status block per phase

After each phase, emit in Portuguese:
```
━━━ FASE N — <Nome> ━━━
[✅/⚠️/❌] <subitem>: <evidência da saída do comando>
Resultado: <APROVADO | PARCIAL | BLOQUEADO>
Próximo passo: <descrição>
```

---

## PHASE 0 — Environment detection

Detect **OS** (macOS / Linux native / WSL / Windows native), **architecture**,
**shell**, and available package managers (`brew`, `winget`, `apt`, `dnf`).
Start with `uname -srm`; `Darwin`→macOS, `Linux`→check `/proc/version` for
"microsoft"→WSL, `MINGW`/`MSYS`→Git Bash. If `uname` fails, you are on Windows
PowerShell/cmd.

Windows-only silent killer — check **PowerShell Execution Policy**:
`Get-ExecutionPolicy -Scope Process`. If `Restricted`/`AllSigned`, use 👋 PATIENT
HELP to have the user run `Set-ExecutionPolicy -Scope Process Bypass` (session
only, safe).

**Network pre-flight** — verify reachability of `registry.npmjs.org`,
`nodejs.org`, `raw.githubusercontent.com` (see `install-commands.md`). If any
fails, check `HTTP_PROXY`/`HTTPS_PROXY`; configure npm if a proxy exists; if not,
warn the user a corporate firewall is likely blocking.

Output a Portuguese table: SO, arquitetura, shell, gerenciador de pacotes, rede.

## PHASE 1 — Prerequisite audit

Diagnose only — do not fix yet. Report a Portuguese table:

| Item | Comando | Critério |
|---|---|---|
| Node.js | `node --version` | ≥ 18.0.0 |
| npm | `npm --version` | presente |
| npx | `npx --version` | presente |
| Claude Code | já em execução | ✅ |

All ✅ → skip to Phase 3. Anything missing/outdated → Phase 2.

## PHASE 2 — Auto-install missing dependencies

Read **`install-commands.md`** and follow the cascade for the detected OS to
install **Node.js ≥ 18 (LTS recommended)**. Verify in-session with
`node --version`; refresh PATH and run `hash -r` after installing. Do not advance
until `node --version` reports ≥ v18 in the current session.

## PHASE 3 — Verify the Playwright MCP registration

This repository **ships `.mcp.json`** at its root, which registers the
`playwright` MCP server — you normally do **not** need to register anything.

1. Confirm `.mcp.json` exists at the repo root and is valid JSON:
   `node -e "JSON.parse(require('fs').readFileSync('.mcp.json'))"`.
2. **Windows native only** (PowerShell/cmd, not WSL/Git Bash): the npx-based
   stdio transport can break. Apply the Windows node-direct fix in
   `install-commands.md` (install `@playwright/mcp` locally and rewrite
   `.mcp.json` to the `node`-direct form).
3. If `.mcp.json` is somehow missing, recreate it (template in
   `install-commands.md`).

## PHASE 4 — Install the browser binary

Pre-flight: check ≥ 1 GB free disk. Then use 🔔 QUICK APPROVAL:
```
🔔 Vou baixar o navegador Chromium para o Playwright (~150–300 MB, ~1–2 min).
   Posso prosseguir? (sim/não)
```
Run `npx playwright install chromium` (retry per policy). Verify with
`npx playwright --version`.

## PHASE 5 — Linux system dependencies (skip on macOS/Windows)

On Linux/WSL the browser needs native libraries (requires sudo). Use 👋 PATIENT
HELP to have the user run `sudo npx playwright install-deps` in a separate
terminal. Skip entirely on macOS and Windows.

## PHASE 6 — Verification checklist

```
[ ] node --version    → ≥ v18
[ ] npm --version     → presente
[ ] .mcp.json         → existe na raiz, JSON válido
[ ] npx playwright --version → presente (browser instalado)
[ ] (Linux) system deps instaladas
```
Any failure → return to the matching phase.

## PHASE 7 — Functional test (mandatory)

Claude Code only loads MCP servers at startup, so the test needs a restart. Use
👋 PATIENT HELP in Portuguese:
```
👋 Última etapa — 30 segundos.

Para o navegador funcionar, reinicie esta sessão:

1. Digite /quit e aperte Enter (sai do Claude Code).
2. Digite "claude" e aperte Enter (abre de novo).
3. Digite /mcp e aperte Enter — você deve ver "playwright" conectado ✅.

Se viu o playwright conectado, cole isto como próxima mensagem:

  Use o playwright mcp para abrir https://example.com e me diga o título.

Se NÃO viu (ou viu com erro), cole isto:

  /mcp não mostrou o playwright conectado. Diagnosticar.
```
The restarted session should open a browser, navigate to example.com and report
the title **"Example Domain"**. On failure, consult the error table in
`install-commands.md`, fix, and retry.

After success, delete `.youtube-setup-state.json` and tell the user they can now
run a research, e.g. `/youtube-niche-research arquitetura`.

A ready-made health check ships in `scripts/healthcheck.sh` (macOS/Linux/WSL/Git
Bash) and `scripts/healthcheck.ps1` (Windows) — point the user to it for future
checks; you do not need to generate one.

## 📊 Final report (Portuguese)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎭 CONFIGURAÇÃO — RELATÓRIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖥  Ambiente: <SO> · <arquitetura> · <shell>
🔧 Instalado nesta sessão:
   [✅/⏭] Node.js → <versão>
   [✅/⏭] Navegador Chromium (Playwright)
📋 Fases: 0✅ 1✅ 2<✅/⏭> 3✅ 4✅ 5<✅/⏭> 6✅ 7<✅/⏳>
📍 Próximo passo: /quit + claude, depois rode uma pesquisa:
   /youtube-niche-research <seu nicho>
⚠️  Pendências: <se houver>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🏆 Golden rules

1. All user-facing output in Brazilian Portuguese; internal reasoning English.
2. If a method fails, automatically try the next — don't stop on first failure.
3. Verify after every install with `--version`.
4. Refresh PATH after a Node install, then `hash -r`; use absolute paths as a
   fallback when the shell PATH is uncooperative.
5. Patient mode for non-technical users — describe the screen, the keystrokes,
   what is normal.
6. Never declare success without observed evidence.
7. Request a session restart only when truly necessary (after a fresh Node
   install where PATH refresh failed; before Phase 7).
8. Write the state file after every phase; delete it on final success.
