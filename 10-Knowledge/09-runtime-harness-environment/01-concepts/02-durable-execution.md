# 持久执行：恢复时究竟要重做什么

> 状态：draft。配套代码是单写者、本地 SQLite 教学实验；不包含分布式调度或通用工具恢复。下文的“扣 10”只是修改本地整数账本，不涉及真实资金。

Agent 花了半小时查资料、写代码，进程突然退出。重启后，你希望它从上次做到的地方继续。但“继续”有两种完全不同的情况：文件还没读，可以再读一次；表单已经提交，只是成功回执没收到，再点一次可能产生第二份订单。保存聊天记录只能告诉我们 Agent 说过什么，不能回答外部动作究竟完成没有。

先用一个比 SDK 调研更小的例子看清问题：任务 `run-1` 有一步 `charge`，要求本地模拟账本增加 10。正常结束时应当有一条记录，净值为 10。下面故意把运行记录与账本放进两个独立数据库，让“外部已经做完，本地还没记住”的故障真正出现。

## 三个崩溃位置，恢复策略为什么不同

一次执行实际经过三个阶段：

1. **prepare**：在 `events.sqlite` 写入任务、步骤、参数 10，状态记为 `pending`。
2. **外部动作**：调用账本，在 `ledger.sqlite` 中写入一条增加 10 的记录。
3. **finish**：拿到回执后，在 `events.sqlite` 把步骤改为 `completed`，同时保存回执。

`pending` 只表示“尚未保存完成回执”。它没有说外部动作没发生。用下表逐项核对，差别就很清楚了。

没有故障时，本地事件依次为 `prepared → attempt → completed`，账本从 0 变为 10。任务再调用同一步时，程序在 prepare 之后发现已完成，直接返回回执，不再新增 attempt。这是正常路径；故障路径则要解释为什么某些步骤只留下前两个事件。

| 崩溃位置 | 重启后本地状态 | 账本记录数／净值 | 恢复后怎样得到正确结果 |
| --- | --- | --- | --- |
| prepare 后，外部动作前 | pending | 0／0 | 按原动作身份执行，增加一条记录，得到 10 |
| 外部动作后，finish 前 | pending | 1／10 | 按原动作身份查询或重试，拿回原回执，仍是 1／10 |
| finish 后，向调用者返回前 | completed | 1／10 | 直接返回已保存回执，不再调用账本 |

第二行最容易写错。如果恢复程序看到 `pending` 就认定上次失败，再用一个新身份调用，账本会增加第二条记录，净值变成 20。网络超时也有同样问题：请求可能没送到，也可能已执行，只是响应丢了。**“没收到结果”是一种未知状态，不能直接写成“动作失败”。**

## 恢复需要固定哪些身份

这里要区分一次**逻辑动作（operation）**与一次**调用尝试（attempt）**。`run-1 / charge / 增加10` 是同一个动作；第一次调用断线，第二次重试，是它的两个 attempt。attempt 可以换编号，operation 的身份和参数必须保持不变。

配套代码用 `operation_key(run_id, step_id)` 生成幂等键。幂等的意思是：相同动作重复请求，效果不继续累加。账本以这个键为唯一键；第一次插入记录，后续同键、同参数请求返回原结果。若同键的金额变成 11，则拒绝调用，因为这已经不是同一个意图。

也不能简单拿参数哈希代替动作身份：用户可能确实要求做两次各增加 10 的动作。这时参数相同，两个 operation 应有不同的 `step_id`。本库将 `[run_id, step_id]` 序列化为 JSON，避免字符串拼接产生歧义；比如 `("a:b", "c")` 与 `("a", "b:c")` 不应撞键。

真实任务还应固定输入文件版本、工具版本和参数摘要。恢复期间如果工具升级后改变了参数含义，需要迁移旧状态，或明确开启新任务。请求身份、重复参数与副作用的关系，可对照 [AWS 的幂等 API 设计说明](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)。

## 代码如何把窗口保留下来

进入[配套工程](../05-code/recoverable-runtime-python/README.md)，下面代码可在设置 `PYTHONPATH=src` 后的 Python 环境运行。它专门复现第二个窗口；使用临时目录，不会碰业务数据。

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from recoverable_runtime import EventStore, LocalLedger, Runner, InjectedCrash

