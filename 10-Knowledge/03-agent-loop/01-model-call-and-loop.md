# 01｜从一次模型调用到最小 Agent 循环

> 状态：draft

[阅读路线](README.md) · 下一篇：[02｜为执行循环接入工具](02-tools-and-observations.md)

先看我们要完成的过程：程序把任务交给模型，执行模型提出的读取请求，再把文件内容交回模型。下面各节会从一次普通调用开始，逐步写出这张图。

```mermaid
flowchart TD
    A["1 配置客户端并输入 prompt"] --> B["2 模型生成 response"]
    B --> C{"3 响应包含工具请求吗"}
    C -->|是| D["4 读取 notes.txt"]
    D --> E["5 请求和 observation 写入历史"]
    E --> B
    C -->|否| F["6 保存回答与运行记录"]
```

**本篇输入：** 根目录的 [notes.txt](notes.txt)。

**运行入口：** `code/v0_model_call.py`、`code/v1_minimal_loop.py`。

**输出位置：** `runs/v0-…/`、`runs/v1-…/`。

## 1. 配置客户端后就可以发起第一次模型调用

按 [README 的配置步骤](README.md) 安装依赖并填写 `.env`：

```dotenv
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=你的实际密钥
OPENAI_MODEL=你的模型名
```

URL 是基础地址，例如 `https://api.openai.com/v1`；SDK 会补上接口路径。下面的完整片段可以在章节目录的 Python 中执行：

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env")
client = OpenAI(
    base_url=os.environ["OPENAI_BASE_URL"],
    api_key=os.environ["OPENAI_API_KEY"],
    timeout=30.0,
    max_retries=0,
)
messages = [{"role": "user", "content": "用一句话解释算术平均值。"}]
response = client.chat.completions.create(
    model=os.environ["OPENAI_MODEL"],
    messages=messages,
)
print(response.choices[0].message.content)
```

**这段代码的作用：** 发起一次真实请求，并打印第一条候选响应的正文。

**参考输出：** `算术平均值是所有数值之和除以数值个数。` 模型措辞可能不同。

| 对象 | 在这段代码中表示什么 |
|---|---|
| prompt | 本次交给模型的输入，包含 `messages` 中的问题 |
| `client` | 配好地址和密钥的 OpenAI 客户端 |
| `response` | API 返回的完整响应对象 |
| `response.choices[0].message` | 第一条候选回答的消息对象 |
| `message.content` | 回答正文 |

配套脚本把同一次调用的输入和响应一起保存。执行：

```bash
python code/v0_model_call.py
```

**输出结构：**

```text
<模型回答>
status=stopped reason=response_received model_calls=1
artifacts=<本次运行目录>
```

打开该目录的 `requests.jsonl`，能看到最初的问题；打开 `responses.jsonl`，能看到完整响应；`answer.md` 保存回答正文。

## 2. 真实文件让模型有了可以读取的外部信息

根目录已经有一份 `notes.txt`，内容是：

```text
本周完成了工具接入与循环日志。
```

先不用模型，直接在章节目录运行下面的完整代码：

```python
from pathlib import Path

