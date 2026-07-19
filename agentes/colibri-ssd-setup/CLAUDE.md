# CLAUDE.md — how to run this setup end-to-end autonomously

You are a Claude Code session tasked with installing Colibrì + the GLM-5.2 model on an **external SSD** on this machine (macOS or Linux; WSL2 with caveats), using the scripts in this repo. Follow this exactly. **Never let the ~372 GB model download onto the internal drive** — the scripts guard against it; do not bypass those guards.

## FIRST ACTION — as soon as the session starts, profile the machine

Before reading anything else or installing anything, run:

```bash
./scripts/00-detect-machine.sh
```

It is **read-only** and prints: OS/CPU/RAM/GPU/SIMD profile, target-drive status, the **realistic tok/s band for THIS machine** (each band labelled measured vs extrapolated), a download-time estimate for the ~372 GB model, and a verdict. Then **report that profile and those expectations to the user BEFORE any install step**, so they can decide whether to proceed. Rules:

- Verdict `NOT VIABLE` or `BLOCKED` → **stop**. Explain why (RAM < 16 GB, x86 without AVX2, native Windows shell). On Windows, point to WSL2 (`wsl --install`).
- Verdict `DEMO-ONLY` → make sure the user explicitly understands (e.g. "a 300-token answer ≈ 25–100 min on this machine") **before** starting a ~372 GB download. Ask once; if they confirm, proceed.
- Never promise tok/s above the printed band. External-SSD datapoints are unpublished — say so.
- The same profile runs automatically at the start of `./setup.sh`; running it standalone first is still mandatory because the user must see it before phase 1 executes.

## 0. Ground truth (verified 2026-07-14 — do not "improve" these)
- Engine: `github.com/JustVugg/colibri`. Binary launcher is **`coli`** (Python 3), driving the compiled `glm`. **No `--model-path` flag** — the model dir is `COLI_MODEL=<dir>` (or `--model <dir>`).
- Build on macOS: **clang (Xcode CLT) + libomp**, via `cd c && ./setup.sh` → `make glm`. **Not gcc.** Apple Silicon can add `make glm METAL=1`.
- Build on Linux/WSL2: **gcc + libgomp** (OpenMP ships with gcc), same `cd c && ./setup.sh` flow; x86-64 **requires AVX2**. NVIDIA GPU boxes can add `make glm CUDA=1` (phase 3 does this automatically when `nvidia-smi` exists). Native Windows is NOT automated here.
- Model: **`mateogrgic/GLM-5.2-colibri-int4-with-int8-mtp`** (int8 MTP heads — required). The `jlnsrk/...` mirror has int4 MTP heads and is broken (0% speculative acceptance). Download with **`hf download`** (+ `HF_HUB_ENABLE_HF_TRANSFER=1`).
- Runtime: raise `ulimit -n` (mmaps 144+ shards; macOS default 256 is too low).

## 1. First: ask the user ONE thing if it's ambiguous
Which external volume to use. Default is `AI_DRIVE` (mounted at `/Volumes/AI_DRIVE`). If the user has a differently-named SSD, either edit `config.env` (`VOLUME_NAME=...`) or run with `VOLUME_NAME=TheirName`. If a suitable SSD is already mounted and obvious, just use it and tell them — don't over-ask.

Also confirm the SSD is **APFS** and has **≥ 400 GB free**. Phase 1 checks this; if it fails, help them format APFS (`diskutil eraseDisk APFS <name> GPT /dev/diskN` — this **erases** the disk, so confirm with the user first).

## 2. Always dry-run first
```bash
./setup.sh --dry-run
```
Read the output. It shows every command without executing. Confirm the paths all point under `/Volumes/<VOLUME_NAME>/colibri/...` and nothing targets the internal drive.

## 3. Run the phases
```bash
./setup.sh
```
This runs, in order and idempotently:
1. `01-check-drive.sh` — SSD present/external/APFS/space/speed. **If this fails, stop** and fix the drive; do not proceed.
2. `02-install-tools.sh` — clang(CLT)/brew/libomp/python3/hf. If Xcode CLT triggers a GUI installer, tell the user to finish it, then re-run `./setup.sh --from 2`.
3. `03-build-colibri.sh` — clone + build on the SSD. Validate: `<SSD>/colibri/engine/c/glm` exists and is executable.
4. `04-download-model.sh` — the long (~372 GB) download. It is resumable; if interrupted, just re-run `./setup.sh --from 4`. **Do not remove the guardrails.**

If any phase fails, the orchestrator prints `./setup.sh --from N` — use it after fixing the cause. Re-running is safe.

## 4. Validate each phase (don't trust, verify)
- After **1** (macOS): `diskutil info /Volumes/<VOL> | grep -E 'File System Personality|Internal'` → APFS + Internal: No. (Linux: `findmnt --target <MOUNT>` → ext4-class, and `lsblk -no TRAN` on the parent disk → usb, or ALLOW_INTERNAL_TARGET deliberately set.)
- After **3**: `test -x /Volumes/<VOL>/colibri/engine/c/glm && echo OK`.
- After **4**: `ls -l /Volumes/<VOL>/colibri/models/*/out-mtp-*` → sizes must be `3527131672 / 5366238584 / 1065950496` (int8). If they're `1765523544 / 2686077736 / 536747200` you got the wrong (int4) repo — fix `MODEL_REPO` and re-download.
- Free space sanity mid-download: `df -h /Volumes/<VOL>`.

## 5. Run the engine
```bash
./setup.sh run                       # interactive chat
./scripts/05-run.sh serve --port 8000   # OpenAI-compatible server
```
First generations are slow (cold cache). It warms up via `.coli_usage`. On Apple Silicon, Metal is used automatically when built (`ENABLE_METAL=auto`).

## 6. Guardrails you must never bypass
- The download must resolve to an external device. If `assert_external_mount` fails in a live run, the SSD is not mounted correctly — **fix the mount, don't edit the check**.
- Never set the model path to anything under `/Users`, `/tmp`, or the boot volume.
- Keep `--ram` conservative enough to avoid swap (swap writes wear the SSD).

## 7. Reporting back
Tell the user: which volume was used, that the engine built (`glm` present), model size on disk, int8-MTP verification result, and the exact command to chat. If you stopped early, say which phase and why.
