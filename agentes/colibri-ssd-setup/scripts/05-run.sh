#!/usr/bin/env bash
# =============================================================================
# 05-run.sh — launch the Colibrì engine, streaming the model from the SSD
# -----------------------------------------------------------------------------
# Verified run form (README + coli launcher):
#     COLI_MODEL=<dir> ./coli chat --ram N
#   • `coli` is a Python 3 launcher that drives the compiled `glm` engine
#   • COLI_MODEL points at the model directory (there is NO --model-path flag)
#   • the launcher itself notes macOS RLIMIT_NOFILE=256 is too low (it mmaps
#     144+ shards; Linux's default 1024 is also tight) → we raise `ulimit -n`
#   • COLI_METAL=1 on Apple Silicon if the Metal engine was built
#   • PILOT=1 (experimental router-lookahead prefetch) if enabled in config
# Pass any subcommand/args through, e.g.  ./scripts/05-run.sh serve --port 8000
# =============================================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/common.sh
source "$SCRIPT_DIR/../lib/common.sh"
load_config

step "Phase 5 — run Colibrì ( model on $MODEL_PATH, --ram $RAM_GB )"

# --- preconditions -----------------------------------------------------------
if ! is_dry; then
  [ -x "$BUILD_DIR/glm" ]  || die "Engine not built. Run ./scripts/03-build-colibri.sh first."
  [ -f "$BUILD_DIR/coli" ] || die "Launcher $BUILD_DIR/coli missing. Run ./scripts/03-build-colibri.sh."
  [ -d "$MODEL_PATH" ]     || die "Model dir $MODEL_PATH missing. Run ./scripts/04-download-model.sh first."
  # cheap sanity check that the model actually has weight shards
  if ! ls "$MODEL_PATH"/*.safetensors >/dev/null 2>&1; then
    warn "No .safetensors found in $MODEL_PATH — download may be incomplete; re-run 04 to resume."
  fi
fi

# --- raise open-file limit (macOS default 256 / Linux 1024 is too low) -------
info "Raising open-file limit for this shell (ulimit -n 8192)…"
run_sh "ulimit -n 8192 2>/dev/null || true"

# --- compose env prefixes ----------------------------------------------------
ENV_PREFIX=( "COLI_MODEL=$MODEL_PATH" )

USE_METAL=0
case "${ENABLE_METAL}" in
  yes) USE_METAL=1 ;;
  no)  USE_METAL=0 ;;
  auto) if [ "$OS_ID" = "macos" ] && [ "$ARCH_ID" = "arm64" ]; then USE_METAL=1; fi ;;
esac
if [ "$USE_METAL" = "1" ]; then
  ENV_PREFIX+=( "COLI_METAL=1" )
  info "Metal backend requested (Apple Silicon)."
fi

if [ "${ENABLE_PILOT}" = "1" ]; then
  ENV_PREFIX+=( "PILOT=1" )
  info "PILOT=1 router-lookahead prefetch enabled (experimental)."
fi

# subcommand: default 'chat', or whatever the caller passes.
# For chat/serve we append the configured --ram budget if the caller didn't.
if [ "$#" -gt 0 ]; then
  SUBCMD=( "$@" )
  case " $* " in
    *" --ram "*) : ;;
    *) case "${1:-}" in
         chat|serve) SUBCMD+=( --ram "$RAM_GB" ); info "Appended --ram $RAM_GB (from config; pass your own --ram to override)." ;;
       esac ;;
  esac
else
  SUBCMD=( chat --ram "$RAM_GB" )
fi

# --- launch ------------------------------------------------------------------
CMD="cd '$BUILD_DIR' && ulimit -n 8192 2>/dev/null; ${ENV_PREFIX[*]} ./coli ${SUBCMD[*]}"
info "Launching:"
printf '    %s\n' "$CMD"
if is_dry; then
  printf '%s\n' "${_C_DIM}[dry-run] (engine not started)${_C_RESET}"
else
  bash -c "$CMD"
fi
