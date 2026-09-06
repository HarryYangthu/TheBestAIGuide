# Runtime 与 Harness：让一个动作有开始、有结果、能追查

> 状态：draft；来源核验：2026-09-06；本地恢复与幂等实验已实跑，生产能力不在验证范围内。


模型输出 `charge(amount=10)` 只是提出一个动作。到底是谁调用接口、重复请求会怎样、进程崩溃后要不要重来，都不由这段文本自动解决。Runtime 是实际安排这些动作执行的程序；本库把包围一次 Agent 运行的权限、预算、记录、验证和环境管理统一称作 Harness。这是本库采用的工程分工，不是一个所有框架都遵循的标准 API。

## 把几个运行对象分清

| 对象 | 回答的问题 | 例子 |
|---|---|---|
| Run | 用户要求完成哪一次任务 | `run-42`：提交本次实验报告 |
| Step | 逻辑上要完成哪一个动作 | `upload-report` |
| Attempt | 同一步第几次尝试 | 网络超时后第 2 次上传 |
| Event | 已经发生了什么 | `prepared`、`attempt`、`completed` |
| State / Checkpoint | 现在确认到哪一步 | 上传完成，回执为 object-7 |
| Artifact | 交付或中间产生了什么 | 报告文件及其内容哈希 |

这几个对象不能互相代替。日志说“准备上传”不证明文件已上传；模型说“成功”不是服务端回执；再次运行同一个 Step 也不是新的业务请求。可靠运行首先依赖这些对象的身份一致。

## 一次工具动作实际经过什么

动作先做输入校验，再检查权限和预算，然后记录逻辑步骤，执行外部调用，验证回执，最后提交完成状态。权限校验必须发生在动作真正执行前；完成记录必须与可信工具结果对应。失败时应保留错误类别，不能把所有异常转成一句“请重试”。

```python
saved = store.prepare(run_id, step_id, amount)
if saved["status"] == "completed":
    return saved["result"]
receipt = ledger.charge(operation_key(run_id, step_id), amount)
store.finish(run_id, step_id, receipt)
return receipt
```

这是[Runner](../05-code/recoverable-runtime-python/src/recoverable_runtime/runner.py)里的关键路径。`prepare` 保留输入与步骤身份，`charge` 使用同一个幂等键，`finish` 将回执和完成事件一起提交。删去任何一项，都可能把一次“连接不可靠”变成一次“业务结果不可靠”。

## Harness 各层应该承担什么

| 层 | 负责 | 不应承担 |
|---|---|---|
| 模型适配器 | 把模型输出转换为动作候选 | 自行授予工具权限 |
| 策略层 | 按真实用户身份检查范围与审批 | 根据模型自述确认身份 |
| 调度层 | 并发、队列、预算、取消 | 用最终回答掩盖超时任务 |
| 工具层 | 校验参数、执行动作、返回类型化结果 | 任意吞掉异常 |
| 持久化层 | 事件、Checkpoint、回执、恢复 | 把未确认结果当已提交事实 |
| 验证层 | 检查产物与任务目标是否匹配 | 仅凭工具“200 OK”认定用户目标达成 |

例如上传接口返回成功，只证明上传动作成功，还要检查报告是否包含所有必需实验、引用是否有效。运行成功与任务正确是两个验收层次。

## 什么时候需要拆出独立 Runtime

短脚本在一个进程内完成，可以先用函数调用加明确错误处理。任务持续几小时、跨用户、需要恢复或带外部副作用时，运行生命周期应成为独立模块，否则业务逻辑里会散落重试、超时和日志代码，很难统一验证。

本域实现只负责本地单写者恢复语义；权限由[安全实验](../../11-safety-security-governance/05-code/README.md)演示，并发由[多 Worker 工程](../../08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/README.md)演示。独立接口便于学习，不意味着把三段代码放在一起就已经是生产平台。

参考[来源索引](../references.md)，继续读[持久执行](02-durable-execution.md)。
