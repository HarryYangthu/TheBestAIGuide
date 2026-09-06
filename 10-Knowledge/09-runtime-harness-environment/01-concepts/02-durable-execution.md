# 持久执行：恢复时究竟要重做什么

> 状态：draft；来源核验：2026-09-06；本地恢复与幂等实验已实跑，生产能力不在验证范围内。


最危险的故障窗口不在调用之前，而在“对方做完了，我还没记住”之间。例如扣款服务已扣 10 元，但本地在写回执前断电；恢复程序只看到 `pending`，再次扣款就可能扣两次。本实验把金额当作本地整数计数，不涉及真实资金。

## Checkpoint、Resume、Replay 各做什么

Checkpoint 是保存的运行状态，例如某个逻辑步骤已经完成、输入是 10、回执为哪一条记录。Resume 读取这个状态继续未完成的工作。Replay 根据已有事件重新计算状态或回答，用于追查和恢复投影。

Replay 不应无条件重新调用所有工具。重放一次历史请求如果再次发送邮件或扣款，就改变了真实世界，也不再是“重看历史”。本例的 `replay(events)` 只是遍历 `prepared/completed/compensated` 事件，生成状态字典，完全不拿 Ledger 对象。

```python
state = {}
for event in events:
    if event["event"] == "completed":
        state[event["step_id"]] = {
            "status": "completed", "result": event["payload"]
        }
```

完整归约器还处理准备与补偿事件，见[recovery.py](../05-code/recoverable-runtime-python/src/recoverable_runtime/recovery.py)。事件顺序由数据库递增序号决定，不能依赖不同机器的墙钟时间恰好一致。

## 三个崩溃位置，恢复策略为什么不同

| 崩溃点 | 本地确认的状态 | 外部效果 | 恢复动作 |
|---|---|---|---|
| 调用之前 | pending | 没发生 | 使用原幂等键调用 |
| 外部提交后、Checkpoint 前 | pending | 已发生，但本地不知道 | 用同键查询或重试，让服务返回原效果 |
| Checkpoint 提交后、响应前 | completed | 已发生 | 返回已存回执，不重复调用 |

第二行叫“结果未知”，不能等同失败。超时也可能发生在这个窗口。重试安全取决于服务端按幂等键去重，而不是客户端“尽量不重试”。

## 代码如何把窗口保留下来

实验用两个独立 SQLite 文件：`events.sqlite` 保存 Runtime 的步骤与事件，`ledger.sqlite` 保存模拟服务的业务记录。它们没有共享事务，故意保留跨系统提交窗口。

`LocalLedger.charge(key, amount)` 在事务中尝试插入唯一 key；若 key 已存在，则检查 amount 是否一致。同 key 同参数返回原结果，同 key 改参数拒绝。`EventStore.finish` 在另一个事务中同时写完成状态和完成事件，避免本地状态与本地日志互相矛盾。

这个设计实现了“允许多次尝试，但同一逻辑动作只有一条账本记录”。不要泛化成所有系统都能 exactly once：如果外部系统既不支持幂等键，也不能查询动作结果，本地 Checkpoint 无法消除这个未知窗口。

## 恢复需要固定哪些身份

恢复必须使用原来的 `run_id` 和 `step_id`；重新生成 ID 会被服务当作新动作。还要固定输入参数或其哈希、工具版本和所依据的数据版本。若更新代码改变了步骤含义，同样的 ID 也可能代表不同意图，这时应迁移状态或开启新 Run。

本例将 `[run_id, step_id]` 序列化成 JSON 作为键，避免用冒号拼接时 `("a:b","c")` 与 `("a","b:c")` 撞键。账本只有整数金额，真实服务还应覆盖币种、目标对象、租户和完整动作参数。

打开[Notebook](../04-labs/01-recovery-and-idempotency.ipynb)，在三个位置分别抛出故障，关闭并重新打开数据库，再恢复执行。记录条数而不仅是最后返回值，是判断是否重复副作用的关键。背景参考 [AWS 幂等 API](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) 与 [LangGraph 持久化](https://docs.langchain.com/oss/python/langgraph/persistence)。
