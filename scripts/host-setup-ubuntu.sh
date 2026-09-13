#!/usr/bin/env bash
# One-time host setup for Ubuntu 22.04/24.04. Run with sudo. Installs Docker Engine + NVIDIA Container Toolkit,
# and optionally puts Docker's data on a separate disk (DATA_DEV, e.g. /dev/sda2). Never formats anything.
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "run with sudo"; exit 1; }
USER_NAME="${SUDO_USER:-$USER}"
DATA_DEV="${DATA_DEV:-}"          # e.g. /dev/sda2 ; empty = keep docker on /
DATA_MNT="${DATA_MNT:-/data}"

echo "== 1/4 data disk"
if [ -n "$DATA_DEV" ]; then
  mkdir -p "$DATA_MNT"
  if ! mountpoint -q "$DATA_MNT"; then
    mount "$DATA_DEV" "$DATA_MNT"
    echo "mounted $DATA_DEV at $DATA_MNT (contents below; nothing was modified)"; ls -la "$DATA_MNT" | head
  fi
  UUID=$(blkid -s UUID -o value "$DATA_DEV")
  grep -q "$UUID" /etc/fstab || echo "UUID=$UUID $DATA_MNT ext4 defaults,nofail 0 2" >> /etc/fstab
  mkdir -p "$DATA_MNT/docker" "$DATA_MNT/isaac-fasttrack" "$DATA_MNT/isaac-workspace"
  chown "$USER_NAME:$USER_NAME" "$DATA_MNT/isaac-fasttrack" "$DATA_MNT/isaac-workspace"
  df -h "$DATA_MNT"
fi

echo "== 2/4 docker engine"
if ! command -v docker >/dev/null; then
  apt-get update -qq
  apt-get install -y -qq ca-certificates curl gnupg
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
  chmod a+r /etc/apt/keyrings/docker.gpg
  . /etc/os-release
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" > /etc/apt/sources.list.d/docker.list
  apt-get update -qq
  apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi
usermod -aG docker "$USER_NAME"
mkdir -p /etc/docker
if [ -n "$DATA_DEV" ]; then
  python3 - "$DATA_MNT/docker" <<'PY'
import json,sys,os
p='/etc/docker/daemon.json'; d=json.load(open(p)) if os.path.exists(p) and os.path.getsize(p) else {}
d['data-root']=sys.argv[1]; json.dump(d,open(p,'w'),indent=2)
PY
fi

echo "== 3/4 nvidia container toolkit"
if ! dpkg -s nvidia-container-toolkit >/dev/null 2>&1; then
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg --yes
  curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
    | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
    > /etc/apt/sources.list.d/nvidia-container-toolkit.list
  apt-get update -qq
  apt-get install -y -qq nvidia-container-toolkit
fi
nvidia-ctk runtime configure --runtime=docker >/dev/null
systemctl enable docker >/dev/null
systemctl restart docker

echo "== 4/4 verify"
docker info --format 'docker {{.ServerVersion}}, data-root {{.DockerRootDir}}, runtimes: {{range $k,$v := .Runtimes}}{{$k}} {{end}}'
docker run --rm --gpus all nvidia/cuda:12.8.0-base-ubuntu22.04 nvidia-smi --query-gpu=name,driver_version --format=csv,noheader \
  && echo "GPU visible in containers: OK"
echo
echo "DONE. Next, as $USER_NAME (new login so the docker group applies):"
echo "  docker login nvcr.io        # user: \$oauthtoken  password: NGC API key"
