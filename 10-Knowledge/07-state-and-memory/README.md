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

## 读完存储之后，追一次完整使用过程

在 [Learning Workbench](../../20-Projects/learning-workbench/README.md)运行 `memory` 任务，然后同时打开[输入题目](../../20-Projects/learning-workbench/fixtures/memory-tasks.jsonl)、[提取与回答代码](../../20-Projects/learning-workbench/src/learning_workbench/memory.py)和[逐题结果](../../20-Projects/learning-workbench/artifacts/offline/memory.json)。沿 m0 追“长期表格偏好 → 写入 → 下一会话召回 → 表格回答”，再看 m3 的当前段落要求为什么胜过旧偏好。它使用规则提取和固定知识回答，8/8 只说明这些格式与生命周期用例通过，不能外推通用记忆模型效果。
