# State与Checkpoint：恢复的是运行事实

> 状态：draft。配套 SQLite 快照、重载和版本冲突测试已在本地离线运行；本文的完整恢复流程属于设计说明。

Pine SDK 升级清单已经写到一半，进程突然退出。重新启动时，你希望它接着比较重试设置，而不是从头搜索，也不希望它看到一个 `report.md` 就宣布完成。程序必须分清：读过哪些资料、报告写到哪一版、哪些检查真的通过、还有多少预算。

这些需要准确记录的运行事实叫 **State，任务状态**。Checkpoint 是某个时刻保存下来、供以后恢复的状态快照。它们解决的是程序进度与数据一致性问题，不要求由模型来实现。

## 先分清状态、事件和产物

同一次读文件，可以留下三种不同记录：事件说“刚刚读成功”，状态说“现在已有哪份证据”，产物保存“实际读到了什么”。少了其中任何一个，都可能难以解释或恢复运行。

| 对象 | Pine SDK 任务中的例子 | 为什么单独保存 |
| --- | --- | --- |
| State | `status=running`，待比较 retry，剩余 6 次调用 | 下一步决策要读取当前值 |
| Event | 第 4 次调用读完 `v2.md` | 排查事情发生的先后顺序 |
| Artifact，产物 | 源文档快照、清单第 2 版、验收报告 | 保存完整证据和真正交付的文件 |
| Checkpoint | 任务状态的第 7 版快照 | 重启后从已知位置继续 |
| Context | 当前目标、进度摘要及选中的原文 | 这一次交给模型的信息 |
| Memory | 用户通常希望清单使用表格 | 以后其他任务仍可能有用 |

State 不是把所有文件塞进一个大 JSON。报告、代码、图片或 PDF 可以很大，还可能被多个步骤复用；状态通常只保存它们的标识、版本、位置和内容哈希。哈希可以用于检查“还是不是当时那份内容”，并不能证明报告结论正确。

数据库连接、打开的文件句柄也不宜直接保存。重启后原来的进程对象已经不存在，需要依据配置重新创建，再载入能序列化的数据。

## 一次任务的状态怎样变化

下面是教学设计，不是 Mini Agent 现有字段的原样复制。它刻意把“报告写出来”和“报告验收通过”分开。

| 事件发生后 | `status` | `next_step` | `report_ref` | `acceptance` |
| --- | --- | --- | --- | --- |
| 创建任务 | `pending` | 读正式文档 | `null` | `not_run` |
| 两份原文已保存 | `running` | 比较三项变更 | `null` | `not_run` |
| 生成清单第 1 版 | `running` | 检查引用与字段值 | `report-v1` | `not_run` |
| 查出引用预览稿 | `running` | 更正 auth 的来源 | `report-v1` | `failed` |
| 第 2 版检查通过 | `completed` | `null` | `report-v2` | `passed` |

这里的状态更新应由程序根据工具与验收结果执行。模型可以说“我已完成”，但代码必须检查报告是否存在、内容是否满足要求，再决定能否进入完成状态。超时、取消和失败也应有明确状态，不能一律归为“结束”。

如果任务需要用户补充资料，可以进入 `waiting_input`；用户回答后再回到 `running`。这是一条状态转移规则：等待期间不能继续执行依赖该信息的操作。定义这些转移，让恢复程序有据可依，而不是每次重启都让模型猜下一步。

Mini Agent 目前把运行结束记为 `status="completed"`，把验收是否通过另存在 `acceptance.json`。因此查看它的结果时必须同时看两者。这个区别也说明字段名本身不足以证明任务成功，要看代码赋予它什么含义。

## 状态怎样指向真实产物

设状态中有以下教学记录：

```json
{
  "run_id": "pine-upgrade-17",
  "schema_version": 1,
  "status": "running",
  "next_step": "verify_report",
  "report": {"id": "report-v2", "path": "artifacts/report-v2.json", "sha256": "实际文件内容的哈希"},
  "inputs": ["pine-v1-snapshot", "pine-v2-snapshot"],
  "calls_left": 6
}
```

