#!/usr/bin/env bash
# =============================================================================
# 03-build-colibri.sh — clone the Colibrì engine ONTO THE SSD and compile it
# -----------------------------------------------------------------------------
# Verified build flow (colibri/c/setup.sh):
#   cd <repo>/c && ./setup.sh      # detects Darwin, builds `make -s glm ARCH=native`,
#                                  # runs the tiny self-test (expects 32/32)
# On Apple Silicon we optionally also build the Metal engine (`make glm METAL=1`)
# — experimental, ~1.4x faster; failure here is non-fatal (CPU build stays).
# Idempotent: pulls if already cloned, rebuilds cleanly.
# =============================================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/common.sh
source "$SCRIPT_DIR/../lib/common.sh"
load_config

step "Phase 3 — build Colibrì engine on the SSD ( $ENGINE_DIR )"

# The engine clone + build artefacts live on the SSD, never the internal drive.
assert_external_mount

run mkdir -p "$COLIBRI_HOME"

# --- 1. clone or update ------------------------------------------------------
if [ -d "$ENGINE_DIR/.git" ]; then
  info "Engine already cloned — updating (git pull --ff-only)…"
  run git -C "$ENGINE_DIR" pull --ff-only || warn "git pull failed (local changes?) — keeping existing checkout."
else
  info "Cloning $COLIBRI_REPO_URL → $ENGINE_DIR"
  run git clone --depth 1 "$COLIBRI_REPO_URL" "$ENGINE_DIR"
fi

# --- 2. build via the project's own setup.sh --------------------------------
if [ ! -d "$BUILD_DIR" ] && ! is_dry; then
  die "Expected build dir $BUILD_DIR not found after clone — repo layout changed?"
fi
info "Building engine via colibri/c/setup.sh (macOS: clang+libomp · Linux: gcc+libgomp; ARCH=native)…"
run_sh "cd '$BUILD_DIR' && ./setup.sh"

# --- 3. optional Metal build on Apple Silicon --------------------------------
WANT_METAL=0
case "${ENABLE_METAL}" in
  yes) WANT_METAL=1 ;;
  no)  WANT_METAL=0 ;;
  auto) if [ "$OS_ID" = "macos" ] && [ "$ARCH_ID" = "arm64" ]; then WANT_METAL=1; fi ;;
esac
if [ "$WANT_METAL" = "1" ]; then
  info "Apple Silicon detected ($ARCH_ID) — building experimental Metal engine (make glm METAL=1)…"
  if run_sh "cd '$BUILD_DIR' && make glm METAL=1"; then
    ok "Metal engine built. Runtime will set COLI_METAL=1 (see 05-run.sh)."
  else
    warn "Metal build failed — keeping the CPU build from setup.sh. Runtime falls back to CPU."
  fi
else
  info "Metal build skipped (ENABLE_METAL=$ENABLE_METAL, os=$OS_ID, arch=$ARCH_ID)."
fi

# --- 3b. optional CUDA build on Linux/WSL with an NVIDIA GPU ------------------
WANT_CUDA=0
case "${ENABLE_CUDA:-auto}" in
  yes) WANT_CUDA=1 ;;
  no)  WANT_CUDA=0 ;;
  auto) if [ "$OS_ID" != "macos" ] && require_cmd nvidia-smi; then WANT_CUDA=1; fi ;;
esac
if [ "$WANT_CUDA" = "1" ]; then
  info "NVIDIA GPU detected — building CUDA engine (make glm CUDA=1)…"
  if run_sh "cd '$BUILD_DIR' && make glm CUDA=1"; then
    ok "CUDA engine built (expert tier can live in VRAM)."
  else
    warn "CUDA build failed (toolkit missing?) — keeping the CPU build."
  fi
fi

# --- 4. verify artefacts -----------------------------------------------------
if ! is_dry; then
  [ -x "$BUILD_DIR/glm" ] || die "Engine binary '$BUILD_DIR/glm' not found — build failed."
  [ -f "$BUILD_DIR/coli" ] || die "Launcher '$BUILD_DIR/coli' (python3) not found — repo layout changed?"
  ok "Engine binary: $BUILD_DIR/glm"
  ok "Launcher:      $BUILD_DIR/coli  (python3)"
fi

ok "Phase 3 complete — engine built on the SSD."
