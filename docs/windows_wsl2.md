# Windows 11 route: WSL2 + Docker Engine

Status 2026-09-13: install path validated end to end on a 12700H / RTX 3050 Ti 4 GB laptop (Win11 Pro 26200); GPU visible in
containers; Isaac Sim boots. Training NOT validated: PhysX fell back to CPU (see "What we measured"). Treat WSL2 as
"try it, fall back to dual-boot".

Why not native Windows: the threads that end with "I installed Ubuntu just for this" are right. Native Windows Isaac Lab
hits DLL conflicts (h5py), carb crashes, and path issues; NVIDIA's own Docker path is Linux-only. WSL2 gives you the
Linux container path on top of your Windows driver, and **the same scripts as the Ubuntu route**. Docker Desktop is
not required.

## Steps (admin PowerShell unless noted)
1. **NVIDIA driver on Windows** >= 580 (we tested 596.08). Never install a driver inside WSL; the Windows driver is
   passed through as `/usr/lib/wsl/lib/libcuda.so`.
2. **Enable the two features** (needed once; `wsl --install` does this too but fails in non-interactive shells):
   ```powershell
   dism /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   dism /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   ```
3. **Install WSL**. Either `wsl --install` from an interactive window (uses the Store), or the MSI from
   https://github.com/microsoft/WSL/releases (we used wsl.2.7.14.0.x64.msi, 259 MB): `msiexec /i wsl.msi /quiet /norestart`.
4. **Reboot.** VirtualMachinePlatform is not active until you do.
5. **Ubuntu 22.04**: `wsl --install -d Ubuntu-22.04 --no-launch`, then `wsl -d Ubuntu-22.04 -u root`.
   Check: `nvidia-smi` inside WSL shows your GPU; `ps -p 1 -o comm=` prints `systemd` (WSL 2.x default).
6. **Memory**: WSL takes half your RAM by default (15 GB of 32 on our box). Create `%UserProfile%\.wslconfig`:
   ```
   [wsl2]
   memory=24GB
   swap=16GB
   ```
   then `wsl --shutdown`. Isaac Sim's startup spike is what needs it.
7. **Inside WSL as root**, clone this bundle under `/root` or `/home/<you>` (NOT `/mnt/c/...`: 10x slower, breaks
   permissions) and run the same host setup as Linux:
   ```bash
   bash scripts/host-setup-ubuntu.sh        # Docker Engine + NVIDIA Container Toolkit; ends with a GPU-in-container check
   ./scripts/preflight.sh && ./scripts/up.sh && ./scripts/smoke.sh
   ```

## What we measured on the 3050 Ti (4 GB)
- Docker Engine + toolkit install: ~3 min. GPU visible in containers on the first try.
- Isaac Lab image: 26.4 GB. Pull it directly (`docker login nvcr.io` inside WSL) or `docker load` a tarball.
- Smoke test: CUDA visible to torch (step 1 OK). Isaac Sim headless booted in ~8 s, then PhysX logged
  `GPU Bp pipeline failed, switching to software` and the empty-scene step never returned (killed after 5 min,
  VRAM in use: 196 MiB). Isaac Lab needs the GPU PhysX pipeline; a CPU fallback is not usable.
- **Cause not isolated.** This box has two disqualifiers at once (4 GB VRAM, and WSL2, which NVIDIA does not list as
  supported for Isaac Sim). If you have >= 8 GB under WSL2 and see the same line, it is WSL2; tell us and we will
  update this page. Until then the honest recommendation for Windows is: **install path works, training on WSL2 is
  unverified; dual-boot Ubuntu 22.04 is the known-good route** (which is also what every long Reddit thread ends with).

## Known limits
- No GUI from the container. Use `LIVESTREAM=1` + the Isaac Sim WebRTC Streaming Client on Windows, or WSLg for
  lightweight tutorials. Training does not need a window.
- Laptops with an Intel iGPU: the NVIDIA GPU must be the one CUDA sees. `nvidia-smi` inside WSL settles it.
- WSL's virtual disk grows on C:; keep 100 GB free.
- Docker Desktop (optional): if you prefer it, install with the WSL2 backend and enable integration for Ubuntu-22.04;
  skip step 7's host-setup. It needs an interactive desktop session to start, which is why we do not script it.
