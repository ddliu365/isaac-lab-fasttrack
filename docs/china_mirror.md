# 国内网络：让下载不再卡死

三个卡点：pip 装 isaacsim（几 GB）、docker pull（20 GB）、运行时从 NVIDIA CDN 拉 assets（几十 GB，最常见的“NoneType”和“一直 Loading”）。

## 1. pip
```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# isaacsim 只在 NVIDIA 源上，保留 extra-index，走代理或耐心等：
pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com
```
torch 用清华的 pytorch 镜像或直接走代理；cu128 wheel 约 900 MB。

## 2. docker pull
nvcr.io 没有国内镜像。可行做法：
- 在有海外线路的机器上 `docker pull` 后 `docker save | gzip` 成 tar，拷回来 `docker load`（bundle 后续会提供百度网盘/阿里云盘包，待验证体积）。
- 或在 Docker daemon 配置 `"proxies"` 走本地代理。

## 3. 运行时 assets（关键）
Isaac Sim 5.x 提供 Isaac Sim Assets 离线包（分 3 个 zip，约 40-90 GB）。解压到本机后，在容器里把资产根路径指到本地：
```
docker/.env:  LOCAL_ASSETS=1  LOCAL_ASSETS_PATH=/data/isaac-assets
```
容器内脚本 `ft-assets-local` 会把 `/persistent/isaac/asset_root/default` 设置为 `/isaac-assets`，之后所有
`ISAAC_NUCLEUS_DIR` 引用都走本地磁盘，不再联网。（该脚本在 GPU 机器上验证后加入。）

## 4. 验证
```bash
./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py --headless   # 不联网也应在 60 s 内完成
```
