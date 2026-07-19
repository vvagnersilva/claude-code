#!/usr/bin/env bash
# =============================================================================
# 00-detect-machine.sh — profile THIS machine, print realistic expectations
# -----------------------------------------------------------------------------
# READ-ONLY and safe to run first, on any OS, with or without the SSD plugged.
# Prints: OS/CPU/RAM/GPU/SIMD profile, target-drive status, a realistic tok/s
# expectation band for GLM-5.2 via Colibrì on this exact machine, a download
# time estimate for the ~372 GB model, and a final verdict.
#
# tok/s bands come from community-measured datapoints in the Colibrì README
# (github.com/JustVugg/colibri, consulted 2026-07-14). Bands between published
# datapoints are EXTRAPOLATED and labelled as such. No number here is a promise
# — especially on external SSDs, where no datapoint is published at all.
#
#   ./scripts/00-detect-machine.sh            informational, always exits 0
#   ./scripts/00-detect-machine.sh --strict   exit 1 if verdict is NOT VIABLE/BLOCKED
# =============================================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/common.sh
source "$SCRIPT_DIR/../lib/common.sh"
load_config

STRICT=0
if [ "${1:-}" = "--strict" ]; then STRICT=1; fi

step "Phase 0 — machine profile & realistic expectations"

# --- 1. profile ---------------------------------------------------------------
OS_PRETTY="$OS_ID"
case "$OS_ID" in
  macos) OS_PRETTY="macOS $(sw_vers -productVersion 2>/dev/null || true)" ;;
  linux|wsl)
    OS_PRETTY="$( (. /etc/os-release 2>/dev/null && printf '%s' "${PRETTY_NAME:-Linux}") || echo Linux)"
    if [ "$OS_ID" = "wsl" ]; then OS_PRETTY="$OS_PRETTY (WSL2 under Windows)"; fi ;;
  windows) OS_PRETTY="Windows shell ($(uname -s 2>/dev/null || echo '?'))" ;;
esac

CPU="unknown"; CORES="?"
case "$OS_ID" in
  macos)
    CPU="$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo unknown)"
    CORES="$(sysctl -n hw.ncpu 2>/dev/null || echo '?')" ;;
  linux|wsl)
    CPU="$(awk -F': ' '/^model name/{print $2; exit}' /proc/cpuinfo 2>/dev/null || echo unknown)"
    CORES="$(nproc 2>/dev/null || echo '?')" ;;
esac
RAM_TOTAL="$(total_ram_gb)"; : "${RAM_TOTAL:=0}"

# SIMD level (x86 only — AVX2 decides whether the engine runs at all there)
HAS_AVX2=0; HAS_AVX512=0
if [ "$ARCH_ID" = "x86_64" ]; then
  FEAT=""
  case "$OS_ID" in
    macos) FEAT="$(sysctl -n machdep.cpu.features machdep.cpu.leaf7_features 2>/dev/null | tr '[:upper:]' '[:lower:]' | tr '\n' ' ' || true)" ;;
    *)     FEAT="$(grep -m1 '^flags' /proc/cpuinfo 2>/dev/null | tr '[:upper:]' '[:lower:]' || true)" ;;
  esac
  case " $FEAT " in *avx2*)   HAS_AVX2=1 ;; esac
  case " $FEAT " in *avx512*) HAS_AVX512=1 ;; esac
fi

# GPU tier available to the engine
GPU="none detected"; GPU_KIND="none"
if [ "$OS_ID" = "macos" ] && [ "$ARCH_ID" = "arm64" ]; then
  GPU="Apple Silicon integrated GPU (Metal backend available)"
  GPU_KIND="metal"
elif require_cmd nvidia-smi; then
  GPU="$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null | head -1 || echo 'NVIDIA (details unavailable)')"
  GPU_KIND="cuda"
fi

info "OS      : $OS_PRETTY  (arch: $ARCH_ID)"
info "CPU     : $CPU  ($CORES cores)"
if [ "$ARCH_ID" = "x86_64" ]; then
  info "SIMD    : AVX2=$([ "$HAS_AVX2" = 1 ] && echo yes || echo NO)  AVX-512=$([ "$HAS_AVX512" = 1 ] && echo yes || echo no)"
