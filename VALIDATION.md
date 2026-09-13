# Validation checklist (run on the GPU box; everything here is unverified until checked)

Linux box: Ubuntu 22.04.5, RTX 3060 12G, driver 580.173, 31 GB RAM.   Windows box: Win11 Pro 26200, RTX 3050 Ti 4G, driver 596.08, 32 GB RAM

- [x] `scripts/preflight.sh` runs clean (3060 box: flagged disk + docker correctly), every check makes sense on this box
- [x] pull ok: 26.4 GB, ~15 min on the 3060 box. NOTE Docker 29 stored it under /var/lib/containerd, not data-root (errors.md #12)
- [x] build ~2 min on top of the base image
- [x] ft-smoke PASS in 45 s warm (boot 4.8 s, Cartpole 64 envs x 100 it). Two fixes: tutorial infinite loop, SimulationApp.close() hang
- [ ] second `up.sh` after `down.sh` starts in < 60 s (cache volumes work)
- [x] 8 tasks x 4 env counts measured on 3060 12G: docs/bench-3060-12gb.csv, table in docs/low_vram.md
- [ ] cameras: `Isaac-Cartpole-RGB-Camera-Direct-v0 --enable_cameras` at 16/32/64 envs, record VRAM
- [ ] livestream: LIVESTREAM=1, connect from the Mac with the WebRTC client
- [ ] local asset pack: download, mount, confirm `create_empty` runs with network blocked (write `ft-assets-local`)
- [ ] URDF lint on 3 real robots (Unitree Go2, H1-2, a Fusion360 export): confirm findings are real, no false errors
- [x] Windows: DISM + MSI + reboot + Ubuntu-22.04 + host-setup-ubuntu.sh inside WSL -> GPU in container OK (3050 Ti 4G). Deviation: `wsl --install` fails over SSH; Docker Desktop dropped in favor of Engine-in-WSL
- [ ] `docker save` tarball size for the offline route
