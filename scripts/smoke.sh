#!/usr/bin/env bash
# Headless smoke test: proves Isaac Sim boots, Isaac Lab imports, and PhysX trains on the GPU.
set -euo pipefail
cd "$(dirname "$0")/../docker"
docker compose exec -T isaaclab bash -lc 'ft-smoke'
