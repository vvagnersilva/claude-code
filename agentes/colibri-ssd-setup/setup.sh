#!/usr/bin/env bash
# =============================================================================
# setup.sh — one-command orchestrator for the Colibrì-on-external-SSD setup
# -----------------------------------------------------------------------------
# Cross-platform (macOS / Linux / WSL2). Always starts with phase 00 (machine
# profile + realistic expectations, read-only), then runs phases 01→04 in
# order (check drive → install tools → build engine → download model).
# Idempotent: safe to re-run; each phase skips finished work. Stops immediately
# with a clear message on the first failing phase.
#
#   ./setup.sh                 run phases 01-04 (phase-0 profile shown first)
#   ./setup.sh detect          only profile this machine + expectations (read-only)
#   ./setup.sh --dry-run       show exactly what each phase WOULD do, run nothing
#   ./setup.sh --only 3        run only phase 3
#   ./setup.sh --from 3        run phases 3 and 4
#   ./setup.sh run [args...]   launch the engine (phase 05), passing args through
#   ./setup.sh --help
# =============================================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

usage() { sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'; }

ONLY=""; FROM=1
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) export COLIBRI_DRY_RUN=1; shift ;;
    --only)    ONLY="${2:?--only needs a phase number}"; shift 2 ;;
    --from)    FROM="${2:?--from needs a phase number}"; shift 2 ;;
    detect)    shift; exec "$SCRIPT_DIR/scripts/00-detect-machine.sh" "$@" ;;
    run)       shift; exec "$SCRIPT_DIR/scripts/05-run.sh" "$@" ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown argument: $1  (try --help)" ;;
  esac
done

load_config

PHASES=(
  "01-check-drive.sh"
  "02-install-tools.sh"
  "03-build-colibri.sh"
  "04-download-model.sh"
)

cat <<EOF
${_C_BOLD}🐦 colibri-ssd-setup${_C_RESET}
  OS       : $OS_ID / $ARCH_ID
  Volume   : $MOUNT   (external NVMe: APFS on macOS / ext4 on Linux)
  Engine   : $ENGINE_DIR
  Model    : $MODEL_REPO
             -> $MODEL_PATH
  RAM budget: ${RAM_GB} GB
  Mode     : $(is_dry && echo 'DRY-RUN (nothing executed)' || echo 'LIVE')
EOF

# Phase 0 — informational machine profile (read-only; never blocks the run)
bash "$SCRIPT_DIR/scripts/00-detect-machine.sh" || warn "machine profile failed — continuing anyway"

for i in "${!PHASES[@]}"; do
  n=$((i+1))
  [ -n "$ONLY" ] && [ "$ONLY" != "$n" ] && continue
  [ -z "$ONLY" ] && [ "$n" -lt "$FROM" ] && continue
  script="$SCRIPT_DIR/scripts/${PHASES[$i]}"
  if ! COLIBRI_DRY_RUN="${COLIBRI_DRY_RUN}" bash "$script"; then
    die "Phase $n (${PHASES[$i]}) failed. Fix the issue above and re-run: ./setup.sh --from $n"
  fi
done

step "All requested phases complete."
if is_dry; then
  info "Dry-run only — nothing was changed."
else
  cat <<EOF
${_C_GRN}✓ Setup finished.${_C_RESET} To start chatting with the model (streamed from the SSD):

    ./setup.sh run
    # or directly:  ./scripts/05-run.sh

EOF
fi
