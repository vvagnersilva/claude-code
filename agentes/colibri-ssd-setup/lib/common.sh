#!/usr/bin/env bash
# =============================================================================
# lib/common.sh — shared helpers for every colibri-ssd-setup script
# -----------------------------------------------------------------------------
# Sourced by setup.sh and scripts/0*.sh. Provides:
#   - coloured logging (info/ok/warn/err/die/step)
#   - OS/platform detection: macOS, Linux, WSL2, Windows shells (OS_ID/ARCH_ID)
#   - config loading + derived paths (mount root resolved per OS)
#   - dry-run plumbing (COLIBRI_DRY_RUN=1)  -> run()/run_sh()
#   - external-drive guardrails (assert_external_mount / free space)
#   - portable disk helpers (device / free space / filesystem / dd-rate parse)
# Portability: written for bash 3.2+ (macOS default bash) — no associative
# arrays, no ${var,,}; GNU vs BSD differences (stat, dd, df) live in helpers.
# =============================================================================

# ---- locate repo root (this file lives in <root>/lib/) ----------------------
_COMMON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$_COMMON_DIR/.." && pwd)"
export REPO_ROOT

# ---- colours (disabled when not a TTY) --------------------------------------
if [ -t 1 ]; then
  _C_RESET=$'\033[0m'; _C_DIM=$'\033[2m'; _C_BOLD=$'\033[1m'
  _C_RED=$'\033[31m'; _C_GRN=$'\033[32m'; _C_YEL=$'\033[33m'; _C_BLU=$'\033[34m'; _C_CYN=$'\033[36m'
else
  _C_RESET=""; _C_DIM=""; _C_BOLD=""; _C_RED=""; _C_GRN=""; _C_YEL=""; _C_BLU=""; _C_CYN=""
fi

info() { printf '%s\n' "${_C_CYN}•${_C_RESET} $*"; }
ok()   { printf '%s\n' "${_C_GRN}✓${_C_RESET} $*"; }
warn() { printf '%s\n' "${_C_YEL}⚠${_C_RESET}  $*" >&2; }
err()  { printf '%s\n' "${_C_RED}✗${_C_RESET} $*" >&2; }
die()  { err "$*"; exit 1; }
step() { printf '\n%s\n' "${_C_BOLD}${_C_BLU}==>${_C_RESET} ${_C_BOLD}$*${_C_RESET}"; }

# ---- dry-run ----------------------------------------------------------------
# Set COLIBRI_DRY_RUN=1 to print commands instead of executing them.
: "${COLIBRI_DRY_RUN:=0}"
is_dry() { [ "${COLIBRI_DRY_RUN}" = "1" ]; }

# run <argv...> : execute a simple command, or print it in dry-run.
run() {
  if is_dry; then printf '%s\n' "${_C_DIM}[dry-run] $*${_C_RESET}"; return 0; fi
  "$@"
}

# run_sh "<shell string>" : execute a command that needs shell features
# (pipes, redirects, env-prefixes), or print it in dry-run.
run_sh() {
  if is_dry; then printf '%s\n' "${_C_DIM}[dry-run] $*${_C_RESET}"; return 0; fi
  bash -c "$*"
}

require_cmd() { command -v "$1" >/dev/null 2>&1; }

# ---- OS / platform detection -------------------------------------------------
# Sets/exports:
#   OS_ID   : macos | linux | wsl | windows | unknown
#   ARCH_ID : arm64 | x86_64 | aarch64 | ...   (uname -m; Darwin arm64 kept as-is)
detect_os() {
  local u; u="$(uname -s 2>/dev/null || echo unknown)"
  case "$u" in
    Darwin) OS_ID="macos" ;;
    Linux)
      if grep -qi microsoft /proc/version 2>/dev/null; then OS_ID="wsl"; else OS_ID="linux"; fi ;;
    MINGW*|MSYS*|CYGWIN*) OS_ID="windows" ;;
    *) OS_ID="unknown" ;;
  esac
  ARCH_ID="$(uname -m 2>/dev/null || echo unknown)"
  export OS_ID ARCH_ID
}

# total physical RAM in GB (integer; 0 if unknown)
total_ram_gb() {
  case "${OS_ID:-}" in
    macos)     sysctl -n hw.memsize 2>/dev/null | awk '{printf "%d", $1/1024/1024/1024}' ;;
    linux|wsl) awk '/^MemTotal/{printf "%d", $2/1024/1024}' /proc/meminfo 2>/dev/null ;;
    *)         echo 0 ;;
  esac
}

# file size in bytes — BSD stat first, then GNU stat
stat_size() { stat -f%z "$1" 2>/dev/null || stat -c%s "$1" 2>/dev/null || echo 0; }

