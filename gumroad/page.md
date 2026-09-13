# Isaac Lab Fast-Track — $49

## Stop fighting the install. Start training tonight.

You have an RTX card and a URDF. NVIDIA has 40 pages of docs, three Python versions, and a driver table.
Reddit has 200 threads titled "Isaac Lab crashes on startup".

This bundle is the setup a working robotics engineer would hand you: one pinned Docker image, a preflight
script that tells you what is wrong with your machine *before* the 20 GB download, and a cookbook for the
11 errors that account for almost every "help" thread.

### What's inside
- **Pinned image**: Isaac Lab 2.3.2 + Isaac Sim 5.1.0 + PyTorch 2.7/cu128. Known-good. Never guess again.
- **Preflight**: driver, VRAM, RAM, disk, Docker, NVIDIA toolkit, NGC login, network. Red/green in 10 seconds.
- **Smoke test**: proves the GPU trains a policy end to end in ~5 minutes.
- **Low-VRAM presets**: measured env counts for 8 / 12 / 16 / 24 GB cards, per task. Yes, an RTX 4060 works.
- **Error cookbook**: DLL load failed, carb crash, NaN reward, CUDA OOM, Nucleus NoneType, and 6 more.
- **URDF lint**: catches disconnected trees, zero mass, bad inertia, and visual-mesh-as-collision in one command.
  Runs anywhere, no Isaac needed.
- **Windows route** (WSL2) and **no-GPU route** (cloud, with a bill-minimizing workflow).
- **China mirror guide**: pip, docker, and the offline asset pack so nothing hangs.

### Who it's for
Students, indie devs, and small teams who want to train locomotion / manipulation policies, not debug Omniverse.

> "The biggest risk is spending half the semester on setup before testing the actual control idea."
> — advice to a 15-week undergrad capstone team, r/robotics

> "Step 1: install Ubuntu 24.04. Step 2: try installing again." — top answer to "Please help me install Isaac Lab"

You have a 4060 laptop, 16 GB RAM, maybe Windows. Everyone says it won't work. It works headless. Here is how.

### Who it's not for
You need Isaac Lab 3.0 beta / Isaac Sim 6.0 today (coming as a free update), or you need macOS native (impossible).

### Guarantee
If the smoke test does not pass on hardware that meets the stated minimum (Ubuntu 22.04 or Win11/WSL2, NVIDIA
driver 580+, 8 GB+ VRAM) and I cannot get you there over email within 7 days, full refund.

### About
Built by a systems engineer with a decade of low-level and real-time work at Apple, now doing robotics RL.
Free updates for every 2.x release.

---
FAQ
- *Does it include Isaac Sim?* No, it pulls NVIDIA's free container; you need a free NGC account (2 minutes, guide included).
- *Laptop with 8 GB?* Yes for state-based tasks. Vision tasks need 12 GB+. The presets tell you exactly.
- *AMD?* No. Nobody can. See the cloud guide.
