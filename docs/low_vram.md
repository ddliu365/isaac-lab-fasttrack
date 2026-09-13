# Running below the official 32 GB RAM / 16 GB VRAM

The official minimum is what NVIDIA tests at 4096 envs with rendering. You do not need that to learn or to train
state-based policies. What actually eats VRAM: number of envs x collision complexity, cameras (each tiled camera
is a render target), and the Isaac Sim GUI itself (~2-3 GB).

## The two camps on Reddit, and who is right
Camp 1: "won't work no matter what, get a cluster." Camp 2: "I ran it on an RTX 2080; you don't need rendering for
most RL, skip the Kit viewer." Camp 2 is right for state-based tasks. Isaac Sim's GUI alone sits at ~4.5 GB VRAM
before you load anything (Zhihu, 4060 laptop). Headless training of Cartpole/Ant/Anymal fits in 8 GB. The 16 GB /
32 GB "minimum" is NVIDIA's number for 4096 envs with rendering on.

## Flags that matter
- `--headless`: saves 2-3 GB and a lot of stutter. Always use for training.
- `--num_envs N`: the knob. Halve it until it fits, then step back up.
- `--enable_cameras`: only when the task needs pixels. Costs ~1-2 GB baseline + per-env render targets.
- Env var `OMNI_KIT_ALLOW_ROOT=1` is already set in the container.

## Measured: RTX 3060 12 GB, headless, driver 580.173, Isaac Lab 2.3.2 (2026-09-13)
Peak VRAM by env count (20 PPO iterations each, rsl_rl; raw data in `bench-3060-12gb.csv`):

| Task | 512 | 1024 | 2048 | 4096 | steps/s @4096 |
|---|---|---|---|---|---|
| Cartpole | 4.5 GB | 4.6 GB | 4.7 GB | 5.0 GB | 244,251 |
| Ant | 4.6 GB | 4.8 GB | 5.2 GB | 5.8 GB | 157,745 |
| Humanoid | 4.7 GB | 5.0 GB | 5.4 GB | 6.4 GB | 110,244 |
| Anymal-C flat | 4.8 GB | 4.9 GB | 5.3 GB | 5.9 GB | 79,187 |
| Anymal-C rough terrain | 5.5 GB | 5.8 GB | 6.3 GB | 7.6 GB | 13,910 |
| Unitree Go2 flat | 4.7 GB | 4.9 GB | 5.3 GB | 6.0 GB | 83,409 |
| Franka reach | 4.5 GB | 4.6 GB | 4.9 GB | 5.4 GB | 147,086 |
| Franka open drawer | 4.8 GB | 5.2 GB | 5.7 GB | 7.1 GB | 58,639 |

What this means:
- **Headless Isaac Sim costs ~4.5 GB before the first env exists.** Each additional 3,500 envs adds 1-3 GB depending on contact complexity.
- **Every stock task runs at 4096 envs on 12 GB.** The official "16 GB minimum" is for rendering workflows.
- **8 GB cards**: everything above except rough terrain and open-drawer fits at 4096; those two fit at 2048 (6.5 GB / 5.9 GB). Leave 0.5 GB headroom for the driver.
- **6 GB cards** (RTX 3050 6G, 2060): 512-1024 envs of flat-terrain tasks; no cameras.
- **4 GB cards** (3050 Ti laptop): the runtime alone exceeds it; use the cloud route. (Measured on our 3050 Ti box: see `windows_wsl2.md`.)

## Presets (`ft-train <task> <preset>`), derived from the table above with 0.5 GB headroom
| Preset | Cartpole / Ant / Humanoid / flat locomotion / Franka reach | rough terrain / open drawer | vision tasks (`--enable_cameras`) |
|---|---|---|---|
| 8g  | 4096 | 2048 | 16-32 envs at 64x64 |
| 12g | 4096 | 4096 | 64 envs at 64x64 |
| 16g | 4096 | 4096 | 128 envs at 84x84 |
| 24g | 4096 | 4096 | 256+ envs |

Vision tasks (`--enable_cameras`) at 8 GB: 16-32 envs at 64x64. Use a frozen pretrained encoder; do not backprop
through images at that scale.

## RAM below 32 GB
- Add 16-32 GB swap. Startup (extension loading, shader compile) is what spikes RAM, not training.
- Keep `num_envs` <= 1024 on 16 GB RAM boxes.
- Do not run the GUI and a training process at the same time.

## When it still OOMs
1. Check the URDF: `python3 /opt/fasttrack/tools/urdf_lint.py robot.urdf`. W1 (visual mesh as collision) is the #1 cause.
2. Replace collision meshes with capsules/boxes, or convex-decompose (CoACD) with <= 16 hulls per link.
3. Lower `sim.physx.gpu_max_rigid_contact_count` / `gpu_max_rigid_patch_count` in your env cfg if you raised them.