text = Path("notes.txt").read_text(encoding="utf-8")
print(text, end="")
```

**标准输出：**

```text
本周完成了工具接入与循环日志。
```

这就是读取工具最终要执行的操作。再运行配套入口：

```bash
python code/inspect_input.py
```

**标准输出：**

```text
本周完成了工具接入与循环日志。
saved=runs/input-preview.txt
```

它还生成 `runs/input-preview.txt`。打开这个文件，应当与 `notes.txt` 完全一致。你可以先修改笔记内容，再运行一次，观察两份文件如何对应。

接下来把任务交给模型：“读取 `notes.txt`，告诉我本周完成了什么。”这一次，模型需要请求程序提供文件内容。

## 3. 工具定义让模型能够提出读取请求

给模型的工具定义描述名称、用途和参数。下面使用 Chat Completions 的函数工具格式，代码可接在第 1 节的客户端初始化之后：

```python
tools = [{
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "读取当前运行目录中的文本文件",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
}]
messages = [{"role": "user", "content": "读取 notes.txt，告诉我本周完成了什么。"}]
response = client.chat.completions.create(
    model=os.environ["OPENAI_MODEL"],
    messages=messages,
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "read_file"}},
    parallel_tool_calls=False,
)
message = response.choices[0].message
print(message.model_dump_json(indent=2))
```

**这段代码的作用：** 明确要求本次生成一个 `read_file` 调用，便于观察请求结构。自动循环中由模型自己选择下一步。

**参考输出中的关键部分：**

```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [{
    "id": "call_xxx",
    "type": "function",
    "function": {
      "name": "read_file",
      "arguments": "{\"path\":\"notes.txt\"}"
    }
  }]
}
```

`call_xxx` 由服务生成，实际值会不同。这里还没有文件内容，只有“请读取哪个文件”的请求。[OpenAI 工具调用文档](https://developers.openai.com/api/docs/guides/function-calling)

## 4. 程序解析参数并执行真实的文件读取

`function.arguments` 是一段 JSON **字符串**，需要用 `json.loads` 转成 Python 字典，才能取出 `path`。以下代码接在上一段之后：

```python
import json
from pathlib import Path

call = message.tool_calls[0]
arguments = json.loads(call.function.arguments)
root = Path.cwd().resolve()
path = (root / arguments["path"]).resolve()
if not path.is_relative_to(root):
    raise ValueError("文件必须在当前目录内。")
observation = path.read_text(encoding="utf-8")

print(type(call.function.arguments).__name__)
print(type(arguments).__name__)
print(observation, end="")
```

**标准输出：**

```text
str
dict
本周完成了工具接入与循环日志。
```

| 变量 | 类型 | 示例值 |
|---|---|---|
| `call.function.arguments` | `str` | `'{"path":"notes.txt"}'`，外层是字符串 |
| `arguments` | `dict` | `{"path": "notes.txt"}` |
| `observation` | `str` | 文件中真实读取到的文本 |

observation 就是操作后的观察结果。本例是文本，执行测试时可以换成检查结果，查询数据库时可以换成记录。

## 5. 请求和观察结果一起进入下一次模型输入

模型生成的请求与程序执行的结果，需要一起保留：

```python
# 接续上一段；只提取本次对话需要的 API 消息字段。
messages.append({
    "role": "assistant",
    "content": message.content,
    "tool_calls": [c.model_dump() for c in message.tool_calls],
})
messages.append({
    "role": "tool",
    "tool_call_id": call.id,
    "content": observation,
})
print([item["role"] for item in messages])

response = client.chat.completions.create(
    model=os.environ["OPENAI_MODEL"],
    messages=messages,
    tools=tools,
    tool_choice="none",
)
print(response.choices[0].message.content)
```

**标准输出的第一行：**

```text
['user', 'assistant', 'tool']
```

**第二行参考输出：** `本周完成了工具接入与循环日志。`

第二次调用通过 `tool_choice="none"` 要求模型直接回答。这样我们手动走完了总览图里的一个完整往返。

| 顺序 | 消息角色 | 保存的信息 |
|---:|---|---|
| 0 | `user` | 用户希望读取笔记并总结 |
| 1 | `assistant` | 模型请求 `read_file`，带调用 ID |
| 2 | `tool` | 对应 ID 的真实读取结果 |

```mermaid
sequenceDiagram
    participant P as 程序
    participant M as 模型
    participant F as 文件工具
    P->>M: 任务和工具定义
    M-->>P: read_file 请求
    P->>F: 按 path 读取
    F-->>P: observation
    Note over P: 保存请求与结果
    P->>M: 更新后的 messages
    M-->>P: 根据内容回答