恢复时，`report.path` 让程序找到文件，`sha256` 让程序发现内容是否变化，输入快照标识让它找回当时用于比较的文档。如果只保存可被反复覆盖的 `report.json` 路径，后来另一个任务改了它，旧状态仍会指向同名文件，却不再对应原来的成果。

因此一种常见做法是给每版产物独立标识，先写完产物，再保存引用它的状态。先保存“报告已写完”，后写文件，中途退出就会出现空引用。反过来先写文件再保存状态，中途退出可能留下尚未被引用的文件；它至少不会被误认为已完成，可在恢复时核对或随后清理。涉及多个存储系统时，单靠两行代码仍不能获得跨系统事务，需要额外的提交记录与恢复规则。

## 为什么一个save函数需要版本号

多 Agent 共享状态时，即使每次写文件都成功，也可能互相覆盖。看下面的明确时间顺序，A 负责推进步骤，B 负责记录预算，二者最初读到同一份数据：

| 时刻 | 操作 | 存储中的状态 |
| --- | --- | --- |
| 1 | A、B 均读取版本 3 | `step=3, calls_left=8` |
| 2 | A 完成比较，保存 `step=4` | 版本 4：`step=4, calls_left=8` |
| 3 | B 在自己的旧副本里把预算减到 7，覆盖整份状态 | 若不检查版本，会变成 `step=3, calls_left=7` |

B 只想修改预算，却把 A 已完成的进度退回去了。这叫**丢失更新**。CAS，即比较并交换，要求写入时带上“我基于哪个版本修改”：只有该版本仍是最新版本，才允许保存。

$$\text{允许保存}\iff v_{\text{expected}}=v_{\text{stored}},\qquad v_{\text{new}}=v_{\text{stored}}+1.$$

在上例中，A 携带 3，数据库也是 3，所以保存后变为 4；B 仍携带 3，数据库已经是 4，因此拒绝。B 随后应该读取版本 4，确认预算变化还适用，再合并成 `step=4, calls_left=7`。不能捕获冲突后直接把预期版本改成 4，再照旧覆盖，那只是绕过了保护。

以下调用的是本库真实的 [`CheckpointStore`](../05-code/state-memory-python/src/state_memory/checkpoint.py)。使用一个尚不存在的 `.runs/pine-state.db`，并按配套 README 配置 Python 导入路径：

```python
from pathlib import Path
from state_memory import CheckpointStore, VersionConflict

Path(".runs").mkdir(exist_ok=True)
a = CheckpointStore(".runs/pine-state.db")
b = CheckpointStore(".runs/pine-state.db")
a.save("pine-17", {"step": 3, "calls_left": 8})
va, sa = a.load("pine-17")
vb, sb = b.load("pine-17")
sa["step"] = 4
a.save("pine-17", sa, expected_version=va)
sb["calls_left"] = 7
try:
    b.save("pine-17", sb, expected_version=vb)
except VersionConflict as error:
    print(error)
print(b.load("pine-17"))
a.close()
b.close()
```

这段代码第一次保存得到版本 1，第二次得到版本 2；因此应打印 `expected 1, actual 2`，随后读到 `(2, {'step': 4, 'calls_left': 8})`。预算仍是 8，表示 B 的修改确实被拒绝了；它没有被偷偷合并。数字不同于前面的版本 3 算例，冲突机制相同。

## 事务保护的范围

CAS 的“读版本、比较、写新版本”必须在同一事务中完成。否则 A 和 B 可能同时检查通过，然后先后覆盖，版本号就成了摆设。参考实现先执行 `BEGIN IMMEDIATE`，再查询版本、判断、插入快照，最后提交；异常时回滚。