fi
info "RAM     : ${RAM_TOTAL} GB total"
info "GPU     : $GPU"
info "--ram   : $RAM_GB GB budget (from config; RAM_GB=auto leaves the OS headroom)"

# --- 2. drive status ------------------------------------------------------------
if is_external_mount "$MOUNT"; then
  ok "Target drive: $MOUNT mounted and external/dedicated ($(free_gb_of "$MOUNT") GB free; need >= ${MIN_FREE_GB})"
else
  warn "Target drive: $MOUNT not usable yet — $REASON"
fi
ROOT_FREE="$(free_gb_of /)"
info "Boot drive free space: ${ROOT_FREE:-?} GB (the ~372 GB model must NEVER land here — the scripts guard this)"

# --- 3. expectation band ----------------------------------------------------------
BAND="unknown"; BASIS=""; VERDICT="UNKNOWN"
if [ "$OS_ID" = "windows" ]; then
  BAND="n/a"; VERDICT="BLOCKED"
  BASIS="this installer does not automate native Windows — use WSL2 (wsl --install); upstream also has a MinGW-w64 port for manual builds"
elif [ "$RAM_TOTAL" -gt 0 ] && [ "$RAM_TOTAL" -lt 16 ]; then
  BAND="n/a"; VERDICT="NOT VIABLE"
  BASIS="Colibrì's stated minimum is 16 GB RAM (this machine: ${RAM_TOTAL} GB)"
elif [ "$ARCH_ID" = "x86_64" ] && [ "$HAS_AVX2" = "0" ]; then
  BAND="n/a"; VERDICT="NOT VIABLE"
  BASIS="the x86-64 engine requires AVX2 and this CPU does not report it"
elif [ "$OS_ID" = "macos" ] && [ "$ARCH_ID" = "arm64" ]; then
  if   [ "$RAM_TOTAL" -ge 96 ]; then BAND="1.0–2.1 tok/s"; VERDICT="USABLE (slow but real work possible)"
       BASIS="MEASURED: M5 Max 128 GB, Metal, warm cache (1.83–2.06)"
  elif [ "$RAM_TOTAL" -ge 64 ]; then BAND="0.4–1.0 tok/s"; VERDICT="USABLE FOR SHORT TASKS"
       BASIS="EXTRAPOLATED between M4 Pro 48 GB (0.30) and M5 Max 128 GB (1.83)"
  elif [ "$RAM_TOTAL" -ge 40 ]; then BAND="0.2–0.4 tok/s"; VERDICT="DEMO / PATIENCE REQUIRED"
       BASIS="MEASURED: Mac Mini M4 Pro 48 GB, Metal, --ram 38 (0.30)"
  elif [ "$RAM_TOTAL" -ge 24 ]; then BAND="0.1–0.2 tok/s"; VERDICT="DEMO-ONLY"
       BASIS="EXTRAPOLATED below the 48 GB datapoint (smaller expert cache → more cold disk reads)"
  else BAND="0.05–0.15 tok/s"; VERDICT="DEMO-ONLY"
       BASIS="floor of published datapoints; near the 16 GB minimum"
  fi
elif [ "$OS_ID" = "macos" ]; then
  BAND="0.05–0.2 tok/s"; VERDICT="DEMO-ONLY (unverified)"
  BASIS="NOT VERIFIED — no published Intel-Mac datapoint; x86 AVX2 CPU path, no Metal expert offload datapoint"
elif [ "$OS_ID" = "wsl" ]; then
  BAND="0.05–0.11 tok/s"; VERDICT="DEMO-ONLY"
  BASIS="MEASURED: developer baseline on WSL2 — and ONLY if the model sits on a native ext4 disk, never /mnt/c (drvfs)"
