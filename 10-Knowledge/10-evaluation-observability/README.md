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
10. [实验入口](04-labs/README.md)、[Eval Harness 实现](05-code/eval-harness-python/README.md)与[来源索引](references.md)

## 当前证据边界

- 正文已经区分 Task、Trial、Trajectory、Outcome、Grader 与 Harness。
- Schema、阈值和门禁是设计模板，不是运行结果。
- Lab 与 Eval Harness 已实现四任务教学实验；正文保持 `draft`，表示尚未完成人工审阅。Workbench 另有真实模型结果；二者都没有独立专家校准证据。

## 完整实践

[从任务数据到回归门禁](03-cases/01-from-task-dataset-to-regression.md)：一套带真实输出的教学案例，把数据构造、状态评分、失败定位、修复和回归接起来。

## 用已有结果练习判断，不急着再跑模型

| 读什么 | 要判断的问题 | 核对位置 |
|---|---|---|
| [统计正文](01-concepts/04-statistics-and-reliability.md) | 为什么 9/12 和 45% 都对？超时算不算分母？ | 微/宏平均与成本算例 |
| [评分正文](01-concepts/03-graders-and-scoring.md) | Judge 3/6 错在哪里？格式失败能否算顺序偏差？ | 已保存的真实模型报告 |
| [Workbench](../../20-Projects/learning-workbench/README.md) | 怎样替换真实系统并保留同一评分口径？ | 模型适配、Task 配对 bootstrap、位置交换 |

读完应能自己写一条 Task，指出标签由谁保存，运行后用 Outcome 验证而非相信自述，再说清分母、失败类型和下一步修改。四题全过只说明这四题的已知条件成立。
