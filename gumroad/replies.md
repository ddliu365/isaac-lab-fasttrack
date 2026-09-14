# Public replies for the three source threads (post as yourself; link only in your profile, not in the reply)

## 1. Reddit r/robotics — "Please help me install Isaac Lab" (4060 laptop, 8 GB, Windows, 16 GB RAM)
https://www.reddit.com/r/robotics/ (the thread where the top answer is "Step 1: install Ubuntu 24.04")

Your hardware is fine for state-based RL; the install path is what's killing you. Three things, in order:

1. Skip native Windows. The DLL error on `import h5py` is a pip/conda mismatch that keeps coming back. Either dual-boot Ubuntu 22.04 or use WSL2 with Docker Engine inside it (not Docker Desktop). I validated the WSL2 install path this week on a 3050 Ti laptop: `nvidia-smi` works inside the container on the first try. What I could NOT validate is training under WSL2, because that laptop has 4 GB and PhysX fell back to CPU ("GPU Bp pipeline failed, switching to software"). If you see that line, stop and dual-boot.
2. Run headless. Isaac Sim's GUI alone holds ~4.5 GB. Without it, on a 12 GB card I measured every stock task (Cartpole, Ant, Humanoid, Anymal flat/rough, Go2, Franka reach/drawer) at 4096 envs with peak VRAM between 5.1 and 7.8 GB. On 8 GB, drop rough terrain and drawer to 2048 envs and everything fits. The "16 GB minimum" is for rendering.
3. Pin versions and never let pip pick: Isaac Sim 5.1.0 + Isaac Lab 2.3.2 + Python 3.11 + torch 2.7.0 from the cu128 index. If you must stay on Windows, the two pins that fixed it for the person in this thread were `tensordict==0.11.0` and `h5py==3.11.0 --force-reinstall` (IsaacLab discussion #5373).

One more: first launch looks frozen for 2-10 minutes while shaders compile. It is not the driver. Wait before reinstalling anything.

## 2. Reddit — 15-week undergrad capstone team choosing between PyBullet and Isaac Lab ("half the semester on setup")
Do Isaac Lab, but time-box the setup to one afternoon with these rules, and fall back to PyBullet if you blow past it:

- One machine, Ubuntu 22.04, NVIDIA driver 580 branch, Docker + nvidia-container-toolkit. Pull NVIDIA's `isaac-lab:2.3.2` container instead of pip-installing anything. That removes the Python/torch/CUDA matrix entirely.
- Headless only. Your 4060s are enough: on a 12 GB card I measured 4096-env Anymal flat at 6.1 GB and 79k steps/s; an 8 GB card runs the same at 4096 envs.
- Two gotchas that eat days: (a) the `create_empty.py` tutorial is an infinite loop by design, it is not hung; (b) if you have Docker 28+, images land in `/var/lib/containerd`, not Docker's data-root, so put that on your big disk before pulling 26 GB.
- Your URDF is the real risk, not the policy. Zero mass, non-positive-definite inertia, or a visual mesh used as collision will give you NaN rewards or OOM at 1024 envs. Lint it before the first training run.

If one person on the team owns the environment and the other two never touch it, you get the whole semester for the control idea.

## 3. 知乎 — 《装 isaac lab（失败）手记》（4060 笔记本，两周后放弃转 Isaac Gym）
看完全文和评论区，你们卡的三个点其实都有确定答案，写在这里给后来的人：

1. "一打开 isaacsim 就卡死、回退驱动才好"：评论区楼下自己也发现了，那是首次启动编译着色器，无响应 2 到 10 分钟是正常的，等就行。550 到 596 的驱动都有人跑通，不用为这个反复装驱动、进 BIOS 切显卡。
2. "啥也没跑就吃了 4.5G 显存"：那是 GUI 的固定开销。训练用 `--headless`，我在 3060 12G 上实测 8 个官方任务（Cartpole、Ant、Humanoid、Anymal 平地和粗糙地形、Go2、Franka reach 和开抽屉）4096 环境峰值显存 5.1 到 7.8G，全部能跑。4060 8G 除粗糙地形和开抽屉降到 2048 环境外也全能跑。"最低 16G"是渲染工作流的要求，不是训练的。
3. 版本别让 pip 自己选：Isaac Sim 5.1.0 + Isaac Lab 2.3.2 + Python 3.11 + torch 2.7.0（cu128 索引）。用官方的 `isaac-lab:2.3.2` 容器最省事，pip 路线才会遇到你文里那些依赖冲突。

Isaac Gym 能跑通说明硬件没问题，回到 Isaac Lab 只差这三条。国内下 assets 慢的问题另说，离线资产包解压后指到本地路径就不联网了。
