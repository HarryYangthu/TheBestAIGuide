# State与Checkpoint：恢复的是运行事实

> 状态：draft | 来源核验：2026-09-06 | SQLite快照、恢复和版本冲突已实测

检索任务已经找到两篇文档，进程却在写答案前退出。重启之后，系统需要知道的是“哪个任务、已经完成什么、证据在哪里、还剩多少预算”，不能靠模型读一段聊天记录猜测当前进度。这些必须精确恢复的事实组成State。

| 对象 | 回答的问题 | 本例字段 |
| --- | --- | --- |
| State | 现在运行到了哪里 | task、step、document_ids、budget_left、status |
| Event | 刚才发生了什么 | 第1次搜索成功，返回doc-1/doc-2 |
| Checkpoint | 从哪个一致位置继续 | State快照与版本号 |
| Memory | 将来其他任务值得记住什么 | 用户偏好、已验证经验及来源 |
| Context | 本次模型实际看到什么 | 目标＋State摘要＋被选中的证据 |

State不是所有信息的大合集。PDF正文适合保存为产物，State记录内容哈希和路径；临时对象、打开的数据库连接或不可序列化句柄不应该直接塞入快照。跨版本恢复还需要schema版本和迁移规则，本教学实现只接受同一版本JSON对象，没有自动迁移。

## 为什么一个save函数需要版本号

假设A和B都读到版本3。A把步骤推进到4；B稍后把旧状态里的预算改小并保存，若直接覆盖整份对象，步骤可能退回3。这是丢失更新，数据库写成功也不能说明业务状态正确。

比较并交换（CAS）要求写入者携带读取时版本：

$$save(s',v_e)\text{ succeeds iff }v_e=v_{stored},\qquad v_{new}=v_{stored}+1.$$

$v_e$是调用方预期版本，$v_{stored}$是数据库实际版本。A用3写入得到4，B再用3就被拒绝；B必须重新读取，决定如何合并，不能让数据库猜业务优先级。

```python
from state_memory import CheckpointStore, VersionConflict
store = CheckpointStore(":memory:")
version = store.save("run-1", {"step": 1, "document_ids": ["doc-1"]})
version = store.save("run-1", {"step": 2, "document_ids": ["doc-1"]},
                     expected_version=version)
print(store.load("run-1"))
store.close()
```

## 事务保护的范围

[checkpoint.py](../05-code/state-memory-python/src/state_memory/checkpoint.py)在`BEGIN IMMEDIATE`事务中读取版本、检查并插入新快照，成功提交，异常回滚。SQLite会序列化写事务，因此两个连接不会同时通过同一版本检查。本实现适合本地教学和低并发状态存储；分布式高并发场景需要结合实际数据库和锁竞争做设计。

事务只能保护参与同一事务的数据库操作。假如已经向外部服务提交付款，随后保存Checkpoint失败，数据库回滚不会撤销付款。恢复后重新执行动作会产生重复副作用。因此“保存了Checkpoint”不等于“恢复后每个外部动作恰好执行一次”。需要外部业务幂等键、结果查询或补偿，见[持久运行领域](../../09-runtime-harness-environment/README.md)。

注意SQLite自身还有WAL checkpoint概念，即将预写日志内容合并到数据库文件；它与本篇“Agent状态快照”的Checkpoint不是同一个层次。

## 恢复后先核验什么

检查目标是否仍有效、代码/schema版本是否兼容、证据产物是否存在且哈希匹配、待执行副作用是否已完成、预算和授权是否过期。不能因为历史状态写着“允许读取”就假设今天仍有权限。

在[Notebook](../04-labs/01-state-memory-and-conflicts.ipynb)中打开两个独立连接，观察旧版本写入如何被拒绝。官方依据：[SQLite事务](https://www.sqlite.org/lang_transaction.html)、[隔离语义](https://www.sqlite.org/isolation.html)。
