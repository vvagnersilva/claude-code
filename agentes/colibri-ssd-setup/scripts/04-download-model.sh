#!/usr/bin/env bash
# =============================================================================
# 04-download-model.sh — download the ~372 GB int4 model ONTO THE SSD (safely)
# -----------------------------------------------------------------------------
# HARD GUARDRAILS (this script refuses to run otherwise):
#   • the destination must resolve to the external SSD, never the internal drive
#   • >= $MIN_FREE_GB must be free on that SSD
# It sets HF_HOME on the SSD (persisted into the shell rc in a marked block),
# enables hf_transfer when available, downloads with auto-resume via `hf`, then
# verifies the int8 MTP head sizes (the whole point of the mateogrgic clone).
# =============================================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/common.sh
source "$SCRIPT_DIR/../lib/common.sh"
load_config

step "Phase 4 — download model to SSD ( $MODEL_PATH )"

# --- GUARDRAIL 1: destination must be the external SSD -----------------------
assert_external_mount
case "$MODEL_PATH" in
  "$MOUNT"/*) : ;;   # good: under the external mount
  *) die "GUARDRAIL: MODEL_PATH ($MODEL_PATH) is not under the target mount $MOUNT. Aborting." ;;
esac
if [ "$OS_ID" = "macos" ]; then
  # macOS-only extra belt: external volumes always live under /Volumes
  case "$MODEL_PATH" in
    /Volumes/*) : ;;
    *) die "GUARDRAIL: MODEL_PATH ($MODEL_PATH) is not under /Volumes — refusing (would risk the internal drive)." ;;
  esac
fi
ok "Destination guardrail passed — $MODEL_PATH is on external device $(device_of "$MOUNT")."

# --- GUARDRAIL 2: free space -------------------------------------------------
FREE_GB="$(free_gb_of "$MOUNT")"
if [ "${FREE_GB:-0}" -lt "$MIN_FREE_GB" ]; then
  if is_dry; then warn "[dry-run] space guardrail would fail: ${FREE_GB:-0} GB free (< ${MIN_FREE_GB})"
  else die "GUARDRAIL: only ${FREE_GB} GB free on $MOUNT, need >= ${MIN_FREE_GB} GB. Aborting before download."; fi
else
  ok "Space guardrail passed — ${FREE_GB} GB free (need ${MIN_FREE_GB})."
fi

run mkdir -p "$MODELS_DIR" "$HF_HOME_DIR"

# --- resolve hf binary -------------------------------------------------------
HF_BIN="$(command -v hf 2>/dev/null || true)"
if [ -z "$HF_BIN" ]; then
  CAND="$(python3 -m site --user-base 2>/dev/null)/bin/hf"
  [ -x "$CAND" ] && HF_BIN="$CAND"
fi
if [ -z "$HF_BIN" ] && ! is_dry; then
  die "hf CLI not found. Run ./scripts/02-install-tools.sh first."
fi
HF_BIN="${HF_BIN:-hf}"

# --- HF_HOME on the SSD + hf_transfer ---------------------------------------
export HF_HOME="$HF_HOME_DIR"
info "HF_HOME set to $HF_HOME (keeps HF's cache off the internal drive)."

HF_XFER=0
if [ "${HF_TRANSFER}" = "1" ] && python3 -c 'import hf_transfer' >/dev/null 2>&1; then
  export HF_HUB_ENABLE_HF_TRANSFER=1
  HF_XFER=1
  ok "hf_transfer enabled (faster multi-threaded download)."
else
  info "hf_transfer not enabled (package missing or disabled) — using standard download."
fi

# --- persist HF_HOME (+ PATH for user-installed hf) into the shell rc --------
# (zshrc on macOS, bashrc/zshrc on Linux — resolved by shell_rc_file)
RC_FILE="$(shell_rc_file)"
persist_shell_rc() {
  local rc="$RC_FILE"
  local begin="# >>> colibri-ssd-setup >>>"
  local end="# <<< colibri-ssd-setup <<<"
  local userbin; userbin="$(python3 -m site --user-base 2>/dev/null)/bin"
  touch "$rc"
  awk -v b="$begin" -v e="$end" '
    $0==b{skip=1} skip==0{print} $0==e{skip=0}
  ' "$rc" > "$rc.colibri.tmp"
  {
    cat "$rc.colibri.tmp"
    printf '%s\n' "$begin"
    printf 'export HF_HOME="%s"\n' "$HF_HOME_DIR"
    [ "$HF_XFER" = "1" ] && printf 'export HF_HUB_ENABLE_HF_TRANSFER=1\n'
    printf 'export PATH="%s:$PATH"\n' "$userbin"
    printf '%s\n' "$end"
  } > "$rc"
  rm -f "$rc.colibri.tmp"
}
if is_dry; then
  info "[dry-run] would write a marked colibri-ssd-setup block (HF_HOME, PATH) into $RC_FILE"
else
  persist_shell_rc
  ok "Persisted HF_HOME (and hf PATH) into $RC_FILE (marked block, idempotent)."
fi

# --- the download ------------------------------------------------------------
info "Downloading '$MODEL_REPO' (~372 GB, resumable) → $MODEL_PATH"
warn "This is a very large, long-running download. It resumes automatically if interrupted."
XFER_ENV=""
[ "$HF_XFER" = "1" ] && XFER_ENV="HF_HUB_ENABLE_HF_TRANSFER=1 "
run_sh "HF_HOME='$HF_HOME' ${XFER_ENV}'$HF_BIN' download '$MODEL_REPO' --local-dir '$MODEL_PATH'"

# --- verify int8 MTP heads (the reason this clone exists) --------------------
# Expected int8 sizes (bytes): 3527131672 / 5366238584 / 1065950496
# Broken int4 sizes (bytes):   1765523544 / 2686077736 / 536747200
if is_dry; then
  info "[dry-run] would verify out-mtp-* file sizes are the int8 set (3527131672/5366238584/1065950496)"
else
  info "Verifying int8 MTP head sizes…"
  INT8="3527131672 5366238584 1065950496"
  INT4="1765523544 2686077736 536747200"
  bad=0; found=0
  for f in "$MODEL_PATH"/out-mtp-*; do
    [ -e "$f" ] || continue
    found=$((found+1))
    sz="$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null)"
    if printf '%s' "$INT4" | grep -qw "$sz"; then
      err "  $(basename "$f") = $sz bytes  -> INT4 (broken) MTP head!"
      bad=1
    elif printf '%s' "$INT8" | grep -qw "$sz"; then
      ok "  $(basename "$f") = $sz bytes  -> int8 (correct)"
    else
      warn "  $(basename "$f") = $sz bytes  -> unrecognised size (model may have changed upstream)"
    fi
  done
  if [ "$found" -eq 0 ]; then
    warn "No out-mtp-* files found under $MODEL_PATH — download may be incomplete; re-run to resume."
  elif [ "$bad" -eq 1 ]; then
    die "This copy has INT4 MTP heads — speculative decoding will sit at 0%. You downloaded the wrong repo. Fix MODEL_REPO in config.env."
  else
    ok "int8 MTP heads verified — speculative decoding will engage (39-59% acceptance)."
  fi
fi

ok "Phase 4 complete — model on SSD at $MODEL_PATH."
