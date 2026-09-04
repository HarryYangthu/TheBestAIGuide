# Evaluation 与 Observability

> 状态：draft
> 学习目标：用可复现任务和可观察证据判断 Agent 系统是否正确、稳定、高效且安全。

## 前置知识

- Agent Loop、Runtime、State、Tool Call 和外部环境结果。
- 基本统计、数据划分和软件测试概念。

## 连续学习顺序

1. [Agent Evaluation 总览](01-concepts/00-overview.md)
2. [评测对象与系统模型](01-concepts/01-evaluation-model.md)
3. [任务、数据集与多次试验](01-concepts/02-tasks-datasets-and-trials.md)
4. [评分器与组合计分](01-concepts/03-graders-and-scoring.md)
5. [统计与可靠性](01-concepts/04-statistics-and-reliability.md)
6. [Trace 与失败归因](01-concepts/05-traces-and-failure-analysis.md)
7. [Multi-Agent 系统评测](01-concepts/06-multi-agent-evaluation.md)
8. [评测运营与发布门禁](02-patterns/01-evaluation-operations.md)
9. [模板与检查清单](02-patterns/02-templates-and-checklists.md)
10. [实验入口](04-labs/README.md)、[Eval Harness 骨架](05-code/eval-harness-python/README.md)与[来源索引](references.md)

## 当前证据边界

- 正文已经区分 Task、Trial、Trajectory、Outcome、Grader 与 Harness。
- Schema、阈值和门禁是设计模板，不是运行结果。
- Lab 与 Eval Harness 仍为占位，因此状态保持 `draft`。
