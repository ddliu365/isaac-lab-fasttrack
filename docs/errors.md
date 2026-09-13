# Error cookbook (ranked by how often they appear in Reddit / Zhihu threads)

## 0. "It hangs on launch" / "isaacsim freezes, must be the driver"
First launch compiles shaders and unpacks extensions: 2-10 minutes of a frozen window or a silent terminal, more on
laptops with power limits. One Zhihu user reinstalled drivers "countless times" and flipped BIOS GPU priority
before noticing it just needed 2 minutes. Wait. Run `tail -f ~/.nvidia-omniverse/logs/Kit/Isaac-Sim/5.1/*.log`
(or the mounted `logs/` dir with Docker) to see it working. Second launch is fast if caches persist (ours do).

## 0b. "It never finishes" on the create_empty tutorial
`scripts/tutorials/00_sim/create_empty.py` (and most 00_sim tutorials) run `while simulation_app.is_running()` forever
by design. Headless, that is an infinite loop with no output. It is not hung. Ctrl-C it. Our `ft-smoke` uses a
bounded scene test instead.

## 0c. `carb.crashreporter-breakpad` crash within the first second, right after a previous run
Seen on Linux 3060 during back-to-back launches: `[Fatal] libomni.kit.telemetry.plugin.so ... regex_error` at 34 ms.
Transient; the immediate rerun succeeded. If it repeats, wait 5 s between launches or disable telemetry:
`--/telemetry/enabled=false` (Kit setting) or `export OMNI_KIT_DISABLE_TELEMETRY=1`. On Windows the same
crashreporter line usually has a different cause: see #3.

## 1. Wall of red text at startup, then it works anyway
`[Error] [omni.kit...] Failed to acquire interface ...`, `[Warning] ... extension not found`
Normal on first boot and after cache wipes. Real failures end with a Python traceback or a `carb` crash; red
warnings that scroll past and then show `Simulation App Startup Complete` are noise. Reduce it with `--headless`.

## 2. `ImportError: DLL load failed while importing _errors` (h5py, Windows)
Native Windows pip install with a conda env that pulled a different HDF5. Fixes, in order of sanity:
a) Stop. Use WSL2 + this Docker image (docs/windows_wsl2.md). This is what the Isaac Lab maintainers actually test.
b) If you must stay native: fresh venv (not conda), Python 3.11 exact, install torch with the cu128 index URL
   FIRST, then `isaacsim[all,extscache]==5.1.0`, then `pip install tensordict==0.11.0` and
   `pip install h5py==3.11.0 --force-reinstall --no-cache-dir`. Source: IsaacLab discussion #5373; a Reddit user on
   a 4060 laptop / Windows / driver 572 went from DLL error to training with exactly these two pins.

## 3. `carb.crashreporter-breakpad.plugin` / instant crash on first RL task (Windows or old driver)
Almost always driver < 580 or a laptop where the iGPU is the primary adapter. Update to 580.88 (Windows) /
580.65+ (Linux). On laptops set the NVIDIA GPU as preferred for python.exe in the NVIDIA Control Panel, or
run headless so no window is created on the iGPU.

## 4. Core dump / `Segmentation fault` right after `import isaacsim`
torch CUDA version mismatch. Check: `python -c "import torch;print(torch.version.cuda)"` must print 12.8 for the
5.1.0 line. Reinstall torch with the index URL from VERSIONS.md. Never let another package upgrade torch.

## 5. Reward goes to NaN / robot launches into the sky on frame 1
Your asset, not your policy. Run `urdf_lint.py`. Zero mass, non-PD inertia, or a mm/m unit slip. Also check
`ArticulationCfg.spawn` uses `fix_root_link=False` only if you intend it, and that `init_state.pos` is above ground.

## 6. `RuntimeError: CUDA out of memory` when creating envs
Collision meshes are too fine or `num_envs` too high. See docs/low_vram.md. Convex-decompose or use primitives.

## 7. Nucleus / assets: `NoneType has no attribute ...`, stuck on "Loading ..." forever
Asset download timing out (common outside US/EU). See docs/china_mirror.md. Symptoms include
`omni.client` errors and `Failed to resolve asset path`. Isaac Sim 5.x no longer needs a Nucleus server for the
default assets, but they still stream from an NVIDIA CDN. Local asset pack fixes it permanently.

## 8. `isaaclab.sh --install` fails on `quadprog` / `rsl-rl` / `skrl`
Install one framework at a time: `./isaaclab.sh --install rsl_rl`. Isaac Lab's own Dockerfile removes quadprog
after install ("hack"); we do the same.

## 9. Python version mismatch `isaacsim requires python 3.11`
Your venv is 3.10 (from an Isaac Sim 4.x tutorial). Isaac Sim 5.x = 3.11. Recreate the env.

## 10. WSL2: GUI does not appear / `Failed to create display`
Expected. The container is headless. Use livestream (`LIVESTREAM=1` in docker/.env, then the Isaac Sim WebRTC
Streaming Client on Windows) or WSLg for the lightweight tutorials. Training does not need a window.

## 12. Root disk fills up even though Docker's data-root points at a big disk (Docker 28+)
Docker 28/29 store images through the system containerd (containerd-snapshotter). `data-root` in daemon.json
moves only Docker's own metadata; image layers land in `/var/lib/containerd`. Fix (stop, move, symlink):
```bash
sudo systemctl stop docker.socket docker containerd
sudo mv /var/lib/containerd /data/containerd && sudo ln -s /data/containerd /var/lib/containerd
sudo systemctl start containerd docker
```
`scripts/preflight.sh` now warns when the containerd root is on a disk with < 80 GB free.

## 13. Training is 20-40% slower than the numbers in docs/low_vram.md
Isaac Sim prints `CPU performance profile is set to powersave` at startup. Set the governor:
`sudo apt install linux-tools-common && sudo cpupower frequency-set -g performance` (or via `/sys/devices/system/cpu/*/cpufreq/scaling_governor`).

## 14. `PhysX warning: GPU Bp pipeline failed, switching to software` then a hang or crawl
PhysX could not create its GPU pipeline, so it silently switched to CPU. Isaac Lab's tensor API assumes GPU PhysX;
what follows is a hang, an OOM-looking crash, or 100x slower stepping. Seen by us on a 4 GB laptop under WSL2; also
reported on containers with broken CUDA library mapping and on some Blackwell drivers (IsaacLab #3448). Check, in order:
`nvidia-smi` inside the container; VRAM >= 6 GB free at launch; not WSL2 (unsupported); driver on the 580 branch.

## 11. Windows path with spaces or non-ASCII characters (中文用户名)
`C:\Users\张三\...` breaks Kit's extension loader. Put IsaacLab under `C:\isaac\` or, in WSL2, under `/home/<you>/`.
Isaac Lab docs say the same for Docker: keep the repo under `/home`.