elif [ "$OS_ID" = "linux" ] && [ "$ARCH_ID" = "x86_64" ]; then
  if [ "$GPU_KIND" = "cuda" ]; then BAND="0.4–1.6 tok/s"; VERDICT="USABLE FOR SHORT TASKS"
       BASIS="MEASURED range: single big-VRAM GPU rigs up to 6×RTX 5090 (1.64); depends on how much of the expert tier fits in VRAM"
  elif [ "$RAM_TOTAL" -ge 128 ]; then BAND="0.3–0.5 tok/s"; VERDICT="DEMO / PATIENCE REQUIRED"
       BASIS="MEASURED: Ryzen AI Max+ 395, 128 GB LPDDR5x (0.40)"
  elif [ "$RAM_TOTAL" -ge 64 ]; then BAND="0.2–0.4 tok/s"; VERDICT="DEMO / PATIENCE REQUIRED"
       BASIS="EXTRAPOLATED between 32 GB-class baselines and the 128 GB datapoint"
  elif [ "$RAM_TOTAL" -ge 32 ]; then BAND="0.1–0.3 tok/s"; VERDICT="DEMO-ONLY"
       BASIS="EXTRAPOLATED; heavily disk-bound at this cache size"
  else BAND="0.05–0.15 tok/s"; VERDICT="DEMO-ONLY"
       BASIS="MEASURED baseline on modest dev boxes"
  fi
elif [ "$ARCH_ID" = "aarch64" ]; then
  BAND="unknown"; VERDICT="UNKNOWN"
  BASIS="NOT VERIFIED — upstream targets x86-64 (AVX2) on Linux; the NEON path is macOS-only. The build may simply not work here"
fi

step "Realistic expectations on THIS machine"
info "Throughput band : ${BAND}"
info "Basis           : ${BASIS}"
info "Cold start      : 0.05–0.1 tok/s on ANY hardware for the first prompts (~11 GB of reads per token until the cache/pin warms via .coli_usage — it gets faster across runs)."
if [ "$GPU_KIND" = "metal" ]; then
  info "Metal           : ~1.4× over CPU-only on Apple Silicon (built automatically; ENABLE_METAL=$ENABLE_METAL)"
fi
info "External SSD    : ALL published datapoints are internal/direct NVMe. A TB3/4 or USB4 NVMe enclosure should land in the same order of magnitude, but no external-SSD number is published — measure before promising anything."

PRACTICE=""
case "$BAND" in
  "0.05"*)               PRACTICE="a 300-token answer ≈ 35–100 minutes" ;;
  "0.1–0.2"*)            PRACTICE="a 300-token answer ≈ 25–50 minutes" ;;
  "0.1–0.3"*)            PRACTICE="a 300-token answer ≈ 17–50 minutes" ;;
  "0.2–0.4"*)            PRACTICE="a 300-token answer ≈ 12–25 minutes" ;;
  "0.3–0.5"*)            PRACTICE="a 300-token answer ≈ 10–17 minutes" ;;
  "0.4–1.0"*|"0.4–1.6"*) PRACTICE="a 300-token answer ≈ 3–12 minutes" ;;
  "1.0–2.1"*)            PRACTICE="a 300-token answer ≈ 2.5–5 minutes" ;;
esac
if [ -n "$PRACTICE" ]; then
  info "In practice     : $PRACTICE (after warm-up; first prompts slower)"
fi

# --- 4. download estimate ---------------------------------------------------------
step "Model download estimate (~372 GB, resumable)"
info "at 100 Mbps ≈ 8.5 h   ·   at 500 Mbps ≈ 1.7 h   ·   at 1 Gbps ≈ 50 min"

# --- 5. verdict --------------------------------------------------------------------
step "Verdict"
case "$VERDICT" in
  "NOT VIABLE"|BLOCKED)
    err "VERDICT: $VERDICT — $BASIS"
    if [ "$STRICT" = "1" ]; then exit 1; fi ;;
  UNKNOWN)
    warn "VERDICT: $VERDICT — $BASIS" ;;
  *)
    ok "VERDICT: $VERDICT — expect $BAND after warm-up." ;;
esac
info "Next: ./setup.sh --dry-run   (preview every action, change nothing)"
exit 0
