标题：实测：Isaac Lab 在 12G 显卡上 8 个官方任务全部能跑 4096 环境，"最低 16G 显存"说的是渲染不是训练

每隔几天就能看到一篇"4060 笔记本装 Isaac Lab 失败"的帖子，最后要么换 Ubuntu 要么转投 Isaac Gym。官方文档写的最低配置是 32G 内存 + 16G 显存，很多人在选型阶段就被这行字劝退了。我手上有一台 RTX 3060 12G（驱动 580.173，Ubuntu 22.04，官方 isaac-lab:2.3.2 容器，Isaac Sim 5.1.0），花了一个下午把数字实测出来。

方法：rsl_rl PPO，--headless，每组跑 20 轮，nvidia-smi 每秒采样取峰值显存。每个任务分别跑 512 / 1024 / 2048 / 4096 个环境。

任务 | 512 | 1024 | 2048 | 4096 | 4096 时每秒步数
Cartpole | 4.7G | 4.7G | 4.9G | 5.1G | 24.4 万
Ant | 4.7G | 4.9G | 5.3G | 6.0G | 15.8 万
Humanoid | 4.8G | 5.1G | 5.5G | 6.5G | 11.0 万
Anymal-C 平地 | 4.9G | 5.1G | 5.4G | 6.1G | 7.9 万
Anymal-C 粗糙地形 | 5.6G | 6.0G | 6.5G | 7.8G | 1.4 万
宇树 Go2 平地 | 4.8G | 5.0G | 5.4G | 6.1G | 8.3 万
Franka reach | 4.6G | 4.8G | 5.1G | 5.5G | 14.7 万
Franka 开抽屉 | 4.9G | 5.3G | 5.9G | 7.3G | 5.9 万

几个结论：

1. 无头模式下 Isaac Sim 还没建环境就占 4.5G，这就是评论区常说的"啥也没跑就吃了 4.5G"。它是 Kit 运行时的固定开销，开 GUI 会更多。
2. 之后每增加 3500 个环境只多 1 到 3G，取决于接触复杂度。12G 显卡上 8 个官方任务 4096 环境全部能跑。
3. 8G 显卡：除粗糙地形和开抽屉外都能跑满 4096，这两个降到 2048（6.5G / 5.9G）也能跑。所以 4060 笔记本可以用，前提是训练时永远别开 GUI。
4. 16G 这个数字对渲染工作流（相机、RTX 传感器）是真的，对状态输入的强化学习高了一倍。

两个比基准测试本身更浪费时间的坑：

- 官方教程 scripts/tutorials/00_sim/create_empty.py 是个设计上的死循环，无头模式下看起来像卡死，其实没有，Ctrl-C 就行。
- Docker 28 以后镜像层存在 /var/lib/containerd，不在 data-root 下面。我把 data-root 指到大盘，拉了 26G 镜像，系统盘照样满了。

顺便试了 Windows 路线（WSL2 + Docker Engine，3050 Ti 4G）：安装全通，容器里能看到 GPU，Isaac Sim 8 秒启动，然后 PhysX 报 "GPU Bp pipeline failed, switching to software" 就挂住。分不清是 4G 的锅还是 WSL2 的锅，有 8G 以上显卡在 WSL2 上跑过的朋友欢迎在评论区说一声。

驱动那件事也说一下：评论区流传"580 以上卡死要回退 535"，那位作者后来自己发现是首次启动编译着色器，无响应两分钟是正常的。550 到 596 的驱动都有人跑通。

---

利益相关：我把这套东西打包成了付费的安装包，因为装环境是所有人都要丢一周的地方。Isaac Lab Fast-Track，$49：锁定版本的 Docker 镜像和 compose（带持久缓存，不用每次重下扩展）、一个 preflight 体检脚本（驱动 / 显存 / 内存 / 磁盘 / Docker / containerd 位置 / CPU 调度器）、上面的实测预设做成了 ft-train <任务> <8g|12g|16g|24g> 一条命令、14 条报错手册（DLL load failed、carb 崩溃、NaN reward、CUDA OOM、Nucleus NoneType、上面两个坑）、一个 URDF 检查工具（零质量、惯量不正定、运动树断裂、视觉网格当碰撞体，在 Isaac 炸之前抓出来）、一个自定义 URDF 的 Direct RL 训练模板。国内网络的 pip 镜像和离线资产包说明也在里面。Ubuntu 22.04 验证通过；WSL2 安装路径验证通过，训练未验证。硬件达到标称最低配置但冒烟测试跑不过，全额退款。

购买链接：https://appleddliu.gumroad.com/l/isaac-lab-fasttrack
国内不方便用 Gumroad 的，闲鱼搜"Isaac Lab Fast-Track"，¥99，同一份文件。

数据有疑问评论区随时问。