SQLite 同时只允许一个写事务，其他写入需要等待或得到忙错误。由数据库把这段操作串行化，才保证两个连接不会同时用同一个旧版本成功更新。这适合本地教学与低并发存储，不意味着可以直接当作高并发分布式调度器。详见 [SQLite 事务说明](https://www.sqlite.org/lang_transaction.html)与[隔离说明](https://www.sqlite.org/isolation.html)。

但事务只保护参加它的数据库操作。假设下一步是把升级报告发给外部系统：发送成功后，保存状态前进程退出。重启看到“待发送”，再次发送就会重复。回滚 SQLite 无法撤回外部系统已经收到的报告。此时需要稳定的操作标识、外部服务的幂等支持，或查询是否已经发送；不能仅凭 checkpoint 宣称每个动作恰好执行一次。

另外，SQLite 的 WAL checkpoint 指的是把预写日志内容合并到数据库文件，属于数据库维护机制；本篇 checkpoint 指 Agent 状态快照，两者不要混为一谈。

## 恢复后先核验什么

加载到一份 JSON，只完成了恢复的第一步。程序还要确认这个任务是否仍有效、状态结构是否与当前代码兼容、产物是否存在且内容匹配、预算和授权是否仍然有效。保存时允许的操作，今天未必仍被允许。

再看未完成步骤。如果状态指向 `verify_report`，且报告内容匹配，就可以重新验收；如果报告丢失，应回到能重新生成它的步骤。如果状态指向一次可能已经完成的外部操作，应先核对结果，再决定是否重试。恢复的是与当前现实相符的工作进度，不能盲目照着旧计划执行。

完整恢复通常还要保存模型与代码版本、输入快照、计划、必要的消息和待执行操作。哪些内容必须精确保存，取决于从哪里继续。本库存储类只接受 JSON 对象并保存版本，**不自动检查这些业务条件，也不提供跨 schema 版本迁移**。这些检查需要运行时实现，继续看[持久运行与故障恢复](../../09-runtime-harness-environment/README.md)。

## 实际运行：看见保存成功，也看见旧写入失败

从仓库根目录运行：

```bash
PYTHONPATH=10-Knowledge/_archive/07-state-and-memory/05-code/state-memory-python/src \
python -m unittest discover \
-s 10-Knowledge/_archive/07-state-and-memory/05-code/state-memory-python/tests -v
```

四项组合测试应通过，其中 `test_checkpoint_resume_and_conflict` 用两个独立连接读取同一个临时数据库，确认新连接能读回已提交快照，旧版本写入会被拒绝，正确版本可以继续保存。测试数据库会随测试清理，不会生成研究报告。需要逐步观察时打开 [State / Memory Notebook](../04-labs/01-state-memory-and-conflicts.ipynb)；需要留下可检查文件时运行上面的示例，检查 `.runs/pine-state.db` 并用 `load("pine-17")` 读取。

对照 [Mini Agent 的 runtime.py](../../../../20-Projects/00-mini-agent/mini_agent/runtime.py)：它会保存 `run.json`、`messages.json`、`trace.jsonl` 和报告，但启动时要求使用新输出目录，没有读取旧目录继续循环的入口。**有运行记录，不等于已经实现断点恢复。** 这不是测试失败，而是实现范围。

## 两个练习

**练习 1：** 把 B 的失败处理改成“重新读取最新版本，再重新计算剩余预算”，最终状态应该是什么？参考：若这次扣减仍然有效，应是 `step=4, calls_left=7`。关键是以最新状态为基础合并，而不是继续写回 B 的整个旧副本；多方同时消耗预算时，还要记录每次消耗对应的操作，避免重复扣减。

**练习 2：** checkpoint 显示“报告已生成，待验收”，文件却已经被人工修改。能否直接把任务标为完成？参考：不能。先比较产物内容与保存的引用，发现变化后，要么重新验收当前版本并建立新记录，要么找回原版本。路径相同并不能证明产物相同。

下一篇：[Memory 生命周期](02-memory-lifecycle.md)。返回[Agent 核心组件总览](../../03-agent-core/01-concepts/04-core-components.md)，把当前任务的状态与跨任务记忆分开理解。
