# Positioning and price (internal, not shipped)

## Who else sells into this pain (from the 56-thread excerpt, 2026-09-13)
| Seller | What | Price | Where |
|---|---|---|---|
| 闲鱼 卖家 A | ToDesk 远程装 Isaac Sim 5.1 + Lab 2.3, 测通基础模型, 装不好全退 | ¥98 (+¥30 调参介绍) | goofish 1042480622431 |
| 闲鱼 卖家 B | 远程装 sim/lab/gym 任意版本, 含驱动/CUDA/conda, 不含使用指导 | 未标 | goofish 920959273662 |
| 闲鱼 课程 | 72 节 Isaac Sim RL 录播 / 9.5h 英文课中字 / URDF 导入 HTML 教程 | 几十元 | goofish |
| gpulab | 远程图形化云开发机, 一键 Isaac Lab | 按量 | 知乎评论区推广 |
| gradmotion (逐际动力) | 预置 Isaac 环境一键训练, 注册送算力 | 免费起 | 知乎评论区推广 |
| 算力自由 gpufree.cn | 4090 + IsaacLab 镜像 | ¥1.38/h | 知乎正文推荐 |
| SimuCode | 浏览器 ROS2 刷题, Isaac 在路线图 | 免费 MVP | Reddit |

## What this means
- **Cloud is taken.** Two CN platforms give away compute; do not build a workspace product.
- **CN price anchor is ¥98 for a human doing it by remote desktop.** A ¥350 self-serve kit loses to that on 闲鱼.
  CN version, if any: ¥99-149, sold on 闲鱼/知乎, positioned as "装完之后的东西" (低显存预设、报错手册、URDF 模板), not as install.
- **EN market has no anchor.** Reddit's answer is still "install Ubuntu". $49 on Gumroad is uncontested; the
  competition is free docs and a two-week detour.
- **The differentiator is not the install; it is the four things nobody has written down:** GPU x OS decision tree,
  driver reality table, low-VRAM presets with measured numbers, and a URDF-to-training template that explains
  "jerks but never walks". Lead with those in the copy; the Docker image is the delivery mechanism.
