# Tool Runtime：把失败限制在可处理的范围

> 状态：draft。本文对照仓库源码说明机制；Python 文件工具与 TypeScript 通用执行层是两份独立教学实现。文中的 Pine SDK 是虚构教学产品。

Agent 想读取新版说明，发出了 `read_file(path="v2.md", start=1, limit=200)`。这看起来是一次合理操作，但工具最多允许读 20 行。程序如果直接执行，长文件会挤满下一轮上下文；如果直接抛异常，整个任务可能提前结束；如果吞掉错误并返回空字符串，模型还可能误以为文档没有内容。

工具执行层要把这次失败说清楚：请求被拒绝，原因是读取范围过大，文件还没有读取。模型随后可以把 `limit` 改成 20。**工具不是一段供模型阅读的说明，而是程序真正调用的函数；执行层负责让这次调用有清楚的边界和结果。**

## 从一句工具描述到一次真实读取

先看调用前各部分分别在哪里。[Mini Agent 的 tools.py](../../../../20-Projects/00-mini-agent/mini_agent/tools.py)用 `schemas()` 描述工具名称、用途和参数，例如 `read_file` 的 `path` 是字符串，`start`、`limit` 是整数。模型看到这些描述后，提出工具名和参数。宿主解析 JSON，找到 `ToolBox.read_file()`，调用 Python 函数，再把结果送回模型。

这里有两个容易混淆的动作：把 Schema 发给模型是在说明“请这样填写”；在服务端校验参数才是在保证“填错就不能执行”。即使模型服务支持结构化输出，也不能省掉后一个动作。模型可能给出格式正确但不存在的路径；宿主也可能从其他入口收到坏请求。

一个完整入口需要检查调用 ID、工具名和参数对象，再查询工具注册表，检查授权和参数，最后执行。授权与参数校验的先后可按系统设计调整，但都必须发生在真实操作之前。本库 TypeScript 实现先查权限，再验证工具参数；这样无权调用者不会进入 handler，也就是实际执行函数。

Python 入门项目没有通用 JSON Schema 校验器。它向模型发送 Schema，随后依靠函数参数和手写检查处理输入。TypeScript 的 [Registry](../05-code/tool-runtime-typescript/src/registry.ts)则在注册时编译输入、输出 Schema，并把它们与 handler、所需 scope 一起保存。这是从小项目过渡到通用执行层的一种方法，不代表 Mini Agent 已经接入了 TypeScript 服务。

## 正常结果要让下一步能继续

读取成功不能只返回“成功”。模型需要知道读到了什么、来自哪里、是否还有下一页。以下是对 [read_file](../../../../20-Projects/00-mini-agent/mini_agent/tools.py)关键代码的节选，省去了文件大小和输出长度检查：

```python
def read_file(self, path, start=1, limit=20):
    target = (self.docs / path).resolve()
    if not target.is_relative_to(self.docs) or target.suffix != ".md":
        raise ValueError("path_outside_documents")
    if type(start) is not int or type(limit) is not int or start < 1 or not 1 <= limit <= 20:
        raise ValueError("start >= 1, limit in 1..20")
    if not target.exists():
        raise FileNotFoundError(path)
    lines = target.read_text(encoding="utf-8").splitlines()
    selected = [{"line": i + 1, "text": text} for i, text in enumerate(lines)
                if start <= i + 1 < start + limit]
    return {"path": str(target.relative_to(self.docs)), "lines": selected,
            "next_start": start + limit if start + limit <= len(lines) else None}
```

`resolve()`先得到实际路径，再检查它是否仍在资料目录中，避免简单的 `../` 越界读取。`type(limit) is int`也会拒绝 Python 中继承自整数的布尔值，防止 `True` 被误当成行数。返回值中的行号来自原文件，不能在裁剪后重新从 1 编号，否则下游引用会指错位置。

读取 `v2.md` 第 3 行会得到超时值 10 秒；旧版第 3 行是 30 秒。工具只负责返回这两行，并不自动得出“应把超时从 30 秒改成 10 秒”。这个比较由 Agent 完成，写入报告后还要经过独立验收。`write_report` 返回 `written` 只证明文件已经写出，不能证明选对了版本或结论正确。

## 报错也要是一份能辨认的结果

同样是失败，`invalid_arguments` 表示调用方填错参数，`permission_denied` 表示当前身份不能操作，`execution_error` 表示操作过程中出错。把三者都写成“工具失败，请重试”，会让模型反复做没有意义的尝试。

本库 TS Runtime 的返回对象采用 `ok` 区分成功与失败。例如缺少 scope 时返回 `{"call_id":"read-1","ok":false,"error":{"code":"permission_denied","retryable":false}}`。成功则放入 `data`，并验证输出 Schema。如果搜索工具约定返回整数 `count`，却返回字符串 `"one"`，执行层会报 `invalid_output`，避免错误悄悄传给下游。

