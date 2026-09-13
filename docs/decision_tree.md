# Which route? Answer 3 questions.

## Q1. What GPU?
- **NVIDIA RTX, >= 8 GB VRAM** (2080 / 3060 12G / 4060 / 4070 / 4090 / A-series) -> continue to Q2.
- **NVIDIA < 8 GB** (GTX 1650, MX, 3050 4G) -> `docs/cloud.md`. Isaac Sim alone idles at ~4.5 GB VRAM with the GUI.
- **AMD / Intel Arc / iGPU / Apple Silicon** -> `docs/cloud.md`. No ROCm, no Metal, no CPU mode. Nobody has a workaround.

## Q2. What OS?
- **Ubuntu 22.04 / 24.04** -> route A (Docker). Route B (pip + venv) only if you cannot run Docker (shared lab box without root).
- **Windows 11** -> route C (WSL2 + Docker Engine, `docs/windows_wsl2.md`): install validated, training unverified (PhysX GPU pipeline may not come up). Dual-boot Ubuntu is the known-good route. Native Windows is route D and you were warned.
- **Windows 10 / Ubuntu 20.04** -> upgrade first. Ubuntu 20.04 has glibc 2.31 (< 2.35 needed for the pip route).
- **macOS** -> `docs/cloud.md`, develop locally, run remotely.

## Q3. Do you need pixels (cameras) in the observation?
- **No** (locomotion, manipulation from state, most course projects) -> run `--headless`, never open the GUI while training. RTX 2080 / 4060 8G is enough. Presets: `docs/low_vram.md`.
- **Yes** -> 12 GB VRAM minimum, 16 GB comfortable. 8 GB: 16-32 envs at 64x64, or rent.

## Route summary
| Route | Who | Command |
|---|---|---|
| A Docker (Ubuntu) | default | `scripts/preflight.sh && scripts/up.sh && scripts/smoke.sh` |
| B pip (Ubuntu) | no Docker allowed | `requirements-lock.txt` + VERSIONS.md commands |
| C WSL2 (Windows) | Windows users | `docs/windows_wsl2.md` then route A inside WSL |
| D native Windows | last resort | VERSIONS.md pip commands + `docs/errors.md` #2 #3 #11 |
| E cloud | no NVIDIA | `docs/cloud.md` then route A on the rented box |

## Driver: what people actually run (collected from threads, 2026)
| Reported | Isaac Sim | Result |
|---|---|---|
| 535 (Linux) | 4.5 / 5.x | works; no livestream on 5.x |
| 550 (Linux) | 5.x | "正好" (Zhihu) |
| 572.16 (Win) | 5.1 | worked after tensordict/h5py pin (Reddit) |
| 580.65+ (Linux) | 5.1 | official recommendation |
| 591.44 (Win) | 5.1 | works (Reddit) |
One Zhihu user reported "580+ hangs, 535 works", then found the real cause: **first launch looks frozen for 2+ minutes
while shaders compile**. Wait 5 minutes before touching the driver. See `docs/errors.md` #0.
