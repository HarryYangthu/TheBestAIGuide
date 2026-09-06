# State与Memory

> 状态：draft | 实测范围：SQLite快照、恢复、版本冲突、过期、删除与主体隔离

State保存当前任务继续执行所需的权威事实，Memory保留未来可能有用的信息。先保证任务状态可靠，再讨论跨任务记忆。

| 顺序 | 文章 | 配套实现 |
| --- | --- | --- |
| 1 | [State与Checkpoint](01-concepts/01-state-and-checkpoints.md) | SQLite事务、CAS、跨连接恢复 |
| 2 | [Memory生命周期](01-concepts/02-memory-lifecycle.md) | 来源/主体/时效/版本数据模型 |
| 3 | [写入与召回](02-patterns/01-memory-write-and-retrieval.md) | 先隔离过滤，再子串检索 |
| 4 | [冲突与遗忘](02-patterns/02-conflict-and-forgetting.md) | 显式更新、TTL和删除墓碑 |
| 5 | [Memory评测](01-concepts/03-memory-evaluation.md) | 无记忆/全量/过滤对照及错误分类 |

[概念速查](01-concepts/README.md)保留State、Session、Checkpoint、Memory、Context边界；[模式导航](02-patterns/README.md)便于按故障找方案。[工程](05-code/state-memory-python/README.md)与[Notebook](04-labs/01-state-memory-and-conflicts.ipynb)共用源码，全部为本地教学数据。来源见[参考资料](references.md)。

## 配套项目扩展（2026-09-06）

[跨会话提取、写入、召回与最终回答对照](../../20-Projects/learning-workbench/README.md)已提供源码、输入数据、运行入口和实际结果。默认机制验证与可选真实模型结果分开记录，具体适用范围见项目说明。
