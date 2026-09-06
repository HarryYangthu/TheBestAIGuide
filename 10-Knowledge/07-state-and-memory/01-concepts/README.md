# State、Session、Checkpoint、Memory与Context

> 状态：draft | 来源核验：2026-09-06

| 概念 | 精确定义 | 不应混淆 |
| --- | --- | --- |
| State | 当前任务继续执行所需的权威运行事实 | 一段可能失真的对话摘要 |
| Session | 一段交互或运行边界 | 不自动等同于任务状态或长期记忆 |
| Checkpoint | 某个一致位置的持久状态快照/事件位置 | 不自动保证外部副作用恰好执行一次 |
| Memory | 为未来任务选择性保留和检索的信息 | 全部历史日志或模型参数 |
| Context | 本次模型调用实际可见的输入 | 数据库全部内容 |

State按run_id精确加载，Memory通常按主体、范围、时效与相关性选择。State可以进入Checkpoint，其中少量事实经来源和用途检查后写入Memory；未来召回的Memory再由Context构造器筛选，不能静默覆盖当前任务约束。

先读[State与Checkpoint](01-state-and-checkpoints.md)，再读[Memory生命周期](02-memory-lifecycle.md)，最后读[Memory评测](03-memory-evaluation.md)。这三篇展开本速查里的机制、代码与边界。
