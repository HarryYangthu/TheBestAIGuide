# Runtime、Harness 与 Environment

> 状态：draft；来源核验：2026-09-06；本地恢复、回放、幂等和补偿为 verified 范围。

本域回答“模型已经提出动作，程序怎样可靠执行”。贯穿案例是本地模拟账本：在动作前后故意中断，观察恢复是否重复产生效果。

| 学习问题 | 正文 | 动手入口 |
|---|---|---|
| Run、Step、Event 和 Harness 分别负责什么 | [运行对象与分层](01-concepts/01-runtime-and-harness.md) | [Runner](05-code/recoverable-runtime-python/src/recoverable_runtime/runner.py) |
| 崩溃后该重做还是返回原结果 | [持久执行](01-concepts/02-durable-execution.md) | [Notebook](04-labs/01-recovery-and-idempotency.ipynb) |
| 如何限制并发、排队与重试开销 | [并发和预算](01-concepts/03-concurrency-and-budgets.md) | [配套并发实现](../08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/README.md) |
| 目录、沙箱、产物怎么区分 | [执行环境](01-concepts/04-workspaces-sandboxes-and-artifacts.md) | [安全边界实验](../11-safety-security-governance/04-labs/01-policy-and-injection.ipynb) |
| 如何处理未知结果和已提交动作 | [重试、幂等与补偿](02-patterns/01-retry-idempotency-compensation.md) | [恢复测试](05-code/recoverable-runtime-python/tests/test_recovery.py) |

[工程说明](05-code/recoverable-runtime-python/README.md) · [实验说明](04-labs/README.md) · [来源索引](references.md) · [State / Memory](../07-state-and-memory/README.md)

## 配套项目扩展（2026-09-06）

[持久 Run API、审批、取消与事件补发](../../20-Projects/learning-workbench/README.md)已提供源码、输入数据、运行入口和实际结果。默认机制验证与可选真实模型结果分开记录，具体适用范围见项目说明。