# where removable volumes mount on this OS (used when MOUNT_POINT is unset)
default_mount_root() {
  case "${OS_ID:-}" in
    macos) echo "/Volumes" ;;
    wsl)   echo "/mnt" ;;
    linux)
      if   [ -d "/run/media/${USER:-root}" ]; then echo "/run/media/${USER:-root}"
      elif [ -d "/media/${USER:-root}" ];     then echo "/media/${USER:-root}"
      elif [ -d /media ];                     then echo "/media"
      else echo "/mnt"; fi ;;
    *) echo "/mnt" ;;
  esac
}

# which shell rc file to persist env vars into on this OS
shell_rc_file() {
  case "${OS_ID:-}" in
    macos) echo "$HOME/.zshrc" ;;
    *)
      if [ "$(basename "${SHELL:-/bin/bash}")" = "zsh" ]; then echo "$HOME/.zshrc"
      else echo "$HOME/.bashrc"; fi ;;
  esac
}

# ---- config -----------------------------------------------------------------
load_config() {
  [ -f "$REPO_ROOT/config.env" ] || die "config.env not found at $REPO_ROOT/config.env"
  # shellcheck disable=SC1090
  source "$REPO_ROOT/config.env"
  # local override wins if present
  if [ -f "$REPO_ROOT/config.local.env" ]; then
    # shellcheck disable=SC1090
    source "$REPO_ROOT/config.local.env"
  fi

  detect_os

  # ---- resolve target mount (explicit MOUNT_POINT wins; else per-OS root) ----
  if [ -n "${MOUNT_POINT:-}" ]; then
    MOUNT="$MOUNT_POINT"
  else
    MOUNT="$(default_mount_root)/${VOLUME_NAME}"
  fi

  # ---- resolve the --ram budget (RAM_GB=auto -> total minus OS headroom) ----
  if [ "${RAM_GB:-auto}" = "auto" ]; then
    local _t; _t="$(total_ram_gb)"; : "${_t:=0}"
    if   [ "$_t" -ge 24 ]; then RAM_GB=$(( _t - 8 ))
    elif [ "$_t" -ge 16 ]; then RAM_GB=$(( _t - 6 ))
    elif [ "$_t" -gt 0 ];  then RAM_GB=8      # below the engine's 16 GB minimum — 00-detect flags this
    else RAM_GB=16; fi
  fi

  # ---- derived paths (all on the target drive) ----
  COLIBRI_HOME="${MOUNT}/colibri"
  ENGINE_DIR="${COLIBRI_HOME}/engine"      # git clone of the colibri repo
  BUILD_DIR="${ENGINE_DIR}/c"              # where setup.sh / make / coli live
  MODELS_DIR="${COLIBRI_HOME}/models"
  MODEL_PATH="${MODELS_DIR}/${MODEL_DIR}"
  HF_HOME_DIR="${COLIBRI_HOME}/hf_cache"
  export MOUNT COLIBRI_HOME ENGINE_DIR BUILD_DIR MODELS_DIR MODEL_PATH HF_HOME_DIR RAM_GB
}

# ---- disk helpers -----------------------------------------------------------
# NOTE: these MUST always return 0. They are used in `var="$(helper ...)"`
# assignments, and with `set -eo pipefail` a failing df/diskutil (e.g. an
# absent mount) would otherwise abort the whole script. The trailing `|| true`
# keeps stdout intact while swallowing the non-zero exit.

# device backing a path, e.g. /dev/disk4s2 or /dev/nvme1n1p1 (empty if missing)
device_of() { df -P "$1" 2>/dev/null | awk 'NR==2{print $1}' || true; }

# free space in GB (integer) for a mounted path
free_gb_of() {
  # df -Pk -> 1024-byte blocks; col 4 = available
  df -Pk "$1" 2>/dev/null | awk 'NR==2{printf "%d", $4/1024/1024}' || true
}

# read a single field from `diskutil info` (macOS only; case-insensitive key)
diskutil_field() {
  # $1 = mount/device, $2 = field label (e.g. "Internal")
  diskutil info "$1" 2>/dev/null \
    | awk -F: -v k="$2" 'tolower($1) ~ tolower("^[[:space:]]*"k"[[:space:]]*$"){sub(/^[[:space:]]+/,"",$2); print $2; exit}' || true
}

# Linux: name of the parent disk of a partition device (e.g. nvme0n1p2 -> nvme0n1)
parent_disk_of() {
  require_cmd lsblk || { echo ""; return 0; }
  lsblk -no PKNAME "$1" 2>/dev/null | head -1 | tr -d ' ' || true
}

# Linux: read one lsblk column for a device (e.g. TRAN, RM, HOTPLUG, ROTA)
lsblk_flag() {
  require_cmd lsblk || { echo ""; return 0; }
  lsblk -dno "$2" "$1" 2>/dev/null | head -1 | tr -d ' ' || true
}

# filesystem type of a mounted path (APFS/ExFAT on macOS; ext4/xfs/... on Linux)
fs_of() {
  local f=""
  case "${OS_ID:-}" in
    macos)
      f="$(diskutil_field "$1" 'File System Personality')"
      [ -n "$f" ] || f="$(diskutil_field "$1" 'Type (Bundle)')" ;;
    *)
      f="$(findmnt -no FSTYPE --target "$1" 2>/dev/null | head -1 || true)"
      [ -n "$f" ] || f="$(stat -f -c %T "$1" 2>/dev/null || true)" ;;
  esac
  printf '%s' "$f"
}

