# Changelog

## 0.1.0 (2026-09-13)
- Pinned image: Isaac Lab 2.3.2 + Isaac Sim 5.1.0 + torch 2.7.0/cu128, on nvcr.io/nvidia/isaac-lab:2.3.2.
- Validated on Ubuntu 22.04 / RTX 3060 12 GB / driver 580: preflight, build, smoke test (72 s warm).
- Measured VRAM for 8 stock tasks x 512-4096 envs on 12 GB (docs/low_vram.md, docs/bench-3060-12gb.csv).
- Windows 11: WSL2 + Docker Engine install path validated on a 3050 Ti laptop; training unverified there.
- Error cookbook (14 entries), version matrix, decision tree, China mirror notes, cloud route.
- Tools: urdf_lint.py, custom-URDF Direct RL template (syntax-checked, not yet trained).
