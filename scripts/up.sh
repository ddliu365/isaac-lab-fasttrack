#!/usr/bin/env bash
# Build (first time) and start the container, then drop into a shell.
set -euo pipefail
cd "$(dirname "$0")/../docker"
[ -f .env ] || { cp .env.example .env; echo "created docker/.env from example"; }
set -a; . ./.env; set +a
mkdir -p "${CACHE_ROOT}"/{cache/{kit,ov,pip,glcache,computecache},logs,data,documents} "${WORKSPACE}"
docker compose up -d --build
echo "container up. entering shell (exit to leave it running; ./scripts/down.sh to stop)"
docker compose exec isaaclab bash
