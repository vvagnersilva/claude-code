#!/usr/bin/env bash
# =============================================================================
# 01-check-drive.sh — validate the target drive before anything heavy happens
# -----------------------------------------------------------------------------
# Cross-platform (macOS / Linux / WSL2). Checks, in order:
#   1. the target volume ($MOUNT) is mounted AND is a real external/dedicated
#      drive (never the boot disk)
#   2. its filesystem is sane for streaming — APFS on macOS; ext4/xfs/btrfs on
#      Linux; refuses exfat/ntfs/vfat/drvfs unless ALLOW_SLOW_FS=1
#   3. it has >= $MIN_FREE_GB free
#   4. a quick sequential write/read speed probe (warns if too slow to stream)
# Idempotent + read-only except for a temporary speed-test file it deletes.
# =============================================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/common.sh
source "$SCRIPT_DIR/../lib/common.sh"
load_config

step "Phase 1 — target drive check ( $MOUNT, os=$OS_ID )"

if [ "$OS_ID" = "windows" ]; then
  die "Native Windows shell detected — run this from WSL2 instead (wsl --install; see README)."
fi

# --- 0. list what's actually attached, to help the user ----------------------
info "Disks currently attached:"
case "$OS_ID" in
  macos)
    if require_cmd diskutil; then
      diskutil list external physical 2>/dev/null | sed 's/^/    /' || true
    else
      warn "diskutil not found (are you on macOS?)"
    fi ;;
  linux|wsl)
    if require_cmd lsblk; then
      lsblk -o NAME,SIZE,TRAN,ROTA,FSTYPE,MOUNTPOINT 2>/dev/null | sed 's/^/    /' || true
    fi ;;
esac

# --- 1. mounted + external ---------------------------------------------------
if ! is_external_mount "$MOUNT"; then
  if is_dry; then
    warn "[dry-run] Target '$MOUNT' not usable right now: $REASON"
    info "[dry-run] Once $MOUNT is a mounted external NVMe drive, this phase would then:"
    info "          • confirm the filesystem (APFS on macOS / ext4-class on Linux)"
    info "          • confirm >= ${MIN_FREE_GB} GB free"
    info "          • probe sequential write/read speed and warn if < ${MIN_WRITE_MBPS} MB/s"
    ok "[dry-run] Phase 1 would validate the drive (nothing checked live — drive absent)."
    exit 0
  fi
  err "Target '$MOUNT' is not usable: $REASON"
  case "$OS_ID" in
    macos) cat <<EOF

  How to fix (macOS):
    • Plug the NVMe SSD into a Thunderbolt 3/4 or USB4 port.
    • If it is unformatted or ExFAT, format it as APFS and name it '$VOLUME_NAME':
        diskutil list external physical         # find its identifier, e.g. disk4
        diskutil eraseDisk APFS "$VOLUME_NAME" GPT /dev/diskN   # ⚠ ERASES the disk
      (or use Disk Utility.app → Erase → Format: APFS, Name: $VOLUME_NAME)
    • Re-run this script.

  You can also point at a differently named volume:
        VOLUME_NAME=MyDrive ./scripts/01-check-drive.sh
EOF
    ;;
    linux|wsl) cat <<EOF

  How to fix (Linux/WSL2):
    • Plug the NVMe SSD (USB4/Thunderbolt) and find it:   lsblk -o NAME,SIZE,TRAN,MOUNTPOINT
    • Format it ext4 (⚠ ERASES it):                       sudo mkfs.ext4 -L $VOLUME_NAME /dev/sdX
    • Mount it:   udisksctl mount -b /dev/sdX1
                  (or: sudo mkdir -p $MOUNT && sudo mount /dev/sdX1 $MOUNT)
    • If it mounts somewhere else, set MOUNT_POINT=/that/path in config.local.env.
    • If the target is a dedicated INTERNAL secondary NVMe (fine on Linux),
      set ALLOW_INTERNAL_TARGET=1 in config.local.env.
    • WSL2: do NOT use /mnt/c-style drvfs paths — attach the disk natively
      (wsl --mount) or keep the model on the ext4 VHD.
EOF
    ;;
  esac
  exit 1
fi
ok "Mounted target drive: $MOUNT  (device $(device_of "$MOUNT"))"

# --- 2. filesystem sanity ------------------------------------------------------
# Refuse slow/corruption-prone filesystems unless the user opts out.
slow_fs_gate() {
  if [ "${ALLOW_SLOW_FS:-0}" = "1" ]; then
    warn "ALLOW_SLOW_FS=1 set — proceeding on '$1' at your own risk."
  else
    die "Refusing to proceed on '$1'. Reformat (see above) or set ALLOW_SLOW_FS=1 in config.local.env to override."
  fi
}

FS="$(fs_of "$MOUNT")"
FS_L="$(printf '%s' "$FS" | tr '[:upper:]' '[:lower:]')"
info "Filesystem: ${FS:-unknown}"

