#!/usr/bin/env bash
# =============================================================================
# 02-install-tools.sh — install ONLY the build/runtime tools that are missing
# -----------------------------------------------------------------------------
# Cross-platform. Verified against colibri/c/setup.sh:
#   macOS  : clang (Xcode CLT) + libomp via Homebrew — NOT gcc
#   Linux  : gcc + OpenMP (libgomp ships with gcc) + make + git, via the
#            native package manager (apt/dnf/yum/pacman/zypper)
#   WSL2   : same as Linux
#   Windows: not automated here (upstream has a MinGW-w64 port) — use WSL2
# The `coli` launcher is a Python 3 script, so python3 is a RUNTIME dep. The
# model is fetched with the `hf` CLI (+ optional hf_transfer accelerator).
# Every step is idempotent — installed tools are skipped.
# =============================================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/common.sh
source "$SCRIPT_DIR/../lib/common.sh"
load_config

step "Phase 2 — install build & runtime tools ( os=$OS_ID )"

if [ "$OS_ID" = "windows" ]; then
  die "Native Windows shell — install WSL2 (wsl --install), re-run inside it, or build upstream manually with MinGW-w64 (see the colibri README)."
fi

if [ "$OS_ID" = "macos" ]; then
  # --- macOS: Xcode CLT (clang) + Homebrew + libomp + python3 -----------------

  # 1. Xcode Command Line Tools (clang + make)
  if xcode-select -p >/dev/null 2>&1 && require_cmd clang; then
    ok "Xcode Command Line Tools present ($(clang --version | head -1))"
  else
    warn "Xcode Command Line Tools missing (needed for clang + make)."
    run xcode-select --install || true
    warn "A macOS dialog may have opened. Finish that install, then re-run this script."
    is_dry || die "Waiting on Xcode CLT install."
  fi

  # 2. Homebrew
  if require_cmd brew; then
    ok "Homebrew present ($(brew --version | head -1))"
  else
    info "Installing Homebrew…"
    run_sh '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    # make brew available in this shell for the rest of the run
    if [ -x /opt/homebrew/bin/brew ]; then eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [ -x /usr/local/bin/brew ]; then eval "$(/usr/local/bin/brew shellenv)"; fi
  fi

  # 3. libomp (OpenMP for the clang build)
  if require_cmd brew && brew list libomp >/dev/null 2>&1; then
    ok "libomp already installed (multi-threaded engine build enabled)."
  else
    info "Installing libomp (OpenMP runtime for clang; without it the engine builds single-threaded)…"
    run brew install libomp
  fi

  # 4. python3 (runtime dep of the `coli` launcher)
  if require_cmd python3; then
    ok "python3 present ($(python3 --version 2>&1))"
  else
    info "Installing python3 via Homebrew…"
    run brew install python
  fi

else
  # --- Linux / WSL2: gcc toolchain + git + python3 + pip ----------------------
  # OpenMP note: libgomp ships with gcc; upstream c/setup.sh verifies it at build.
  PKG=""
  for p in apt-get dnf yum pacman zypper; do
    if require_cmd "$p"; then PKG="$p"; break; fi
  done
  SUDO=""
  if [ "$(id -u)" != "0" ]; then
    if require_cmd sudo; then SUDO="sudo"
    else warn "Not root and no sudo — if packages are missing you must install them manually."; fi
  fi

  pkg_install_all() {
    case "$PKG" in
      apt-get) run_sh "$SUDO apt-get update -qq && $SUDO apt-get install -y build-essential git python3 python3-pip" ;;
      dnf|yum) run_sh "$SUDO $PKG install -y gcc gcc-c++ make git python3 python3-pip" ;;
      pacman)  run_sh "$SUDO pacman -S --noconfirm --needed base-devel git python python-pip" ;;
      zypper)  run_sh "$SUDO zypper install -y gcc gcc-c++ make git python3 python3-pip" ;;
      *) warn "No supported package manager found (apt/dnf/yum/pacman/zypper)."
         warn "Install manually: gcc (with OpenMP/libgomp), make, git, python3, pip."
         return 1 ;;
    esac
  }

  MISSING=0
  for c in gcc make git python3; do
    if require_cmd "$c"; then ok "$c present"; else warn "$c missing"; MISSING=1; fi
  done
  if python3 -m pip --version >/dev/null 2>&1; then ok "pip present"; else warn "pip missing"; MISSING=1; fi

  if [ "$MISSING" = "1" ]; then
    info "Installing missing toolchain via ${PKG:-<none>}…"
    pkg_install_all || die "Toolchain incomplete — install the packages above and re-run."
  fi
fi

# --- shared: Hugging Face CLI + hf_transfer -----------------------------------
# The modern CLI binary is `hf` (huggingface-cli is deprecated). hf_transfer is
# the Rust accelerator toggled by HF_HUB_ENABLE_HF_TRANSFER=1.
if require_cmd hf; then
  ok "hf CLI present ($(hf version 2>/dev/null | head -1 || echo installed))"
else
  info "Installing huggingface_hub[cli] + hf_transfer (user site)…"
  # PEP 668: Homebrew/Debian python may be 'externally managed'. Try --user first,
  # fall back to --break-system-packages if pip refuses.
  if ! run_sh 'python3 -m pip install -U --user "huggingface_hub[cli]" hf_transfer'; then
    warn "Plain --user install failed (likely PEP 668). Retrying with --break-system-packages…"
    run_sh 'python3 -m pip install -U --user --break-system-packages "huggingface_hub[cli]" hf_transfer'
  fi
fi

# --- make sure `hf` is on PATH -------------------------------------------------
if ! require_cmd hf && ! is_dry; then
  USER_BIN="$(python3 -m site --user-base 2>/dev/null)/bin"
  if [ -x "$USER_BIN/hf" ]; then
    warn "'hf' installed to $USER_BIN but that dir is not on PATH."
    warn "Add it (the 04-download step also exports it into $(shell_rc_file)):"
    warn "    export PATH=\"$USER_BIN:\$PATH\""
  fi
fi

ok "Phase 2 complete — toolchain ready."
