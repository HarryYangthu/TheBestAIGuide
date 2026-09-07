# 生产工程：容量、可靠性与可恢复发布

> 状态：draft · 更新：2026-09-06

本域从“能跑一次”推进到“流量增加和出现故障时如何运行”。公式用教学参数说明口径，生产结论需要真实压测和观测。

| 阅读顺序 | 核心能力 | 实践 |
|---|---|---|
| [部署与容量](01-concepts/01-deployment-and-capacity.md) | 分清 Worker、模型和工具限制 | [容量算例](05-code/production_checks.py) |
| [SLO 与成本](01-concepts/02-slos-reliability-and-cost.md) | 区分接口可用、任务成功与单位成功成本 | [公开 SLO 方法案例](03-cases/production-systems/README.md) |
| [发布与恢复](01-concepts/03-release-and-recovery.md) | 版本、灰度、回滚与副作用恢复 | [重复写入复盘](03-cases/failure-postmortems/README.md) |

[代码说明](05-code/README.md)记录实跑范围；[来源索引](references.md)连接 Google SRE 与 Kubernetes 官方文档。本库没有部署生产服务，也没有把本地算例当作容量压测或真实事故。

## 看一次真实排队

从仓库根目录运行 `python scripts/run_python.py -m learning_workbench.cli queue --output .runs/queue`，比较无界队列与短队列的输出。先检查 `completed + len(rejected) == arrivals`，再比较时延；拒掉大半请求后得到更低 p95，并不表示同样负载下服务能力提高。[实现](../../20-Projects/learning-workbench/src/learning_workbench/experiments.py)实际运行 asyncio Worker，但工作负载是固定等待与人工重试，测出的秒数不能作为模型吞吐指标。