case "$OS_ID" in
  macos)
    case "$FS_L" in
      *apfs*)
        ok "APFS confirmed — correct filesystem for SSD streaming (TRIM + journaling)."
        ;;
      *exfat*|*msdos*|*fat*)
        warn "Filesystem is '$FS' (ExFAT/FAT). This is measurably slower for heavy"
        warn "random reads on macOS and has higher corruption risk (no journaling)."
        warn "Reformat as APFS before downloading the model:"
        warn "    diskutil eraseVolume APFS \"$VOLUME_NAME\" \"$(diskutil_field "$MOUNT" 'Device Node')\"   # ⚠ ERASES this volume"
        slow_fs_gate "$FS"
        ;;
      *)
        warn "Filesystem '${FS:-unknown}' is neither APFS nor ExFAT — proceed with caution; APFS is strongly recommended."
        ;;
    esac ;;
  linux|wsl)
    case "$FS_L" in
      ext4|xfs|btrfs|f2fs)
        ok "$FS confirmed — fine for SSD streaming on Linux."
        ;;
      exfat|vfat|ntfs|fuseblk|drvfs|9p|v9fs)
        warn "Filesystem '$FS' is slow and/or corruption-prone for heavy random reads on Linux."
        if [ "$OS_ID" = "wsl" ]; then
          warn "On WSL2, drvfs/9p (/mnt/c-style Windows mounts) is CATASTROPHICALLY slow for"
          warn "expert streaming — attach the disk natively (wsl --mount) or use the ext4 VHD."
        fi
        warn "Reformat ext4 (⚠ ERASES it):  sudo mkfs.ext4 -L $VOLUME_NAME /dev/sdX"
        slow_fs_gate "$FS"
        ;;
      *)
        warn "Filesystem '${FS:-unknown}' unrecognised — ext4/xfs recommended for streaming."
        ;;
    esac
    # spinning-disk check: streaming needs NVMe-class random reads
    DEV="$(device_of "$MOUNT")"
    PD="$(parent_disk_of "$DEV")"
    BASE="$DEV"; if [ -n "$PD" ]; then BASE="/dev/$PD"; fi
    ROTA="$(lsblk_flag "$BASE" ROTA)"
    if [ "$ROTA" = "1" ]; then
      warn "Spinning HDD detected (ROTA=1). Expert streaming does ~11 GB of random reads"
      warn "per cold token — an HDD will land far below the slowest published datapoint."
    fi
    ;;
esac

# --- 3. free space -----------------------------------------------------------
FREE_GB="$(free_gb_of "$MOUNT")"
info "Free space: ${FREE_GB} GB (need >= ${MIN_FREE_GB} GB)"
if [ "${FREE_GB:-0}" -lt "$MIN_FREE_GB" ]; then
  if is_dry; then warn "[dry-run] would fail: only ${FREE_GB} GB free (< ${MIN_FREE_GB})"
  else die "Not enough free space on $MOUNT: ${FREE_GB} GB < ${MIN_FREE_GB} GB. Free space or use a bigger SSD."; fi
else
  ok "Free space is sufficient."
fi

# --- 4. speed probe ----------------------------------------------------------
if is_dry; then
  info "[dry-run] would write+read a 1 GB test file at $MOUNT/.coli_speedtest and measure MB/s"
else
  TESTFILE="$MOUNT/.coli_speedtest"
  case "$OS_ID" in macos) DD_BS=1m ;; *) DD_BS=1M ;; esac
  info "Probing sequential speed (1 GB write+read at $TESTFILE)…"
  trap 'rm -f "$TESTFILE" 2>/dev/null || true' EXIT
  W_OUT="$(dd if=/dev/zero of="$TESTFILE" bs=$DD_BS count=1024 2>&1 || true)"
  sync
  R_OUT="$(dd if="$TESTFILE" of=/dev/null bs=$DD_BS 2>&1 || true)"
  rm -f "$TESTFILE"; trap - EXIT
  W_MBPS="$(parse_dd_mbps "$W_OUT")"
  R_MBPS="$(parse_dd_mbps "$R_OUT")"
  info "Sequential write: ${W_MBPS} MB/s   |   read: ${R_MBPS} MB/s (read may be page-cache influenced)"
  if [ "${W_MBPS:-0}" -eq 0 ]; then
    warn "Could not parse dd output — speed unknown; verify the link manually (TB3/4 or USB4 NVMe expected)."
  elif [ "$W_MBPS" -lt "$MIN_WRITE_MBPS" ]; then
    warn "Write speed ${W_MBPS} MB/s < ${MIN_WRITE_MBPS} MB/s threshold."
    warn "This looks like a USB 3.0 / SATA link. Expert streaming (~11 GB of random"
    warn "reads per token on a cold cache) will be very slow. For usable token rates"
    warn "use an NVMe SSD in a Thunderbolt 3/4 or USB4 enclosure (~1500-2800 MB/s)."
  else
    ok "Drive is fast enough for streaming (>= ${MIN_WRITE_MBPS} MB/s write)."
  fi
fi

ok "Phase 1 complete — drive $MOUNT is ready."
