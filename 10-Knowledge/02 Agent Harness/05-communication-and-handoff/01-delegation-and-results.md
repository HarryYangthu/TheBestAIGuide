# 01｜任务委派与消息协议

[阅读路线](README.md) · [下一篇：02｜消息重试与结果合并](02-retries-and-late-messages.md)

本章总览图如下：

```mermaid
flowchart TD
    O["任务与指定笔记内容快照"] --> D["建立委派请求"]
    D --> Q["JSON 进入执行者队列"]
    Q --> S["started 开始通知"]
    S --> W["读取笔记内容并计算缺口"]
    W --> R["result 结果回执"]
    S --> V["关联请求并更新状态"]
    R --> V
    V --> C["协调者保存有效结果"]
```

## 1. 函数委派

协调者需要一份笔记摘要，把“读取笔记并检查必要事实”交给读取者。`fixtures/notes.txt` 中有工具接入、循环日志两条记录；任务还要求错误重试的说明，因此缺少一条。

下面是完整可运行片段。在本章目录执行，输入为真实笔记，输出三个计数，不写文件：

```python
from pathlib import Path
text = Path("fixtures/notes.txt").read_text(encoding="utf-8")
required = ["工具接入", "循环日志", "错误重试"]
found = sum(fact in text for fact in required)
print(f"required={len(required)} found={found} missing={len(required) - found}")
```

标准输出：

```text
required=3 found=2 missing=1
```

[check_notes](code/v1_delegate.py) 将这一步封装成函数：读取请求指定的笔记，返回 `path`、`required`、`found`、`missing` 和 `evidence`。证据包含文本、文件名和快照版本，接收方能够重新读取并核对。

运行完整入口：

```bash
python code/v1_delegate.py
```

标准输出：

```text
path=notes.txt required=3 found=2 missing=1
owner=coordinator
artifacts=runs/v1
```

打开 `runs/v1/result.json` 核对两条原文。读取者完成读取，协调者仍负责后续如何写报告；这就是本章的委派。

## 2. 消息协议

如果有两个执行者、多个任务或重试，调用方不能靠“刚收到一段文字”判断它属于哪个任务。本文消息字典把身份、收发地址和正文分开。下面是正常运行 v2 时第一条请求的结构示例；它是 JSON 数据，不是独立可执行脚本：

```json
{
  "protocol": 1,
  "message_id": "request-001",
  "case_id": "report-017",
  "task_id": "read-notes",
  "correlation_id": "request-001",
  "attempt": 1,
  "input_version": "notes-2",
  "epoch": 1,
  "from": "coordinator",
  "to": "notes-reader",
  "kind": "delegate",
  "payload": {
    "task": {
      "case_id": "report-017",
      "path": "notes.txt",
      "required_facts": [
        "工具接入",
        "循环日志",
        "错误重试"
      ],
      "instruction": "读取笔记，列出已完成的工作和缺少的说明，保存报告。"
    },
    "snapshot_file": "snapshot-ready.json",
    "return_fields": [
      "path",
      "required",
      "found",
      "missing",
      "evidence"
    ]
  }
}
```

| 字段 | 类型 | 用来回答什么 |
|---|---|---|
| `message_id` | 字符串 | 是不是同一条消息的再次投递 |
| `case_id` | 字符串 | 属于哪张任务的整件工作 |
| `task_id` | 字符串 | 受托完成哪项逻辑任务 |
| `correlation_id` | 字符串 | 对应哪一次委派请求；本例等于请求的 message_id |
| `attempt` | 正整数 | 该逻辑任务第几次真正执行 |
| `input_version` | 字符串 | 结果基于哪份输入快照 |
| `epoch` | 正整数 | 委派时整体负责人处于哪一任期 |
| `from`、`to` | 字符串 | 发件者和收件者 |
| `kind` | 字符串 | delegate、started、result 或 failure |
| `payload` | 字典 | 请求参数、结果或结构化失败 |
| `protocol` | 整数 1 | 本文消息结构的版本 |

这些是本文任务程序实际使用的字段，不是供应商 API 格式。每个 ID 只有一种主要职责：`task_id` 跨重试不变，`correlation_id` 随新执行请求变化，回复自己的 `message_id` 则与请求不同。不要拿模型工具调用的 `tool_call_id` 直接充当整个任务 ID。

## 3. JSON 序列化与队列

[protocol.py](code/protocol.py) 中的 `LocalBus` 为每个参与者保存一个 `asyncio.Queue`。下面是 `send` 和 `receive` 的方法节选，依赖 `self.queues/self.wire`、`canonical` 和 `json`，定义本身不打印：

```python
async def send(self, message):
    encoded = canonical(message)
    self.wire.append(json.loads(encoded))
    await self.queues[message["to"]].put(encoded)

async def receive(self, recipient):
    encoded = await self.queues[recipient].get()
    self.queues[recipient].task_done()
    return json.loads(encoded)
```

`canonical` 使用固定键顺序将字典序列化成 JSON 字符串。接收方用 `json.loads` 建立新的字典，不会与发送者共享原来的嵌套对象。`messages.jsonl` 保存实际传过的消息，便于查关联。

这里的 `task_done` 表示队列项已经交到调用者手中，**不代表笔记内容检查已经完成**。业务状态只由后面的 `started/result/failure` 处理器改变。本章不使用 `Queue.join()` 判断任务是否完成。

## 4. 进度通知与结果回执

笔记内容执行者先发 `started`，读取指定文件后才发结果。`Case.response` 从原请求复制关联字段，交换收发地址，并创建新的消息 ID。以下是其中返回对象的等价节选，依赖 `request/kind/payload` 和 `self.new_id`，没有标准输出：

```python
return {"protocol": 1, "message_id": self.new_id("message"),
        "case_id": request["case_id"], "task_id": request["task_id"],
        "correlation_id": request["correlation_id"], "attempt": request["attempt"],
        "input_version": request["input_version"], "epoch": request["epoch"],
        "from": request["to"], "to": request["from"], "kind": kind,
        "payload": deepcopy(payload)}
```

| 正常路径上的消息 | 接收后状态 | 是否可汇总 |
|---|---|---|
| `delegate` | `pending` | 否，尚未执行 |
| `started` | `running` | 否，仅证明开始 |
| `result` 且证据通过 | `completed` | 是 |

接收结果时，程序不仅看 `kind=result`，还读取请求指定的笔记内容文件，重新构造期望结果，再与回执比较。要求的事实、找到的数量、缺失数量、证据版本和文件路径都必须一致。这种领域检查在本例很短；复杂任务可以返回文件、行号、测试结果，再由相应验收器检查。

在本章目录运行完整入口，读取同一组正常输入：

```bash
python code/v2_messages.py
```

准确标准输出：

```text
decisions=accepted_started,accepted_result
complete=True owner=coordinator epoch=1
artifacts=runs/v2
```

打开 `messages.jsonl`：请求是 `request-001`，开始与结果通知是不同的消息 ID，但都关联 `request-001`。再打开 `result.json`：有效结果只有 `read-notes` 一份，负责人仍是协调者。

[下一篇：02｜消息重试与结果合并](02-retries-and-late-messages.md)
