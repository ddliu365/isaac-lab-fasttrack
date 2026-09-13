# Isaac Lab Fast-Track Bundle

One command to a working, pinned Isaac Lab 2.3.2 + Isaac Sim 5.1.0 environment.
Targets Ubuntu 22.04 natively, and Windows 11 via WSL2 (same scripts, Docker Engine inside WSL).
No macOS path exists (Isaac Sim is CUDA/RTX only); see `docs/cloud.md` for the no-GPU route.

## What you get
- `docker/`            pinned image + compose file with persistent caches (no re-downloading 10+ min of extensions every run)
- `scripts/preflight.sh` checks driver / VRAM / RAM / disk / Docker / nvidia-container-toolkit BEFORE you waste an hour
- `scripts/up.sh`       build-or-pull, start, drop into shell
- `scripts/smoke.sh`    headless smoke test: empty scene + 200 iterations of Cartpole, so you know it works
- `docs/low_vram.md`    measured VRAM for 8 stock tasks x 512-4096 envs on a 12 GB card; presets for 8 / 12 / 16 / 24 GB
- `docs/errors.md`      the errors people actually hit (DLL load, carb crash, NaN reward, OOM, Nucleus NoneType) with fixes
- `docs/china_mirror.md` pip mirror + local asset pack so nothing hangs on downloads
- `docs/windows_wsl2.md` the Windows route that does not involve fighting conda on Windows
- `tools/urdf_lint.py`  catches disconnected trees, zero mass, bad inertia, visual-mesh-as-collision before Isaac explodes

## Quick start (Ubuntu 22.04, NVIDIA driver >= 580)
```bash
./scripts/preflight.sh          # fix anything red
cp docker/.env.example docker/.env
./scripts/up.sh                 # pulls ~20 GB the first time
./scripts/smoke.sh              # ~5 min, prints PASS
```

## Versions (do not mix)
| Component     | Pin                       |
|---------------|---------------------------|
| Isaac Lab     | v2.3.2 (last 2.x stable)  |
| Isaac Sim     | 5.1.0                     |
| Python        | 3.11                      |
| PyTorch       | 2.7.0 + cu128             |
| NVIDIA driver | >= 580.65 (Linux) / 580.88 (Windows) |
| Docker        | >= 26, compose >= 2.25, nvidia-container-toolkit |

Isaac Lab 3.0 is beta and requires Isaac Sim 6.0; it is NOT covered by this bundle yet. Updates are free.
