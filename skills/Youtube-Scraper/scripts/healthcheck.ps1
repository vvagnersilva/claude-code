# Health check for the YouTube Market Research Agent (Windows PowerShell).
# Run from the repository root:  powershell -File scripts\healthcheck.ps1

Set-Location (Join-Path $PSScriptRoot "..")
Write-Host "=== YouTube Market Research Agent - Health Check ==="

$ok = $true

$nodeV = (node --version 2>$null)
if ($nodeV) { Write-Host "[OK] Node.js: $nodeV" }
else { Write-Host "[X] Node.js: NOT FOUND - run /setup in Claude Code"; $ok = $false }

$npxV = (npx --version 2>$null)
if ($npxV) { Write-Host "[OK] npx: $npxV" }
else { Write-Host "[X] npx: NOT FOUND"; $ok = $false }

if (Test-Path .mcp.json) {
  try {
    Get-Content .mcp.json -Raw | ConvertFrom-Json | Out-Null
    Write-Host "[OK] .mcp.json: present and valid"
  } catch { Write-Host "[X] .mcp.json: invalid JSON"; $ok = $false }
} else { Write-Host "[X] .mcp.json: missing"; $ok = $false }

$pwV = (npx playwright --version 2>$null)
if ($pwV) { Write-Host "[OK] Playwright: $pwV" }
else { Write-Host "[!] Playwright browser not installed yet - /setup installs it" }

if (Test-Path .claude\skills\youtube-niche-research) {
  Write-Host "[OK] Research skill: present"
} else { Write-Host "[X] Research skill: missing"; $ok = $false }

Write-Host "---"
if ($ok) {
  Write-Host "All core checks passed. In Claude Code run:  /youtube-niche-research <niche>"
} else {
  Write-Host "Some checks failed. Open this folder in Claude Code and run:  /setup"
}
