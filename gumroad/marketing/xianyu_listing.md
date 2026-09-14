标题（30 字内）：Isaac Lab 一键环境包 实测显存预设 报错手册 URDF检查 4060可跑

价格：¥99

正文：
Isaac Lab Fast-Track 安装包，Isaac Lab 2.3.2 + Isaac Sim 5.1.0 锁定版本，Ubuntu 22.04 实测通过。

不是远程装机，是一套文件：拿到后自己跑三条命令，preflight 先告诉你机器哪里不行，再拉镜像、跑冒烟测试，5 分钟知道能不能训练。

包含：
- Docker 镜像定义 + compose，缓存持久化，不用每次重下扩展
- preflight 体检脚本：驱动、显存、内存、磁盘、Docker、containerd 位置、CPU 调度器、网络
- 3060 12G 实测显存表：8 个官方任务 × 512 到 4096 环境，4060 8G 怎么设一目了然，做成 ft-train 一条命令
- 14 条报错手册：首次启动假死、DLL load failed、carb 崩溃、NaN reward、CUDA OOM、Nucleus NoneType、Docker 28 之后系统盘被填满
- URDF 检查工具：零质量、惯量不正定、运动树断裂、视觉网格当碰撞体，在 Isaac 炸之前抓出来
- 自定义 URDF 的 Direct RL 训练模板，改一个文件换机器人
- 国内网络：pip 镜像、离线资产包说明
- Windows 11 路线（WSL2）：安装路径验证通过，训练未验证，文档如实写了

适合：4060 笔记本、8G 到 12G 显卡、Windows 想转 Ubuntu、毕设或课程项目不想把半学期耗在装环境上的。

不适合：需要 Isaac Lab 3.0 / Isaac Sim 6.0 的（后续免费更新）、AMD 卡、Mac（文档里有云端方案）。

售后：拍下发网盘链接，硬件达到标称最低配置（Ubuntu 22.04、驱动 580+、8G 显存）但冒烟测试跑不过，7 天内邮件没解决全额退款。作者前 Apple 系统工程师，现做机器人强化学习。

英文版商品页（同一份文件）：appleddliu.gumroad.com/l/isaac-lab-fasttrack
