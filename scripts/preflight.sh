#!/usr/bin/env bash
# Host preflight for Isaac Lab Fast-Track. Run on the Ubuntu host (or inside WSL2). No sudo needed.
set -u
R="\033[31m"; G="\033[32m"; Y="\033[33m"; N="\033[0m"
fail=0
ok(){ echo -e "${G}[OK]${N}   $*"; }
warn(){ echo -e "${Y}[WARN]${N} $*"; }
bad(){ echo -e "${R}[FAIL]${N} $*"; fail=1; }

echo "== Isaac Lab Fast-Track preflight =="

# OS
if grep -qi microsoft /proc/version 2>/dev/null; then ok "WSL2 detected (see docs/windows_wsl2.md)"; WSL=1; else WSL=0; fi
if [ -r /etc/os-release ]; then . /etc/os-release; case "$VERSION_ID" in 22.04|24.04) ok "OS $PRETTY_NAME";; *) warn "OS $PRETTY_NAME (tested on Ubuntu 22.04/24.04; containers usually fine)";; esac; fi
GLIBC=$(ldd --version 2>/dev/null | head -1 | awk '{print $NF}'); ok "glibc $GLIBC (needs >= 2.35 for pip route; Docker route does not care)"

# NVIDIA driver
if ! command -v nvidia-smi >/dev/null; then bad "nvidia-smi not found: install NVIDIA driver >= 580 (production branch)"; else
  DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)
  GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
  VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
  MAJ=${DRV%%.*}
  if [ "$MAJ" -ge 580 ]; then ok "driver $DRV on $GPU"; elif [ "$MAJ" -ge 550 ]; then warn "driver $DRV: Isaac Sim 5.1 wants >= 580; 550-57x mostly works, livestream/RTX sensors may break"; else bad "driver $DRV too old for Isaac Sim 5.1 (need >= 580)"; fi
  if [ "$VRAM" -ge 16000 ]; then ok "VRAM ${VRAM} MiB"; elif [ "$VRAM" -ge 8000 ]; then warn "VRAM ${VRAM} MiB: below official 16 GB, use presets in docs/low_vram.md"; else bad "VRAM ${VRAM} MiB: Isaac Lab will not be usable; see docs/cloud.md"; fi
fi

# RAM / disk
RAM=$(awk '/MemTotal/{printf "%d",$2/1024/1024}' /proc/meminfo)
if [ "$RAM" -ge 30 ]; then ok "RAM ${RAM} GB"
elif [ "$WSL" = 1 ]; then warn "RAM ${RAM} GB visible to WSL (default is half the host): set memory=24GB+ in %UserProfile%\\.wslconfig, then wsl --shutdown (docs/windows_wsl2.md step 6)"
elif [ "$RAM" -ge 16 ]; then warn "RAM ${RAM} GB: official minimum is 32 GB; add swap, keep env count low"
else bad "RAM ${RAM} GB: too low"; fi
DISK=$(df -BG "${HOME}" | awk 'NR==2{gsub("G","",$4); print $4}')
if [ "$DISK" -ge 80 ]; then ok "free disk ${DISK} GB in \$HOME"; else bad "free disk ${DISK} GB: need ~80 GB (image 20 GB + caches + assets)"; fi

# Docker
if ! command -v docker >/dev/null; then bad "docker not installed: https://docs.docker.com/engine/install/ubuntu/"; else
  DV=$(docker version --format '{{.Server.Version}}' 2>/dev/null || echo "?")
  if docker info >/dev/null 2>&1; then ok "docker $DV, daemon reachable"; else bad "docker daemon not reachable (add yourself to docker group: sudo usermod -aG docker \$USER, then re-login)"; fi
  if docker compose version >/dev/null 2>&1; then ok "docker compose $(docker compose version --short)"; else bad "docker compose plugin missing"; fi
  if docker info 2>/dev/null | grep -qi nvidia; then ok "nvidia container runtime registered"; else bad "nvidia-container-toolkit not configured: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html then: sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker"; fi
  if docker run --rm --gpus all nvidia/cuda:12.8.0-base-ubuntu22.04 nvidia-smi >/dev/null 2>&1; then ok "GPU visible inside containers"; else warn "could not run a GPU test container (offline, or toolkit missing)"; fi
  if docker image inspect nvcr.io/nvidia/isaac-lab:2.3.2 >/dev/null 2>&1; then ok "isaac-lab:2.3.2 image already present (no NGC login needed)"
  elif grep -q nvcr.io "${HOME}/.docker/config.json" 2>/dev/null; then ok "logged in to nvcr.io"; else warn "not logged in to nvcr.io: get a free NGC API key at https://ngc.nvidia.com/setup/api-key then: docker login nvcr.io  (user: \$oauthtoken)"; fi
fi

# CPU governor (Isaac Sim warns; costs 20-40% throughput)
GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo unknown)
case "$GOV" in performance|schedutil) ok "cpu governor $GOV";; unknown) ok "cpu governor n/a (VM/WSL)";; *) warn "cpu governor '$GOV': set performance (see docs/errors.md #13)";; esac

# Docker 28+: images live under the containerd root, not data-root
if command -v docker >/dev/null; then
  CROOT=$(readlink -f /var/lib/containerd 2>/dev/null || echo /var/lib/containerd)
  CFREE=$(df -BG "$CROOT" 2>/dev/null | awk 'NR==2{gsub("G","",$4); print $4}')
  if [ -n "$CFREE" ] && [ "$CFREE" -lt 80 ]; then warn "containerd root $CROOT has ${CFREE} GB free; images go HERE, not data-root (docs/errors.md #12)"; fi
fi

# Network sanity (Nucleus/asset downloads hang silently in some regions)
if curl -sI --max-time 5 https://pypi.nvidia.com >/dev/null; then ok "pypi.nvidia.com reachable"; else warn "pypi.nvidia.com unreachable: see docs/china_mirror.md"; fi

echo
if [ $fail -eq 0 ]; then echo -e "${G}PREFLIGHT PASSED${N}"; else echo -e "${R}PREFLIGHT FAILED: fix [FAIL] lines above${N}"; exit 1; fi
