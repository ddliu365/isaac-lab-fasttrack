# Version matrix (verified 2026-09-13 against official docs)

Source of truth: https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html

| Isaac Lab | Isaac Sim | Python | torch          | driver (Linux) | status                          |
|-----------|-----------|--------|----------------|----------------|---------------------------------|
| 3.0.0-beta2 | 6.0 / 6.0.1 | 3.11 | (per docs)   | 580+           | beta, API changes, not bundled  |
| **2.3.2** | **5.1.0** | 3.11   | 2.7.0 cu128    | 580.65.06+     | **bundled**                     |
| 2.2.x     | 5.0.0     | 3.11   | 2.7.0 cu128    | 570+           | works, not maintained           |
| 2.1.x     | 4.5.0     | 3.10   | 2.5.1 cu118    | 535+           | old, Python 3.10                |
| <= 2.0    | 4.2 and below | 3.10 | -            | -              | dropped upstream                |

Rules that cause 80% of "it crashes":
1. Python of the venv MUST equal Python of Isaac Sim (3.11 for 5.x, 3.10 for 4.x).
2. Driver must be the production branch >= 580 for 5.1.0. 550-series "mostly works" until livestream or RTX sensors break.
3. Never `pip install torch` without the index-url. You get a CPU or wrong-CUDA wheel and `isaacsim` core-dumps.
4. `isaaclab.sh --install` must run inside the same venv, after isaacsim is installed.
5. Docker image tags are exact: `nvcr.io/nvidia/isaac-sim:5.1.0`, `nvcr.io/nvidia/isaac-lab:2.3.2`.

Pip route (for reference, the bundle uses Docker):
```bash
conda create -n env_isaaclab python=3.11 && conda activate env_isaaclab
pip install --upgrade pip
pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128
pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com
git clone https://github.com/isaac-sim/IsaacLab.git --branch v2.3.2 && cd IsaacLab
./isaaclab.sh --install
./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py
```
