# 模型适配器：一次请求怎样变成下一步动作

> 状态：draft | 配套源码：[Mini Agent providers.py](../../../20-Projects/00-mini-agent/mini_agent/providers.py) | Pine SDK 为虚构教学产品；API 文档核对：2026-09-17

你已经写好 `read_file(path)`，也把“可以读取文件”写进提示词。模型回复：“我接下来读取 v2.md。”文件却没有被打开。缺的不是一句更强硬的提示词，而是把模型输出接到 Python 函数上的程序。

模型适配器负责这条连接的前半段：把程序持有的消息、工具说明和配置发给模型服务，再把返回值转换成主循环看得懂的消息或动作。真正调用 `read_file` 的是运行时。沿着 Pine SDK 升级任务走一遍，就能看清这两部分各自做什么。

## 发出去的到底是什么

第一次请求时，Mini Agent 有两条消息。`system` 消息说明如何使用证据和工具；`user` 消息要求比较 Pine SDK v1/v2，交付三项带出处的变化。除此以外，还要发送工具定义：工具名称、用途和参数格式。

服务端看到的是 `read_file` 的说明以及 `path` 等参数定义，不是本机的 Python 函数体，也不会自动看到资料目录。想让模型知道 `v2.md` 第 3 行写了什么，必须先由程序执行读取，再把结果放进后续请求。

模型配置回答另外三个问题：请求发给哪里，用哪个模型，以什么身份访问。项目分别从 `MINI_AGENT_BASE_URL`、`MINI_AGENT_MODEL`、`MINI_AGENT_API_KEY` 读取这些值。基础地址后面追加 `/chat/completions`；密钥放在认证请求头中，不放进对话内容。

## 顺着真实代码走完一次调用

下面截取 [LiveModel.respond](../../../20-Projects/00-mini-agent/mini_agent/providers.py) 的关键行；省略的异常处理在后文说明：

```python
payload = json.dumps({"model": self.model, "messages": messages,
                      "tools": tools, "temperature": 0}).encode()
request = urllib.request.Request(
    self.base + "/chat/completions", data=payload,
    headers={"Authorization": "Bearer " + self.key,
             "Content-Type": "application/json"})
with urllib.request.urlopen(request, timeout=60) as response:
    data = json.load(response)
message = data["choices"][0]["message"]
return {
    "role": "assistant", "content": message.get("content"),
    **({"tool_calls": message["tool_calls"]} if message.get("tool_calls") else {})
}, data.get("usage", {})
```

第一行把 Python 字典变成 JSON 文本，再编码为网络传输的字节。`tools` 与 `messages` 同时发送，所以模型在这次决策时知道有哪些操作可选。`timeout=60` 为底层网络等待设置超时，它不是整个研究任务的截止时间。

`json.load` 把响应体重新变成字典，`choices[0]` 选取第一个候选回复。本接口按一个候选使用，不是让 Agent 从多个答案里自动投票。最后返回两样东西：主循环要追加的 assistant 消息，以及服务提供的用量数据。

例如回复包含 `tool_calls=[...]`，其中函数名是 `read_file`，`arguments` 是字符串 `'{"path":"v2.md"}'`。适配器把这条请求交给主循环；主循环解析参数并执行文件读取。若回复只是普通文本，就没有工具操作。你在聊天框里看见“我会读文件”，并不能证明服务返回了 `tool_calls`。

## 为什么“返回JSON”还不够

假设模型给出 `{"path":7}`。它是合法 JSON，可以被 `json.loads` 解析，但 `path` 不是工具需要的字符串。再看 `{"path":"preview.md"}`：类型正确，文件也存在，但如果最终把预览稿当成正式版，任务仍然做错了。

因此解析、参数检查、结果验收分别发生在不同位置。适配器识别响应格式；运行时和工具确认名称、参数与访问范围；验收器核对最终报告。结构化输出可以减少字段格式错误，不能代替后两项。

还要区别两种看起来相似的 JSON：一种是模型把 JSON 当普通文字写在 `content` 中，另一种是 API 的 `tool_calls` 字段。当前 Mini Agent 只把后者当工具请求。如果模型在普通回复中写了 `{"name":"read_file"}`，主循环不会搜索这段文字并尝试执行它。

同一回复也可能包含两个工具请求，比如分别读 v1 和 v2。Mini Agent 保留整个列表，主循环逐个处理，最多允许 8 个。另一个[最小 Action 接口](../05-code/agent-loop-python/src/agent_loop/models.py)一次只能表达一个动作。把这两种接口连接起来时，必须明确增加动作列表或者拒绝不支持的多调用；只取第一项会悄悄漏掉工作。

## 流式输出为什么不能来一段就执行一段

当前 `LiveModel` 等完整响应返回，没有实现流式读取。要扩展它，先考虑工具参数可能这样到达：第一个片段给出调用编号、名称 `read_file` 和空参数；后续三个片段依次是 `{"path":`、`"v2.md"`、`}`。

第二个片段到达时，参数还不是完整 JSON。即使某一时刻凑巧能解析，也不能据此判断整条调用已经结束。正确做法是先收集，确认本次调用完整结束，再解析和检查。

