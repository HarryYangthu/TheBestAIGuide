# Agent Loop：每一轮究竟改变了什么

> 状态：draft | 主线源码：[Mini Agent runtime.py](../../../20-Projects/00-mini-agent/mini_agent/runtime.py) | Pine SDK 为虚构教学产品

你可能已经会这样调用模型：传入一个问题，得到一段回答。现在任务变成“比较目录里的两版 SDK 文档，再保存升级清单”。第一次请求时模型还不知道有哪些文件；读取文件后，它又需要根据内容决定下一步。一次请求显然不够。

Agent Loop 就是把“决策、执行、接收结果、再次决策”接起来的循环。这里最值得看懂的不是 `for` 这个语法，而是：**下一次模型请求究竟比上一次多了什么。** 如果工具结果没有进入新请求，循环十次也可能只是在重复问同一个问题。

## 从两条消息开始，第一轮还不知道答案

Mini Agent 的任务是比较 Pine SDK v1 和 v2 正式版，给出认证、超时、重试三项变化，并保存新旧两侧引用。初始 `messages` 只有两项：一条 system 消息规定做事方式，一条 user 消息说明任务。此时 v1 的“30 秒”和 v2 的“10 秒”都不在消息里。

主循环把消息和工具定义交给 `provider.respond(...)`。模型可以请求 `list_files`，但它只是在返回一个调用请求；真正访问目录的是 Python 程序。执行结果是 `preview.md`、`v1.md`、`v2.md`，随后被放入一条 tool 消息。

现在历史从两条变成四条：system、user、assistant 的列目录请求、tool 的目录结果。第二轮模型由此知道了实际文件名。这就是一次行动改变下一次决策的最小例子。

`demo` 模式提前写好了动作顺序，适合观察这个过程；`live` 模式才由真实模型选动作。两者共用同一个循环，不能把演示轨迹顺利执行理解成模型已经学会调查。

## 跟着五轮请求，看消息怎样增长

先看第 1 阶段的完整演示。每次只请求一个工具，前四轮分别列目录、读旧版、读新版、写报告，第五轮返回结束文本。

| 本轮模型调用 | 发送前消息数 | 返回动作 | 工具执行后获得什么 |
| --- | ---: | --- | --- |
| 1 | 2 | `list_files` | 三个实际文件名 |
| 2 | 4 | `read_file("v1.md")` | 旧版原文与行号 |
| 3 | 6 | `read_file("v2.md")` | 新版原文与行号 |
| 4 | 8 | `write_report(...)` | 两个报告文件已写入的回执 |
| 5 | 10 | 普通结束文本 | 没有新工具调用，循环退出 |

例如第 3 轮读完后，消息里已经同时包含两条事实：v1 第 3 行是“超时：默认等待 30 秒。”，v2 第 3 行是“超时：默认等待 10 秒。”。第 4 轮才有足够信息填写 `before="30 秒"`、`after="10 秒"` 和两侧引用。

第 5 轮结束后，完整消息数是 11。它比第 4 轮结束时只多一条 assistant 消息，因为没有工具要执行。这些数字适用于本项目第 1 阶段的固定演示，真实模型可能采用别的合法顺序，也可能一次请求多个工具。

工具结果通常会让输入越来越长。这里的记录存在宿主 Python 列表中，是程序在后续请求里重新发送它们，不是模型调用函数后自动记住了本机文件。第 3 阶段起，`pack` 会从完整历史里选择本次发送的内容，具体见[上下文管理](../../04-context-engineering/README.md)。

## 为什么要同时保存 assistant 请求和 tool 结果

假设模型一轮里请求读取两份文件，两个调用都叫 `read_file`。工具名无法区分“30 秒”属于哪个请求，因此每个调用需要自己的 ID。tool 消息里的 `tool_call_id` 必须回指发起它的调用。