Mini Agent 使用更小的约定：成功内容放在 `result`；从第 2 阶段起，已知工具异常转换为 `ok=false`、异常类型和简短细节，并写入 `trace.jsonl`。两份实现的字段并不相同。系统接入新工具时，应该统一转换一次，不能要求每个 Agent 自己猜测各种错误格式。错误细节也不能原样包含服务密钥；TS 示例只返回安全错误码。

## 超时与取消为什么不是强制杀死

假设写报告花了 2 秒，而调用方等到 1 秒就超时。此时报告可能已经写出，只是响应还没到。超时说明“没有及时收到结果”，不能推出“操作没有发生”。直接重试写操作，可能造成重复邮件、重复扣款或重复实验提交。

TS Runtime 用 `Promise.race` 等待 handler 和中断结果，同时向 handler 传 `AbortSignal`。前者决定何时停止等待，后者请求操作停止。handler 要配合检查信号，网络客户端也要支持取消；阻塞事件循环的代码甚至会阻止超时定时器及时触发。要终止不合作的计算，需使用可终止的进程或 Worker，并处理已发生的外部效果。

文件路径检查解决的是“这个读文件函数是否越界”。执行隔离解决的是“被执行的代码能碰到哪些文件、网络和进程”。如果另外开放任意 Shell，模型仍可能绕开上述 Python 函数。Mini Agent 没有开放 Shell；它的路径检查不应被称为操作系统沙箱。

## 幂等缓存要处理并发与冲突

两次相同请求可能同时到达。只在执行完后保存结果，会让二者都先执行一遍。本库 TS Runtime 以 `(subject, call_id)` 为键，在第一次调用开始时就保存正在执行的 Promise。第二次若参数相同，等待这份结果；若参数不同，返回 `idempotency_conflict`。

这意味着 ID 是一次操作的身份，不能把 `read-1` 先用于读 v1，随后又用于读 v2。参数签名按对象键排序，避免 JSON 字段顺序变化被误认为不同操作；输入和结果复制后使用，避免调用者在验证后偷偷修改对象。

这份缓存只存在于当前进程，重启后会消失。它不提供跨服务“绝对只执行一次”的保证。写操作若需要可靠重试，应在真正修改数据的后端保存操作 ID 与提交回执；结果未知时先查询。当前实现还让重复等待者复用首个请求的取消语义，不能把它理解成每个等待者独立控制底层操作。

## MCP 工具也要真正执行一次

如果文件在远端服务中，可以通过 MCP 接入。客户端先用 `tools/list` 获取工具名称与 Schema，再用 `tools/call` 传递参数，并解析返回内容和错误标志。把工具描述从配置文件读进提示词，只完成了介绍工具这一步，还没有建立可执行连接。这里采用固定版本的[官方工具规范](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)，完整版本说明见 [MCP 专题](../01-concepts/03-mcp.md)。

本库 [MCP 工程](../05-code/mcp-server-typescript/README.md)会启动真实 stdio 子进程，再发现、调用和关闭；它与本篇 TS Runtime 仍是分开的教学工程。MCP 解决消息如何互通，宿主和服务端仍须检查权限、参数、超时与结果。

## 怎样验证，先看哪些反例

从仓库根目录运行下面的离线案例；再次运行时换一个输出目录：

```bash
python 20-Projects/00-mini-agent/run.py run --stage 2 --mode demo --output .runs/tool-lesson
python 20-Projects/00-mini-agent/run.py verify --output .runs/tool-lesson
```

打开 `report.md` 看三项变更，再看 `trace.jsonl` 的工具结果和 `acceptance.json` 的 `passed`。`demo` 预先编写模型动作，但真实执行文件操作；它不测模型自主选择工具的能力。

通用执行层的反例在 [runtime.test.ts](../05-code/tool-runtime-typescript/test/runtime.test.ts)。进入[工程目录](../05-code/tool-runtime-typescript/README.md)执行 `npm ci`、`npm test`（Node 22+）；预期是测试全部通过。测试会主动传错类型、额外字段、无权限身份和重复 ID，并确认这些情况被正确拒绝。终端测试结果是此工程的产物，它不会生成 Pine 报告。

**练习 1：** 把读取行数从 20 改成 200 后报错，应该增加重试次数吗？答案：先改参数，重复同一非法请求没有帮助。让模型收到具体约束，再检查下一次工具参数是否缩小。

**练习 2：** `write_report` 已返回成功，验收却发现引用了废弃预览稿，该改 Runtime 吗？答案：先改选材或比较过程。文件写入成功与内容符合任务是两项检查；只有报告格式或写入行为违反契约，才属于工具实现问题。

返回 [Agent 核心组件总览](../../03-agent-core/01-concepts/04-core-components.md)，继续理解工具如何接入执行循环。
