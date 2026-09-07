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

## 从本地恢复继续学服务生命周期

先完成账本 Notebook，再进入 [Workbench Run 服务](../../20-Projects/learning-workbench/README.md)：创建一次 Run，读取版本号后批准，观察事件，再试取消与重连。[server.py](../../20-Projects/learning-workbench/src/learning_workbench/server.py)展示持久状态与事件补发；取消是协作式的，已经开始的只读计算可能继续，但不再发布完成结果。

读完应能回答：pending 是否等于没有副作用？Replay 为什么可能仍显示 pending？相同 ID 重试与新建 Run 有什么区别？如果不能用账本行数与事件解释，回到持久执行的三个崩溃窗口再运行一次。
