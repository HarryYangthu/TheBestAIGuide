# State与Memory来源

> 状态：draft | 核验日期：2026-09-06

| 一手资料 | 使用位置 | 边界 |
| --- | --- | --- |
| [SQLite事务](https://www.sqlite.org/lang_transaction.html) | BEGIN IMMEDIATE、提交与回滚 | 本地数据库事务不覆盖外部服务副作用 |
| [SQLite隔离](https://www.sqlite.org/isolation.html) | 并发连接与已提交状态 | SQLite WAL checkpoint与Agent状态快照不同 |
| [MemGPT，arXiv:2310.08560](https://arxiv.org/abs/2310.08560) | 有限上下文与外部记忆分工 | 不复现论文模型控制策略或基准成绩 |

写入规则、CAS接口、评测样例与TTL设置为本库教学设计；不声称是上述论文给出的唯一实现。