```

配套命令也可以运行两次调用的过程：

```bash
python code/v1_minimal_loop.py --manual
```

成功时，控制台显示 `reason=manual_two_calls`。此入口同样为两次请求配置了工具选择规则；打开 `requests.jsonl` 的第 2 行，应能找到文件内容。

## 6. 本文用一个响应字典连接 API 与执行循环

随着代码变长，我们把 SDK 字段读取集中到 `openai_model.py`。本文循环中的 `response` 是一个 Python 字典：

```python
{
    "content": None,
    "tool_calls": [{
        "id": "call_xxx",
        "name": "read_file",
        "arguments": {"path": "notes.txt"},
    }],
}
```

它只保留循环需要的正文、调用 ID、工具名和已解析参数。转换关系如下：

| API 消息中的字段 | 本文响应字典中的字段 | 转换操作 |
|---|---|---|
| `message.content` | `response["content"]` | 保留正文 |
| `call.id` | `call["id"]` | 保留关联编号 |
| `call.function.name` | `call["name"]` | 提取工具名 |
| `call.function.arguments` | `call["arguments"]` | `json.loads`：字符串转字典 |

对应函数如下。它是函数定义，执行定义本身没有控制台输出；调用后的返回值就是上面的字典结构。

```python
def normalize_message(message):
    return {
        "content": message.content,
        "tool_calls": [
            {
                "id": call.id,
                "name": call.function.name,
                "arguments": json.loads(call.function.arguments),
            }
            for call in (message.tool_calls or [])
            if call.type == "function"
        ],
    }
```

下一次请求 API 时，`api_messages()` 再把工具名放回 `function.name`，用 `json.dumps` 把参数转回 JSON 字符串。`requests.jsonl` 保存发给 API 的格式，`messages.json` 保存本文循环使用的格式，可并排打开比较。

## 7. 一个循环可以替代不断增加的手动调用

手动版本只处理一次工具调用。如果模型还要继续操作，就需要重复“请求模型 → 执行工具 → 追加结果”。下面是 `v1_minimal_loop.py` 的核心函数，所需导入和工具定义在同一文件中：

```python
def run_loop(model, workspace, max_steps=10):
    messages = initial_messages(TASK)
    for _ in range(max_steps):
        response = model(messages, TOOLS)
        add_assistant(messages, response)
        if not response["tool_calls"]:
            return messages
        for call in response["tool_calls"]:
            if call["name"] != "read_file":
                raise ValueError("阶段 1 只支持 read_file。")
            observation = read_file(workspace, call["arguments"]["path"])
            add_observation(messages, call, observation)
    raise RuntimeError("最小示例达到调用上限。")
```

| 代码步骤 | 对应总览图 | 这一步留下什么 |
|---|---|---|
| `model(messages, TOOLS)` | 模型生成响应 | 本轮 response |
| `add_assistant` | 保存模型请求 | assistant 消息 |
| `read_file` | 读取文件 | observation |
| `add_observation` | 结果进入历史 | 带 `tool_call_id` 的 tool 消息 |
| 下一轮 `for` | 再次输入模型 | 更新后的 messages |
| 没有工具请求时返回 | 保存回答 | 完整历史中的最后一条正文 |

定义函数不打印内容。运行入口负责调用它并保存结果：

```bash
python code/v1_minimal_loop.py
```

**输出结构：**

```text
status=stopped reason=no_tool_calls model_calls=<本次调用次数>
artifacts=<本次运行目录>
```

本版把“没有工具请求”作为退出规则，并用调用上限防止无限循环。第三篇会增加明确的结束信号，第四篇再处理空响应等情况。

## 8. 修改输入后可以对照模型看到的内容与最终回答

打开本次目录，按下面顺序查看：

| 文件 | 检查方法 |
|---|---|
| `workspace/notes.txt` | 确认本次运行使用的文件内容 |
| `responses.jsonl` | 找到 `read_file` 请求及其参数 |
| `requests.jsonl` | 找到后续请求中的 tool 消息，核对文件内容 |
| `answer.md` | 看回答是否使用了这份笔记 |
| `report.md` | 查看运行状态、调用次数与回答 |

将根目录 `notes.txt` 改成“本周完成了参数校验，但还没有加入错误重试。”，再运行 v1。比较两个运行目录的输入副本、后续请求和回答。

这时，总览图中的每个节点都有了对应代码与文件。下一篇会在同一条循环里加入写入和检查工具，完成 `stats.py` 的修复任务。

[下一篇：02｜为执行循环接入工具](02-tools-and-observations.md)
