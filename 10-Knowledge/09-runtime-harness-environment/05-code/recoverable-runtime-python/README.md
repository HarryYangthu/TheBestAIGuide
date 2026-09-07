# 可恢复运行时（本地 Python 实验）

> 状态：verified（本地故障窗口、回放与补偿）；最近单元测试：2026-09-07，7 项通过；Notebook 保存输出日期另见实验。

Python 3.11+，无第三方运行依赖。进入本目录：

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Windows PowerShell 先 `$env:PYTHONPATH="src"` 再执行 python 命令。可通过 `python -m pip install -e . --no-build-isolation` 安装，构建环境需已有 setuptools>=68。

```python
from recoverable_runtime import EventStore, LocalLedger, Runner
store = EventStore("events.sqlite")
ledger = LocalLedger("ledger.sqlite")
runner = Runner(store, ledger)
receipt = runner.execute("run-1", "step-1", 10)
assert runner.execute("run-1", "step-1", 10) == receipt
print(runner.replay("run-1"))
print(ledger.snapshot())
store.close()
ledger.close()
```

示例文件由本地生成，仅模拟外部业务效果。运行一次应得到 charge_count=1、net=10；相同 ID 与参数重复执行不新增记录。故障参数为 `crash_at="before_effect"/"after_effect"/"after_checkpoint"`，抛 `InjectedCrash`。恢复时保持同 ID、同参数。

| 文件 | 核心职责 |
|---|---|
| [events.py](src/recoverable_runtime/events.py) | 步骤输入、状态、顺序事件、同事务完成记录 |
| [runner.py](src/recoverable_runtime/runner.py) | 执行、恢复、缓存结果与补偿 |
| [recovery.py](src/recoverable_runtime/recovery.py) | 独立账本的幂等效果、退款与纯事件回放 |
| [tests](tests/test_recovery.py) | 7 项测试，覆盖故障窗口、重复调用与 pending 补偿不产生新效果 |

边界：单写者同步 Runner，不提供分布式租约、跨进程调度或任意工具适配器。持久化使用与 State 域相同的 JSON 状态思路，但为展示“状态与完成事件同事务”而保留独立事件库，无隐式跨域依赖。模拟服务自身支持原子幂等；真实外部服务不支持时，不能宣称同样保证。完整实验见 [Notebook](../../04-labs/01-recovery-and-idempotency.ipynb)，机制见[持久执行](../../01-concepts/02-durable-execution.md)。

`compensate` 只接受已完成的步骤。对 pending 调用 `execute` 会确保原动作执行，可能产生此前尚未发生的效果；再补偿不等于取消。先读[补偿与取消的区别](../../02-patterns/01-retry-idempotency-compensation.md)，不要把本 API 接成通用取消按钮。
