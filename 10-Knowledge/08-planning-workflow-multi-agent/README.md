# Planning、Workflow 与 Multi-Agent

> 状态：draft；正文已补全；配套 Python 实现、故障实验为本地 verified 范围。来源核验：2026-09-06。

本域从“如何在约束内选择一个候选模型”讲清任务分解、控制权、结果交接和冲突。先判断确定性程序能否完成，再决定是否需要动态规划或多个 Agent。

| 学习问题 | 正文 | 对应实现 / 实验 |
|---|---|---|
| 怎么把目标变成能验收的子任务 | [规划与重规划](01-concepts/01-planning-and-replanning.md) | [任务契约](05-code/multi-agent-runtime-python/src/multi_agent/contracts.py) |
| 下一步什么时候允许发生 | [状态机与 DAG](01-concepts/02-workflow-state-machines.md) | [协调器](05-code/multi-agent-runtime-python/src/multi_agent/supervisor.py) |
| 谁决定下一步、为何要多 Agent | [协作拓扑](01-concepts/03-multi-agent-topologies.md) | [路由器](05-code/multi-agent-runtime-python/src/multi_agent/router.py) |
| 子任务输入输出如何约定 | [交接契约](02-patterns/01-task-contract-and-handoff.md) | [测试](05-code/multi-agent-runtime-python/tests/test_runtime.py) |
| 结果不一致或部分失败怎么办 | [共享状态与合并](02-patterns/02-shared-state-and-merge.md) | [合并器](05-code/multi-agent-runtime-python/src/multi_agent/merge.py) |
| 加入协作是否值得 | [完整案例](03-cases/01-single-vs-multi-agent.md) | [运行 Notebook](04-labs/01-single-vs-multi-agent.ipynb) |

[工程运行说明](05-code/multi-agent-runtime-python/README.md) · [实验入口](04-labs/README.md) · [来源](references.md) · [多 Agent 评测](../10-evaluation-observability/01-concepts/06-multi-agent-evaluation.md)