# parse `dd` rate output -> integer MB/s on stdout (0 if unparseable)
#   BSD dd : "1073741824 bytes transferred in 0.502 secs (2138912190 bytes/sec)"
#   GNU dd : "1073741824 bytes (1.1 GB, 1.0 GiB) copied, 1.23 s, 871 MB/s"
parse_dd_mbps() {
  printf '%s\n' "${1:-}" | awk '
    /bytes\/sec/ { n = split($0, a, /[()]/); if (n >= 2) { split(a[2], b, " "); printf "%d\n", b[1]/1000000; f=1; exit } }
    /copied/     { v = $(NF-1); u = $NF
                   if (u ~ /^GB/)      printf "%d\n", v*1000
                   else if (u ~ /^MB/) printf "%d\n", v
                   else if (u ~ /^kB/) printf "%d\n", v/1000
                   else                print 0
                   f=1; exit }
    END { if (!f) print 0 }'
}

# Is $1 a *separately mounted external/dedicated* volume — i.e. safe for the
# ~372 GB download, never the boot drive?
# Prints nothing; returns 0 (safe) or 1 (not safe) and sets REASON.
is_external_mount() {
  REASON=""
  local m="$1"
  if [ ! -d "$m" ]; then REASON="$m does not exist (drive not mounted?)"; return 1; fi

  local dev_root dev_m
  dev_root="$(device_of /)"
  dev_m="$(device_of "$m")"
  if [ -z "$dev_m" ]; then REASON="cannot resolve a device for $m"; return 1; fi
  if [ "$dev_m" = "$dev_root" ]; then
    REASON="$m is on the SAME device as / ($dev_root) — it is NOT a separately mounted drive"
    return 1
  fi

  case "${OS_ID:-}" in
    macos)
      # diskutil cross-check: Internal must be No / Device Location External.
      # This also catches other APFS volumes of the internal boot container.
      local internal loc
      internal="$(diskutil_field "$m" 'Internal')"
      loc="$(diskutil_field "$m" 'Device Location')"
      if [ "${internal}" = "Yes" ] || [ "${loc}" = "Internal" ]; then
        REASON="diskutil reports $m as an INTERNAL disk (Internal=${internal:-?}, Location=${loc:-?})"
        return 1
      fi
      return 0 ;;
    linux|wsl)
      case "$dev_m" in
        /dev/*) : ;;
        *) return 0 ;;   # drvfs/9p/network style device — separate from /; 01 flags slow FS
      esac
      # same *physical disk* as / (different partition) is still the boot drive
      local pd_root pd_m base
      pd_root="$(parent_disk_of "$dev_root")"
      pd_m="$(parent_disk_of "$dev_m")"
      if [ -n "$pd_m" ] && [ "$pd_m" = "$pd_root" ]; then
        REASON="$m lives on the same physical disk as / (/dev/$pd_m) — that IS the boot drive"
        return 1
      fi
      base="$dev_m"; if [ -n "$pd_m" ]; then base="/dev/$pd_m"; fi
      # external heuristics: USB transport, removable, or hot-pluggable (TB/USB4)
      local tran rmv hot
      tran="$(lsblk_flag "$base" TRAN)"
      rmv="$(lsblk_flag "$base" RM)"
      hot="$(lsblk_flag "$base" HOTPLUG)"
      if [ "$tran" = "usb" ] || [ "$rmv" = "1" ] || [ "$hot" = "1" ]; then return 0; fi
      if [ "${ALLOW_INTERNAL_TARGET:-0}" = "1" ]; then return 0; fi
      REASON="$base is not detected as external/hot-pluggable (TRAN=${tran:-?}, RM=${rmv:-?}, HOTPLUG=${hot:-?}). If it IS a dedicated data drive (common on Linux), set ALLOW_INTERNAL_TARGET=1 in config.local.env"
      return 1 ;;
    windows)
      REASON="native Windows shells are not supported by this installer — use WSL2 (see README)"
      return 1 ;;
    *) return 0 ;;
  esac
}

# Hard guardrail used before ANY heavy write to the target drive. Exits on failure.
# In --dry-run it only reports what it would enforce (the drive may be absent).
assert_external_mount() {
  load_config >/dev/null 2>&1 || true
  if is_external_mount "$MOUNT"; then
    return 0
  fi
  if is_dry; then
    warn "[dry-run] drive guardrail would enforce: $REASON"
    warn "[dry-run] (live run aborts here unless $MOUNT is a mounted external/dedicated drive)"
    return 0
  fi
  err "Drive guardrail FAILED: $REASON"
  err "Refusing to write to a path that would land on the internal/boot drive."
  err "Mount an external SSD as '$VOLUME_NAME' (see: ./scripts/01-check-drive.sh) and retry."
  exit 1
}