在第 1 阶段，读 v1 的 ID 是 `demo-2`，读 v2 的 ID 是 `demo-3`。如果把结果只写成一句“读取成功，默认超时 10 秒”，又删掉对应的请求，后续模型就失去了这个结果与具体操作之间的关系。消息也可能不再符合服务要求的工具调用格式。[官方函数调用示例](https://developers.openai.com/api/docs/guides/function-calling)使用的也是先追加调用消息，再按调用 ID 追加各自结果。

下面是从真实主循环提炼出的简化版本，保留数据流，省略日志、用量统计和异常处理：

```python
for turn in range(max_steps):
    message, usage = provider.respond(messages, schemas(stage))
    messages.append(message)
    calls = message.get("tool_calls") or []
    if not calls:
        status = "completed"
        break
    if len(calls) > 8:
        raise ValueError("too_many_tool_calls_in_one_turn")
    for call in calls:
        arguments = json.loads(call["function"]["arguments"])
        result = box.call(call["function"]["name"], arguments)
        messages.append({
            "role": "tool", "tool_call_id": call["id"],
            "content": json.dumps({"ok": True, "result": result})
        })
else:
    status = "budget_exhausted"
```

`messages.append(message)` 在执行工具之前，保存“是谁请求了什么”。内层 `for call in calls` 处理全部调用，不能只处理第一项。最后追加的 tool 消息保存真实执行结果，而不是模型对结果的猜测。

这里多个工具按顺序执行。返回多个请求，和程序使用线程并发，是两件事；两者都不自动变成多 Agent。第 6 阶段的 `parallel_read` 才在工具内部并发读文件，子 Agent 另有独立实验。

## 一次工具失败，怎样进入下一次决策

第 2 阶段故意请求不存在的 `release-notes.md`。Python 抛出 `FileNotFoundError`，运行时捕获它，把结果整理成 `ok=false`、`error="FileNotFoundError"` 和简短错误详情，然后仍然追加到消息列表。

下一轮因此能看到两件事：目录里已有 v1/v2，刚才尝试的文件不存在。真实模型可以改用已知文件名，演示驱动也按这个轨迹继续。错误是新信息，不必立即变成整个任务的终点。

但不是所有异常都在同一处处理。第 1 阶段尚未启用这类工具错误反馈，遇到它会停止；第 2 阶段起才允许上述恢复。模型 API 调用本身出错，则没有新的有效决策，外层异常处理记录 `status="error"`。不能把“工具读取失败”和“根本没连上模型”混为一种情况。

仓库的另一个[最小 Loop](../05-code/agent-loop-python/src/agent_loop/loop.py)使用 `Action` 和 `AgentState` 表达相同过程：模型返回动作，工具结果进入 `state.observations`，下一轮再读取这些观察。它一次只有一个动作，也没有 Mini Agent 这套聊天消息格式。理解共同的数据流以后，再比较接口会容易得多。

## 终止必须是代码里的条件

本项目把“不再返回工具调用”当作正常结束信号，于是设置 `completed`。但模型也可能第一轮就说“已完成”，连文件都没读。循环正常结束与任务完成，是两个不同判断；后者由循环外的验收器检查报告。

第 1 阶段还提供了一个更微妙的例子。把 `max_steps` 设成 4，第四轮已经写出正确报告，却没有剩余轮数接收第五轮结束文本。Python 的 `for ... else` 因为未执行 `break`，记录 `budget_exhausted`。当前验收规则要求状态为 `completed`，所以这次验收仍失败。报告存在，可以保留作诊断，但不满足本项目事先约定的完整执行条件。

实际系统若允许“预算耗尽但产物已独立验收”的完成方式，需要明确新增这样的状态和验收规则，不能只把失败标签改成成功。另一种停止原因是程序错误，它也不能伪装成模型主动结束。

一直重复同一动作怎么办？最小 `agent_loop` 实现有重复检测：本次运行中，相同动作、参数和结果累计达到默认两次，就记为 `stopped/no_progress`。换一个调用 ID 不算新进展。Mini Agent 没有此项检测，只受轮数等约束；不要把两个实现的功能混在一起。

## 预算怎样估算

一轮模型调用可能提出多个工具动作，所以模型轮数、工具调用数、时间、token 用量并不相同。Mini Agent 的 `max_steps` 限制模型调用轮数，每轮工具调用另外最多 8 个；它没有实现按金额停止。

模型输入会带上历史，后面的调用往往比前面的更长。假设两轮输入分别为 1000、1800 token，输出分别为 100、200 token。若教学单价是每百万输入 1 元、每百万输出 4 元，工具费用合计 0.02 元，那么总费用是：

$$C=(1000+1800)/10^6+(100+200)\times4/10^6+0.02=0.024\text{ 元}.$$

这些是便于计算的假定数字，不是服务报价。例子要说明的是：限制轮数可以防止无限循环，却不能单独限制费用。费用控制还要知道每次请求的输入量、输出上限和工具开销；调用后的 usage 用来核对已经发生的用量，缺失时不能当成零。详见[模型适配器](03-model-adapters.md)。

## 追踪什么，不追踪什么

从仓库根目录运行下面三次独立实验。输出目录必须尚不存在：

```bash
python 20-Projects/00-mini-agent/run.py run --stage 1 --mode demo --output .runs/loop-normal
python 20-Projects/00-mini-agent/run.py run --stage 2 --mode demo --output .runs/loop-recover
python 20-Projects/00-mini-agent/run.py run --stage 1 --mode demo --max-steps 4 --output .runs/loop-budget
```

正常实验应得到 5 次模型调用、4 次工具调用、11 条消息和验收通过。恢复实验应得到 6 次模型调用、5 次工具调用、1 次工具错误，最后仍通过。预算实验应有 4 次模型调用，状态为 `budget_exhausted`，验收失败且进程退出码为 1；这正是该实验的预期结果。

先查看 `run.json` 验证计数，再读 `messages.json` 按 `tool_call_id` 配对请求和结果。`trace.jsonl` 的 `model_request` 则让你看到每一轮实际送给模型的输入。这样才能分清：模型没看到文件、看到了错误文件，还是看到了正确原文却生成错误答案。

无需依赖模型的隐藏思考过程来做这些检查。可观察的请求、工具返回、报告和验收结果已经能回答很多问题。当前 Mini Agent 写出事件和状态，但没有自动从这些文件恢复执行；想理解恢复还需阅读[状态与检查点](../../07-state-and-memory/01-concepts/01-state-and-checkpoints.md)。

## 两道练习：预测下一轮会看到什么

**练习一：** 某轮 assistant 同时请求读 v1 和 v2，前一轮已有 4 条消息。如果两个工具都成功，本轮结束后多少条？需要几条 tool 消息？

参考解释：共 7 条，新增一条包含两个调用的 assistant 消息，以及两条各自带调用 ID 的 tool 消息。模型调用只增加 1 次，工具调用增加 2 次。不要把每个工具结果单独记成一次模型调用。

**练习二：** 报告存在、格式正确，模型也已返回结束文本，为什么还可能验收失败？到哪里找原因？

参考解释：可能漏了 `retry`，可能把预览稿的“5 秒”当新版值，也可能引用行号与原文不匹配。查看 `acceptance.json` 定位失败项，再顺着 `messages.json` 看证据何时进入上下文。`completed` 只表示循环采用了正常结束路径，不能替报告内容作判断。

返回[核心组件入口](04-core-components.md)，继续理解循环周围的上下文、状态和验收。