若同一回复有多个工具调用，它们的片段还可能交错。需要按调用的 `index` 分别累加：`buffers[0]` 装 v1 的参数，`buffers[1]` 装 v2 的参数。不能把所有 `arguments` 拼成一个大字符串。调用 ID 和名称通常出现在初始片段，后续片段不重复，也不能因为字段缺失就覆盖掉已保存的值。这些字段规则见[官方函数调用的流式说明](https://developers.openai.com/api/docs/guides/function-calling#streaming)。

除了“拼完内容”，还要知道“为什么结束”。正常结束、输出达到长度上限、服务拒绝请求、网络断开，需要分别处理。尤其是 `finish_reason="length"` 时，拿到的参数可能只是前半截；不能为了让程序继续，就猜测并补齐文件名。

这里也有一个实际待补项：当前适配器没有保留 `finish_reason` 和拒绝字段，因此不能完整区分这些情况。阅读现有实现时，应把它理解为非流式兼容接口的教学起点，而不是已经完成全部响应状态处理的通用客户端。

## 同一个失败，在哪一层发生很重要

如果基础地址错误，HTTP 请求可能直接失败，尚未得到模型决策。项目将 HTTP 错误转成只含状态码的异常，将网络错误转成 `model_transport_error`，不把响应体和认证头写进教学轨迹。主循环最终记录 `status="error"`。此时改“请认真读取文档”的提示词没有用，应先修正连接配置。

如果请求成功，但服务返回的 `choices` 为空或形状不符合预期，现有代码也会报错。这属于适配失败，不能算模型不会做 SDK 调查。

如果模型正确返回了读取请求，但 `release-notes.md` 不存在，则应由工具把文件错误反馈给模型。模型可以根据目录改读 `v1.md`、`v2.md`，无需重发完全相同的模型请求。再往后，模型读对文件却把 10 秒写成 5 秒，才进入答案质量和验收的问题。

当前网络适配器不自动重试。以后增加重试时，应先区分临时连接故障与固定的请求格式错误，再受次数和预算限制；反复提交服务不支持的参数不会让它突然受支持。换模型时同样要检查工具调用、结构化输出和参数兼容性，不能只改模型名称就默认其余行为一致。

## 用量没有返回，不等于用了零个 token

`usage` 是服务对本次请求用量的记录。Mini Agent 从中累加 `prompt_tokens`、`completion_tokens` 和 `total_tokens`；仅当字段存在且为整数时才计入。演示驱动返回 `{}`，因为它没有调用语言模型，不能拿它比较模型成本。

真实服务没给 usage 时，也会得到空记录，但含义是“没有观测到”。例如流式连接提前断开，可能已经生成并计费，却没有收到最后的用量片段。官方接口也明确说明中断时最终 usage 可能缺失，不能把它补成 0。[接口说明](https://developers.openai.com/api/reference/resources/chat)

还有更隐蔽的情况：五次请求只有三次返回 usage。直接累加这三次得到的是已知部分，不是本次运行的完整总用量。当前项目没有单独记录用量覆盖率；扩展时应增加“已计量请求数/全部请求数”，让读者知道总数是否完整。

费用还需要模型价格和计费规则，不能直接把 `total_tokens` 当金额。本项目只保存供应商返回的计数，不估算费用。真实模型的名称、服务配置、提示词和工具定义也应该与实验一起保存，否则两次结果差异可能只是调用条件不同。

## 接入真实模型时替换哪一层

先不配置密钥，从仓库根目录观察统一接口：

```bash
python 20-Projects/00-mini-agent/run.py run --stage 1 --mode demo --output .runs/adapter-demo
python -m unittest discover -s 20-Projects/00-mini-agent/tests -v
```

查看 `trace.jsonl` 的 `model_request` 与 `model_response`，你能看到输入消息和返回的工具调用。`DemoModel` 预先安排动作，`LiveModel` 请求远程服务，但二者都返回 `(message, usage)`；主循环因此无需知道是谁产生了回复。

测试中的网络接口检查使用预设响应，验证请求序列化和返回解析，不发起真实模型调用。`test_live_transport_serialization_without_external_request` 检查模型名、三个工具定义及 usage 的读取；测试通过不能推出真实模型会选对文件。

要运行真实模型，按[项目的环境变量说明](../../../20-Projects/00-mini-agent/README.md#接入真实模型)完成配置，然后执行：

```bash
python 20-Projects/00-mini-agent/run.py run --stage 1 --mode live --output .runs/adapter-live
```

检查 `run.json` 的 `mode`、`model` 和 `usage`，再看 `acceptance.json`。前者回答调用了什么和怎样停止，后者回答三项变更是否正确。没有配置时 live 会报错，不会改用演示结果。

## 两道练习：不要把格式和能力混在一起

**练习一：** 模型在 `content` 里回复“读取 v2.md”，同时没有 `tool_calls`。应改主循环去识别这句话，还是先检查模型接口？

参考解释：先看请求是否发送工具定义、服务是否支持对应格式，再看返回值。自然语言中出现函数名不等于操作请求；让循环猜测并执行普通文字，会把边界变得不明确。若确实要采用文本动作协议，应单独设计解析器和验证规则。

**练习二：** 一次请求只收到参数片段 `{"path":"v2` 后断线，usage 为空。能否补上 `.md"}` 执行，再记零成本？

参考解释：两个做法都不成立。未收到完整调用，文件名不能由适配器猜测；usage 缺失只能记为未知。应记录不完整响应，按策略重新发起请求，并把第二次尝试与第一次分开记录。

接着读 [Agent Loop](02-agent-loop.md)，看回复如何改变下一轮输入；返回[核心组件入口](04-core-components.md)。
