# State与Memory模式导航

> 状态：draft | 来源核验：2026-09-06

| 当前问题 | 看哪里 | 验证重点 |
| --- | --- | --- |
| 进程恢复后不知道继续哪一步 | [State与Checkpoint](../01-concepts/01-state-and-checkpoints.md) | 版本、状态完整性、证据产物 |
| 什么值得记住，怎么召回 | [写入与召回](01-memory-write-and-retrieval.md) | 主体、来源、时效先于相关性 |
| 新旧事实矛盾或已被删除 | [冲突与遗忘](02-conflict-and-forgetting.md) | 明确作用域、CAS、墓碑、缓存 |
| 记忆越多效果越差 | [Memory评测](../01-concepts/03-memory-evaluation.md) | 区分写入、读取和使用错误 |

[完整实现](../05-code/state-memory-python/README.md)以SQLite存储教学事实，默认拒绝无版本的覆盖。生产数据服务还需真正的身份认证、资源授权、备份保留和索引失效策略。