with TemporaryDirectory() as directory:
    root = Path(directory)
    store = EventStore(root / "events.sqlite")
    ledger = LocalLedger(root / "ledger.sqlite")
    runner = Runner(store, ledger)
    try:
        runner.execute("run-1", "charge", 10, crash_at="after_effect")
    except InjectedCrash:
        print(runner.replay("run-1")["charge"]["status"], ledger.snapshot()["net"])
    store.close()
    ledger.close()
    store = EventStore(root / "events.sqlite")
    ledger = LocalLedger(root / "ledger.sqlite")
    runner = Runner(store, ledger)
    runner.execute("run-1", "charge", 10)
    print(runner.replay("run-1")["charge"]["status"], ledger.snapshot()["net"])
    print(ledger.snapshot()["charge_count"])
    store.close()
    ledger.close()
```

依次应看到 `pending 10`、`completed 10`、`1`。第一行证明本地与外部确实可能不一致；第二行证明恢复补上了完成回执；第三行证明恢复没有增加第二次效果。只检查返回值为 10 不够，因为两条重复记录也可能各自返回 10。

为什么它能做到？[LocalLedger.charge](../05-code/recoverable-runtime-python/src/recoverable_runtime/recovery.py)把“记录幂等键”和“记录金额”放在同一个账本事务中。如果先改金额、再另开事务记键，中间崩溃仍可能重复执行。[EventStore.finish](../05-code/recoverable-runtime-python/src/recoverable_runtime/events.py)也把本地完成状态和完成事件放在同一事务。两个库之间仍没有共同事务；未知窗口依然存在，只是恢复时有办法处理。

因此，这不是对任意工具的 exactly-once 承诺。实际成立的条件是：服务端支持可靠去重，动作身份稳定，而且重复请求的参数一致。外部服务不支持幂等或结果查询时，Runtime 单靠本地数据库无法消除未知状态；应保留待核对状态，交给相应业务流程处理。

## Checkpoint、Resume、Replay 各做什么

**Checkpoint 是保存下来的进度**，包括状态、参数与已确认回执。**Resume 是读进度后继续执行**：完成的返回回执，未确认的按恢复策略处理。**Replay 是读历史事件重新算状态**，常用于检查或重建状态视图。

本库的 `replay(events)` 只遍历 `prepared / completed / compensated` 事件，不接收账本对象，也不调用工具。因此，在 `after_effect` 崩溃后，Replay 仍得到 `pending`：历史里尚未出现完成事件，它无权猜测外部账本。此时调用 `execute` 才是在恢复动作，两者不能混用。事件顺序使用数据库序号，避免依赖多台机器的时钟恰好一致。

## 重试、取消和补偿并不是一件事

重试的目标是让原动作完成。参数校验错误通常需要修参数，不该原样反复调用；短暂连接失败可以在次数和时间预算内退避重试；结果未知的写操作，先确认它的幂等与查询契约。教学 Runner 没有自动重试队列，第二次 `execute` 是调用者主动发起的恢复。

取消的目标是停止后续推进，却不能保证已送出的请求没生效。特别是在第二个窗口，用户按了取消，账本中的 10 仍然存在。补偿则是一个新的业务动作，比如再记一条退款；它不抹去原扣款历史，也未必能完全逆转所有现实效果。

本库 `compensate` 只接受已确认完成的步骤，拒绝 `pending`。不要为了取消而先调 `execute`：如果原请求其实还没发生，这会主动把它做完。生产系统需要单独的取消状态与只读对账能力；本实验没有提供通用取消接口。进一步看[重试、幂等与补偿](../02-patterns/01-retry-idempotency-compensation.md)。

## 运行后，具体检查什么

从仓库根目录运行：

```bash
cd 10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python
PYTHONPATH=src python -m unittest discover -s tests -v
```

PowerShell 先执行 `$env:PYTHONPATH="src"`，再运行 `python -m unittest discover -s tests -v`。测试覆盖三个故障窗口、输入变更拒绝、无副作用回放、重复补偿等；预期 7 项通过。各测试使用临时数据库，不生成长期报告。想逐步查看保存的输出，打开[恢复与幂等 Notebook](../04-labs/01-recovery-and-idempotency.ipynb)。

## 检查自己是否理解

**练习一：** 把上面代码的恢复调用改成 `runner.execute("run-2", "charge", 10)`，预测账本净值。参考解释：变为 20、两条记录。新 `run_id` 代表新动作，去重机制没有失效，是调用者给错了身份。

**练习二：** 在 `after_effect` 崩溃后连续调用三次 `replay`，本地会变成 completed 吗？参考解释：不会；回放只能重建已记录事实，账本仍为 10，本地仍为 pending。需要恢复执行或具备明确契约的对账操作，才能把未知结果转为已确认结果。

回到 [Agent 核心组件总览](../../03-agent-core/01-concepts/04-core-components.md)：状态管理负责记住进度，持久执行还必须回答“恢复后哪些动作能再做”。这正是两者之间多出来的工作。
