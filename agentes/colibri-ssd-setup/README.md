# colibri-ssd-setup

One-command installer that gets the **Colibrì** engine ([github.com/JustVugg/colibri](https://github.com/JustVugg/colibri)) compiled and the giant **GLM-5.2 (744B MoE, int4, ~372 GB)** model downloaded and running **entirely from an external SSD** — so the ~400 GB never touches your internal drive. Works on **macOS and Linux** (WSL2 with caveats; native Windows is not automated — upstream has a MinGW-w64 port for manual builds).

Colibrì keeps only the model's dense part (~9.9 GB at int4) in RAM and **streams the 21,504 routed experts from disk on demand**. The disk *is* the model store, so it must be a fast **NVMe SSD in a Thunderbolt 3/4 or USB4 enclosure**, formatted **APFS on macOS / ext4 on Linux**. This repo automates the whole thing, refuses to let the heavy download land on the internal disk, and — before anything else — **profiles your machine and tells you the realistic tok/s to expect** (phase 0).

> Every command, flag, path and size below was verified against the real Colibrì README, its `c/setup.sh`, the `coli` launcher, and the Hugging Face model pages on **2026-07-14**. See [Corrections to the original research](#corrections-to-the-original-research) for what the starting notes got wrong. Anything not confirmable is marked **NOT VERIFIED**.

---

## TL;DR

```bash
# 1. Plug in an NVMe SSD (TB3/4 or USB4), formatted APFS (macOS) / ext4 (Linux), named "AI_DRIVE"
# 2. From this repo:
./setup.sh detect        # phase 0: profile THIS machine + realistic tok/s expectations
./setup.sh --dry-run     # see exactly what it will do, change nothing
./setup.sh               # phases 1-4: check drive, install tools, build engine, download model
./setup.sh run           # launch the chat, streaming the model from the SSD
```

Nothing is hardcoded — edit `config.env` (volume name, RAM budget, model repo, …) or copy it to `config.local.env` to override.

---

## What you need

| Requirement | Why | Verified |
|---|---|---|
| **macOS** (Apple Silicon/Intel) or **Linux x86-64 with AVX2** (WSL2 works, slower) | Colibrì builds natively on both (clang+libomp / gcc+libgomp); native Windows only via upstream's manual MinGW port | ✅ README + a real `make glm` build on an M-series Mac here |
| **External NVMe SSD, Thunderbolt 3/4 or USB4** | experts are streamed from disk (~11 GB of random reads *per token* on a cold cache); USB 3.0/SATA is too slow | ✅ project datapoints are all multi-GB/s NVMe |
| **APFS filesystem** | faster + TRIM + journaled vs ExFAT on macOS | ✅ |
| **≥ 400 GB free** on the SSD | model container is ~372 GB + HF metadata + engine | ✅ (`c/setup.sh` says "~372 GB") |
| **≥ 16 GB RAM** | dense weights resident + expert LRU cache | ✅ |
| Xcode CLT (clang), Homebrew, **libomp**, python3 | build + run toolchain (installed for you) | ✅ (see corrections — it's **clang**, not gcc) |

---

## Quick start (step by step)

1. **Format the SSD** as APFS and name it `AI_DRIVE` (Disk Utility → Erase → APFS), or:
   ```bash
   diskutil list external physical            # find the disk id, e.g. disk4
   diskutil eraseDisk APFS AI_DRIVE GPT /dev/disk4   # ⚠ ERASES the whole disk
   ```
2. **Dry-run** to preview every action:
   ```bash
   ./setup.sh --dry-run
   ```
3. **Run it** (idempotent — safe to re-run; each phase skips finished work):
   ```bash
   ./setup.sh
   ```
   It stops at the first failing phase with a clear message and a `--from N` hint.
4. **Chat** (streams the model off the SSD):
   ```bash
   ./setup.sh run
   # or:  ./scripts/05-run.sh
   # or an OpenAI-compatible server:  ./scripts/05-run.sh serve --host 127.0.0.1 --port 8000
   ```

---

## What each phase does

| Phase | Script | Does |
|---|---|---|
| 0 | `scripts/00-detect-machine.sh` | **Read-only machine profile**: OS (macOS/Linux/WSL/Windows), CPU/SIMD (AVX2/AVX-512), RAM, GPU (Metal/CUDA), drive status — then prints the **realistic tok/s band for THIS machine** (measured vs extrapolated basis), download ETA, and a verdict (`USABLE` / `DEMO-ONLY` / `NOT VIABLE` / `BLOCKED`). Runs automatically at the start of `./setup.sh`; standalone via `./setup.sh detect` (add `--strict` to exit 1 on NOT VIABLE). |
| 1 | `scripts/01-check-drive.sh` | Detects external disks, confirms the target volume is a **mounted external** drive (not the internal one), verifies **APFS** (offers reformat guidance if ExFAT), checks **≥ 400 GB** free, and runs a quick **write/read speed probe** (warns if too slow to stream). |
| 2 | `scripts/02-install-tools.sh` | Installs only what's missing: **Xcode CLT (clang)**, **Homebrew**, **libomp** (OpenMP), **python3**, and the **`hf` CLI + hf_transfer**. Idempotent. |
| 3 | `scripts/03-build-colibri.sh` | Clones Colibrì **onto the SSD** and builds it with the project's own `c/setup.sh` (`make -s glm ARCH=native`). On Apple Silicon it also builds the experimental **Metal** engine. |
| 4 | `scripts/04-download-model.sh` | **Guardrails first** (destination must be the external SSD, ≥ 400 GB free), points **`HF_HOME` at the SSD** (persisted in `~/.zshrc`), downloads the model with **auto-resume**, then **verifies the int8 MTP head sizes**. |
| 5 | `scripts/05-run.sh` | Raises `ulimit -n` (the engine mmaps 144+ shards; macOS default 256 is too low), sets `COLI_MODEL`, and launches `./coli chat --ram N` (adding `COLI_METAL=1` on Apple Silicon, `PILOT=1` if enabled). |

### The download guardrail (why this repo is safe)

`04-download-model.sh` will **abort before writing a single byte** if:
- the target path does not resolve to a **separately-mounted external device** (it compares the device backing the path against the device backing `/`, and cross-checks `diskutil info … | Internal`), or
- the path isn't under `/Volumes/`, or
- there is **< 400 GB free**.

This is the core promise: **nothing heavy ever lands on the internal drive.** If the SSD isn't mounted, `/Volumes/AI_DRIVE/...` would otherwise be created on the boot disk — the guardrail catches exactly that.

---

## Configuration (`config.env`)

| Key | Default | Meaning |
|---|---|---|
| `VOLUME_NAME` | `AI_DRIVE` | external SSD volume; mount root resolved per OS (`/Volumes` on macOS, `/run/media/$USER` or `/media/$USER` on Linux, `/mnt` on WSL) |
| `MOUNT_POINT` | *(empty)* | full mount-path override when the drive mounts somewhere non-standard |
| `RAM_GB` | `auto` | `--ram` budget; `auto` = total RAM − ~8 GB OS headroom (24 GB → 16, 128 GB → 120), or set an integer |
| `ALLOW_INTERNAL_TARGET` | `0` | Linux only: accept a **dedicated internal** secondary NVMe as target (boot disk is always refused) |
| `ALLOW_SLOW_FS` | `0` | proceed on exfat/ntfs/vfat/drvfs instead of refusing (at your own risk) |
| `ENABLE_CUDA` | `auto` | Linux/WSL: build `make glm CUDA=1` when `nvidia-smi` is present |
| `MODEL_REPO` | `mateogrgic/GLM-5.2-colibri-int4-with-int8-mtp` | **the int8-MTP clone** (see corrections) |
| `MODEL_DIR` | `GLM-5.2-colibri-int4-with-int8-mtp` | sub-dir under `<SSD>/colibri/models` |
| `MIN_FREE_GB` | `400` | space guardrail |
| `MIN_WRITE_MBPS` | `700` | speed warning threshold |
| `ENABLE_METAL` | `auto` | build/use Metal on Apple Silicon |
| `ENABLE_PILOT` | `0` | `PILOT=1` router-lookahead prefetch (experimental) |
| `HF_TRANSFER` | `1` | use the Rust `hf_transfer` accelerator |

Layout created on the SSD:
```
/Volumes/AI_DRIVE/colibri/
├── engine/            # git clone of colibri (build dir: engine/c, binaries glm + coli)
├── models/GLM-5.2-colibri-int4-with-int8-mtp/   # ~372 GB
└── hf_cache/          # HF_HOME (kept off the internal drive)
```

---

## Corrections to the original research

The starting notes were mostly right on the **concept** but wrong on several **exact commands** — which is what actually breaks a setup. Corrected here, all verified against the live repo:

| # | Original note | Reality (verified) |
|---|---|---|
| 1 | Run with `PILOT=1 ./colibri --model-path ./models/<m> --ram 16` | Binary is **`coli`** (a **Python 3** launcher driving the compiled `glm`), not `colibri`. Model path comes from **`COLI_MODEL=<dir>`** env (or `--model <dir>`), **there is no `--model-path`**. Correct form: `COLI_MODEL=<dir> ./coli chat --ram 16`. `--ram`, `PILOT=1`, `.coli_usage` are all real. |
| 2 | Build with `make` in the repo root; `brew install gcc make python` | Build is **`cd c && ./setup.sh`** (then `make glm`). On macOS the toolchain is **clang (Xcode CLT) + libomp** — **not gcc** (gcc is the Linux/MinGW path). `c/setup.sh` explicitly checks `clang` and `libomp`. Apple Silicon adds `make glm METAL=1`. |
| 3 | Download via `huggingface-cli download …` | The modern CLI is **`hf download`** (`huggingface-cli` is deprecated). Add **`HF_HUB_ENABLE_HF_TRANSFER=1`** (+ `pip install hf_transfer`) for fast multi-threaded, resumable downloads. |
| 4 | (not mentioned) | The engine mmaps **144+ shards**; macOS default `RLIMIT_NOFILE` is **256** — too low. You must raise **`ulimit -n`** before running (the launcher's own source flags this). Handled in `05-run.sh`. |
| 5 | "clone comunitário com MTP heads int8" | Correct and important: **`mateogrgic/GLM-5.2-colibri-int4-with-int8-mtp`** is the community clone (matey-0) with int8 MTP heads. The original mirror **`jlnsrk/GLM-5.2-colibri-int4`** ships **int4** MTP heads → **0% draft acceptance**, speculation silently disabled. int8 → **39–59% acceptance, 2.2–2.8 tok/forward**. Verify via `out-mtp-*` sizes (`3527131672 / 5366238584 / 1065950496`). |

### Confirmed exactly as written
Colibrì is a pure-C, zero-dependency engine; dense part **~9.9 GB in RAM**; **21,504 routed experts (~370 GB) streamed from disk**; **GLM-5.2 744B MoE** and the int4 model repo both **exist**; **APFS > ExFAT** for macOS SSD streaming; NVMe over **TB3/4 or USB4** needed, USB 3.0 too slow; **`HF_HOME` on the SSD**; `.coli_usage` learning cache pins hot experts and the engine gets faster with use.

### NOT VERIFIED (be honest about these)
- **Exact token/s on *your* external SSD.** Real project datapoints are on *internal* SSDs (M5 Max internal ~4 GB/s cold → **1.06 tok/s** CPU, **1.83–2.06 tok/s** Metal; Mac Mini M4 Pro 48 GB → 0.30 tok/s Metal). An external TB3/4 NVMe (~2–3 GB/s) should land in a similar order of magnitude, but **no external-SSD datapoint is published** — treat throughput as unverified until you measure it (`./coli bench`, or `iobench`).
- **`PILOT=1` benefit.** Verified real and experimental; measured *neutral* on disk-bound boxes, only helps when compute and disk are balanced. Off by default.
- **Intel-Mac AVX2 path.** README lists x86-64 + AVX2; not tested here (the build test ran on Apple Silicon/arm64, which uses NEON + optional Metal, no AVX2).

---

## Performance expectations (real, community-measured)

| Machine | Config | tok/s |
|---|---|---|
| Apple M5 Max · 128 GB · internal SSD | CPU, MTP off | **1.06** |
| Apple M5 Max · 128 GB · 2 TB SSD | Metal, `--ram 96` | **1.83** |
| Apple M5 Max · 128 GB | Metal, `--ram 110`, warm pin | **2.06** (fastest published) |
| Mac Mini M4 Pro · 48 GB · Metal | `--ram 38` | **0.30** (vs 0.18 CPU-only) |
| Ryzen AI 9 HX 370 · 128 GB · Linux NVMe | int8 MTP, PIN 46.7 GB | 0.37 (MTP acceptance 52%) |

The engine **warms up**: `.coli_usage` pins your hottest experts across runs, so tok/s climbs the more you use it (M5 Max: 1.11 → 1.83 over one run). Cold starts are slow (0.05–0.1 tok/s) until the cache/pin warms.

### What to expect on YOUR machine (bands)

Run `./setup.sh detect` to get the band for the exact machine you're on. Summary of the logic it applies:

| Machine class | Band (tok/s) | Basis |
|---|---|---|
| Apple Silicon ≥ 96 GB | 1.0–2.1 | **measured** (M5 Max 128 GB, Metal, warm) |
| Apple Silicon 64–95 GB | 0.4–1.0 | extrapolated |
| Apple Silicon 40–63 GB | 0.2–0.4 | **measured** (M4 Pro 48 GB = 0.30) |
| Apple Silicon 16–39 GB | 0.05–0.2 | extrapolated — **demo-only** (300-token answer ≈ 25–100 min) |
| Linux x86 + NVIDIA GPU | 0.4–1.6 | **measured** (5090-class rigs; depends on VRAM expert tier) |
| Linux x86 ≥ 128 GB | 0.3–0.5 | **measured** (Ryzen AI Max+ 395 = 0.40) |
| Linux x86 32–127 GB | 0.1–0.4 | extrapolated |
| Linux x86 16–31 GB / WSL2 | 0.05–0.15 | **measured** baselines — demo-only |
| Intel Mac / ARM Linux | unknown | **not verified** upstream |
| Any machine < 16 GB RAM, or x86 without AVX2 | — | **not viable** (engine minimums) |

All bands assume a fast local NVMe; every published datapoint is an internal/direct drive — external TB3/4/USB4 numbers are unpublished, so measure before promising anything.

---

## Troubleshooting

- **"Volume 'AI_DRIVE' is not usable"** → the SSD isn't mounted, isn't external, or is named differently. macOS: `diskutil list external physical`; Linux: `lsblk -o NAME,SIZE,TRAN,MOUNTPOINT`. Then rename/format it, or run with `VOLUME_NAME=YourName ./setup.sh`, or set `MOUNT_POINT=/actual/path` in `config.local.env`.
- **Linux: "not detected as external/hot-pluggable"** → the target is an internal secondary NVMe. If that's deliberate (common on desktops), set `ALLOW_INTERNAL_TARGET=1` in `config.local.env` — the boot disk itself is always refused.
- **WSL2 is crawling** → the model is on a `/mnt/c`-style drvfs mount. Attach the disk natively (`wsl --mount`) or keep it on the ext4 VHD; drvfs random reads are catastrophically slow.
- **Filesystem is ExFAT** → reformat APFS (the script prints the exact `diskutil eraseVolume` command). ExFAT is slower and corruption-prone on macOS.
- **MTP stuck at 0% acceptance** → you have the int4-MTP mirror. Confirm `MODEL_REPO=mateogrgic/...int8-mtp` and re-check `out-mtp-*` sizes.
- **`hf: command not found`** → `./scripts/02-install-tools.sh` installs it to the Python user-bin; the `04` step adds that dir to `~/.zshrc`. Open a new shell or `source ~/.zshrc`.
- **Slow generation** → check the SSD link is TB3/4 or USB4 (`./scripts/01-check-drive.sh` speed probe), give more `--ram`, and let `.coli_usage` warm up. On Apple Silicon try Metal (`ENABLE_METAL=yes`).

---

## Sources (all consulted 2026-07-14)

- Colibrì repo & README — https://github.com/JustVugg/colibri · https://raw.githubusercontent.com/JustVugg/colibri/main/README.md
- Colibrì build script & launcher — `c/setup.sh` and `c/coli` (python3) in the repo
- Model (int8 MTP, recommended) — https://huggingface.co/mateogrgic/GLM-5.2-colibri-int4-with-int8-mtp
- Model (original mirror, int4 MTP — broken speculation) — https://huggingface.co/jlnsrk/GLM-5.2-colibri-int4
- Hugging Face CLI / download guide — https://huggingface.co/docs/huggingface_hub/en/guides/download · https://huggingface.co/docs/huggingface_hub/v0.34.0/guides/cli
- APFS vs ExFAT on macOS SSDs — https://darkghosthunter.medium.com/apfs-or-hfs-or-ntfs-or-exfat-on-my-external-drive-595d98d30e3c · https://www.adamtalks.tech/reviews/best-external-ssd-format-for-mac · https://forums.sandisk.com/t/exfat-slower-on-macos-than-apfs-macos-extended/226779

## License
Colibrì is Apache-2.0; the GLM-5.2 weights are MIT (Z.ai). This installer is provided as-is, without warranty of any kind — read the scripts (they're short) and run `--dry-run` before trusting them with your disks.
