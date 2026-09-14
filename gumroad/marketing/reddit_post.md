Title: I measured Isaac Lab VRAM on a 12 GB card: every stock task runs at 4096 envs headless. The "16 GB minimum" is for rendering, not training.

Every week there is a thread here or in r/robotics from someone with a 4060 laptop asking if Isaac Lab is even possible. NVIDIA's docs say 32 GB RAM / 16 GB VRAM minimum. I had an RTX 3060 12 GB (driver 580.173, Ubuntu 22.04, Isaac Lab 2.3.2 + Isaac Sim 5.1.0 in the official container) and a free afternoon, so I ran the numbers instead of guessing.

Method: rsl_rl PPO, `--headless`, 20 iterations per run, peak VRAM sampled with nvidia-smi every second. Each task at 512 / 1024 / 2048 / 4096 envs.

| Task | 512 | 1024 | 2048 | 4096 | steps/s @4096 |
|---|---|---|---|---|---|
| Cartpole | 4.7 GB | 4.7 | 4.9 | 5.1 | 244k |
| Ant | 4.7 | 4.9 | 5.3 | 6.0 | 158k |
| Humanoid | 4.8 | 5.1 | 5.5 | 6.5 | 110k |
| Anymal-C flat | 4.9 | 5.1 | 5.4 | 6.1 | 79k |
| Anymal-C rough terrain | 5.6 | 6.0 | 6.5 | 7.8 | 14k |
| Unitree Go2 flat | 4.8 | 5.0 | 5.4 | 6.1 | 83k |
| Franka reach | 4.6 | 4.8 | 5.1 | 5.5 | 147k |
| Franka open drawer | 4.9 | 5.3 | 5.9 | 7.3 | 59k |

What this means:

* Headless Isaac Sim costs ~4.5 GB before the first env exists. That is the number the Zhihu crowd complains about ("4.5 GB with nothing running"). It is the GUI plus Kit runtime, and it is fixed.
* After that, 3,500 more envs cost 1 to 3 GB depending on contact complexity. Every stock task fits on 12 GB at 4096 envs.
* On 8 GB: everything except rough terrain and open-drawer fits at 4096; those two fit at 2048 (6.5 / 5.9 GB). So yes, the 4060 laptop works, as long as you never open the GUI while training.
* The 16 GB figure is real for rendering workflows (cameras, RTX sensors). For state-based RL it is 2x too high.

Two things that wasted more of my afternoon than the benchmark itself, in case you hit them:

* `scripts/tutorials/00_sim/create_empty.py` is an infinite loop by design. Headless it looks hung. It is not. Ctrl-C.
* Docker 28+ stores image layers under `/var/lib/containerd`, not under Docker's `data-root`. I pointed data-root at a big disk, pulled the 26 GB image, and filled the root partition anyway.

Also tried the Windows route (WSL2 + Docker Engine, 3050 Ti 4 GB): install works, GPU visible in the container, Isaac Sim boots in 8 s, then PhysX prints `GPU Bp pipeline failed, switching to software` and hangs. Can't tell whether that is the 4 GB or WSL2; if anyone has >= 8 GB under WSL2 and sees that line, I'd like to know.

Raw CSV and the bench script are in the bundle below if you want to reproduce on your card.

---

Full disclosure: I packaged this into a paid bundle, because the setup is the part everyone loses a week on. Isaac Lab Fast-Track ($49): the pinned Docker image + compose with persistent caches, a preflight script (driver / VRAM / RAM / disk / Docker / containerd root / CPU governor), the measured presets above wired into a `ft-train <task> <8g|12g|16g|24g>` command, a 14-entry error cookbook (DLL load failed, carb crash, NaN reward, CUDA OOM, Nucleus NoneType, the two above), a URDF linter that catches zero mass / bad inertia / disconnected trees / visual-mesh-as-collision before Isaac explodes, and a custom-URDF Direct RL template. Ubuntu 22.04 validated; WSL2 install path validated, training there not. Refund if the smoke test won't pass on hardware that meets the stated minimum.

https://appleddliu.gumroad.com/l/isaac-lab-fasttrack

Happy to answer questions about the numbers either way.
