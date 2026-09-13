# No NVIDIA GPU (Mac, AMD, laptop iGPU): the rental route

Isaac Sim has no macOS, no ROCm, no CPU mode. Every "how do I run it on my M2" thread ends here.

## Cheapest workable
| Provider   | GPU          | approx $/h | Notes |
|------------|--------------|-----------:|-------|
| RunPod     | RTX 4090 24G | 0.3-0.7    | community cloud, pick "NVIDIA driver >= 580" template |
| Vast.ai    | RTX 3090/4090| 0.2-0.5    | check driver version in listing; skip < 580 |
| Lambda     | A10 24G      | ~0.75      | reliable, driver current |
| AutoDL (国内)| RTX 4090   | ¥2-3/h     | 有预装 Isaac Sim 镜像，网络到 NVIDIA CDN 仍慢 |
| 算力自由 gpufree.cn | RTX 4090 | ¥1.38/h | 镜像仓库有 IsaacLab / IsaacSim+ROS2，VNC 连接，知乎用户实测顺畅 |
| gradmotion (逐际动力) | 多种 | 注册送算力 | 预置 Isaac 环境一键训练；平台型，锁定其工作流 |
| gpulab | 3090-5090/A100 | 按量 | 远程图形化开发机，一键启动 Isaac Lab/Gym/MuJoCo |

Rule: 32 GB RAM, >= 16 GB VRAM, 100 GB disk, Ubuntu 22.04, driver >= 580. Anything else wastes the first hour.

## Workflow that keeps the bill small
1. Persistent volume (100 GB) holding this bundle's cache dir. Pay for storage, not for re-downloading.
2. Start pod -> `./scripts/up.sh` -> train headless with tmux -> `rsync` checkpoints back -> stop pod.
3. Develop the env code locally on your Mac (it is plain Python); only run it remotely.
4. Livestream only when you need to see it; it doubles GPU load.
