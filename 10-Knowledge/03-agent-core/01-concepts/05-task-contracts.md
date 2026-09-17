# 任务与协议：先说清交什么，再讨论怎么做

> 状态：draft | 配套实践：[Mini Agent](../../../20-Projects/00-mini-agent/README.md)；Pine SDK 为虚构教学产品

你让 Agent “整理一下 SDK 升级的变化”，它给出三段通顺的文字，最后说“整理完成”。但你原本想要一份可以交给开发者使用的清单：具体改哪个字段，旧值和新值是什么，结论出自哪里。双方都觉得自己理解了任务，最后却没有得到同一种东西。

任务与协议层要解决的就是这个问题。它把一句请求变成几项明确约定，让执行程序知道接收什么、交付什么，让验收程序知道检查什么。这里的“协议”先理解为程序之间的数据约定即可，不需要先学习某种网络协议。

## 1. 把“整理变化”改成可以检查的任务

先打开教学资料 [v1.md](../../../20-Projects/00-mini-agent/fixtures/docs/v1.md) 和 [v2.md](../../../20-Projects/00-mini-agent/fixtures/docs/v2.md)。两份文件都有认证、超时、重试三项。以超时为例，旧版第 3 行写着“超时：默认等待 30 秒。”，新版第 3 行变成“超时：默认等待 10 秒。”。

现在把请求写完整：比较 Pine SDK v1 与 v2 **正式版**，输出 `auth`、`timeout`、`retry` 三项；每项给出新旧值，以及两侧的文件名、行号和原文；调用 `write_report` 保存清单；不能采用废弃预览稿。

这里每个补充都有作用。“正式版”排除目录里的 `preview.md`；三项名称规定内容范围；新旧两侧引用允许读者复查变化；保存文件则把交付物与聊天回复区分开。约束没有规定必须先读 v1 还是 v2，因为两种顺序都可能得到正确结果。

任务目标与执行计划因此不同。任务目标是“交付三项有依据的变更”，计划可能是“列目录、读旧版、读新版、写清单”。缺少某份资料时，计划可以改变，但程序不能为了让本次运行成功，就自行把任务改成“随便写一项”。

## 2. Task、Run、Attempt 为什么要分开

假设同一个任务今天用模型 A 执行一次，明天换模型 B 再执行一次。如果只给它们一个编号，第二次的失败日志就可能和第一次的成功报告混在一起。

可以约定：`task_id` 标识要完成的工作；`run_id` 标识一次完整执行；`attempt` 标识某个操作的第几次尝试。比如任务是 `pine-v1-v2`，模型 A 的运行叫 `run-a`。其中读取文件的调用 `read-v2` 第一次超时，第二次成功，是同一操作的两个 attempt。模型 B 从头再做，则建立 `run-b`，不应把它记成读取工具的第三次尝试。

这套命名是本章的扩展设计，不是各框架都必须照搬的标准。关键是编号指向的对象不能混用。还要写明 attempt 属于工具操作、子任务还是整个作业，否则“重试了三次”仍然不清楚。

Mini Agent 为了保持简单，没有实现这套完整字段，而是要求每次使用一个新的输出目录；目录已存在就拒绝运行。这样 `.runs/pine-a/report.json` 和 `.runs/pine-b/report.json` 不会互相覆盖。另一个最小实现的 [AgentState](../05-code/agent-loop-python/src/agent_loop/models.py) 已有 `task` 和 `run_id`，但同样没有 attempt 管理。读代码时要按实际字段理解能力。

## 3. Schema 描述形状，不能只看 JSON 能否解析

JSON 是表示数据的格式，Schema 是描述数据应当长什么样的规则。`{"line":"第三行"}` 是合法 JSON，但如果后续代码要用 `line - 1` 读取文件，它就不能工作。反过来，`{"line":3}` 的类型正确，却仍然可能引用了错误文件。

下面是为引用对象设计的一份简化 JSON Schema，用 Python 字典表示：

```python
citation_schema = {
    "type": "object",
    "properties": {
        "path": {"type": "string"},
        "line": {"type": "integer", "minimum": 1},
        "quote": {"type": "string"},
    },
    "required": ["path", "line", "quote"],
    "additionalProperties": False,
}
```

`properties` 说明各字段类型，但不会自动要求字段出现；`required` 才规定三者必须都有。`minimum` 排除第 0 行和负数，`additionalProperties` 排除未约定的额外字段。JSON Schema 的这些含义可以在[官方对象规范](https://json-schema.org/understanding-json-schema/reference/object)中核对。

仅仅创建这个字典不会启动检查。你还得把它交给验证器，或者像本项目的 [write_report](../../../20-Projects/00-mini-agent/mini_agent/tools.py) 一样，用 Python 明确检查字段集合、类型和取值范围。发给模型的工具定义只是告诉模型如何填写；模型返回后，宿主仍要检查。

## 4. 一条 timeout 记录怎样从原文进入报告

把整个过程跟一遍：`read_file("v2.md")` 返回带行号的列表，其中一项是 `{"line":3,"text":"超时：默认等待 10 秒。"}`。模型把它和 v1 第 3 行比较，向 `write_report` 提交下面这一条记录；完整报告还需要另两项。

```json
{
  "id": "timeout",
  "before": "30 秒",
  "after": "10 秒",
  "old_source": {
    "path": "v1.md", "line": 3, "quote": "超时：默认等待 30 秒。"
  },
  "source": {
    "path": "v2.md", "line": 3, "quote": "超时：默认等待 10 秒。"
  }
}
```

为什么值和引用要分开？`after` 给使用者看最直接的结论，`quote` 留下支持结论的完整原文。若两者混成“据新版文档，超时似乎改成 10 秒”，程序就很难分别判断字段值和出处。

工具首先检查这条记录的形状，然后保存 `report.json` 和 `report.md`。它返回 `written`，只说明文件已写入。接下来，独立验收器读取报告，把三项 ID 与预期集合比较，再检查每一项的新旧值，以及引用的路径、行号、原文是否一致。这时才回答“本任务有没有做对”。

例如 `after="5 秒"`、`source.path="preview.md"`，所有字段和类型都可以正确，引用甚至可以逐字真实，却仍然违反“使用正式版”的任务约定。这是业务错误，不是 JSON 解析错误。

## 5. 输入、输出、错误，最好都能让下一步采取行动

本项目的输入分散在明确的位置：`TASK` 保存自然语言任务，`--docs` 指定可读取资料，`--format` 指定输出样式，`--max-steps` 限制执行轮数。它们各自回答不同问题。步数上限是运行约束，不能拿来替代“必须包含三项变化”的结果要求。

输出也有两个层面：报告是给使用者的成果，`run.json` 和 `acceptance.json` 是程序对这次运行的记录。把它们分开以后，就能表达“报告已经写了，但运行提前中止”，而不是只能给出笼统的成功或失败。

错误类型同样影响下一步。文件不存在，Agent 可以先查看目录、换成真实文件名；参数类型错误，应修正参数；结果漏了 `retry`，需要补读资料并重新生成报告。若所有情况都只返回“失败，请重试”，模型可能反复执行完全一样的错误请求。

Mini Agent 从第 2 阶段起把部分工具异常转成 `ok=false`、异常类型和简短详情，交回下一轮。它还没有统一的跨服务错误码系统。较完整的设计可以再区分 `invalid_input`、`permission_denied`、`timeout`、`acceptance_failed`，但这些名字有用的前提，是调用方确实据此采取不同动作。

## 6. 正常完成与“看起来完成”，亲自对照一次

从仓库根目录运行，输出目录要使用尚不存在的名称：

```bash
python 20-Projects/00-mini-agent/run.py run --stage 1 --mode demo --output .runs/contracts-first
python 20-Projects/00-mini-agent/run.py verify --output .runs/contracts-first
```

第一条应得到 `status="completed"`、`passed=true`；第二条重新检查已有报告。先看 `report.json` 的 `timeout`，对照上节字段，再看 `acceptance.json` 中的 `exact_required_changes`、`timeout:values` 和 `timeout:source`。检查名称直接告诉你是在检查完整性、值还是出处。

再运行完整教学实验：

```bash
python 20-Projects/00-mini-agent/learn.py --output .runs/contracts-course
```

对比 `stage-07/acceptance.json` 与 `expected-citation-failure/acceptance.json`。后者把引用改成废弃文档，应该失败。总表却把这个故障实验记为 PASS，因为教学实验要验证的是“系统能否发现错误”。不要把总表里的 PASS 理解成那份错误报告通过了验收。

`demo` 的动作和答案字段由程序预先编写，工具仍然真实读写文件。这里验证的是任务约定和检查程序，不是模型自主完成任务的能力。真实模型入口见项目 README。

## 7. 两道练习：从字段走回任务本身

**练习一：** 删除 timeout 的 `old_source`，与保留全部字段但把新版值改成“5 秒”，分别应该在哪里发现？

参考解释：删除必需字段应在 `write_report` 的结构检查中被拒绝，尚不需要判断 SDK 知识。错误数值可以通过结构检查并写入文件，随后由独立验收的 `timeout:values` 发现。两种失败应该保留不同原因，修复手段也不同。

**练习二：** 今天要求比较 v1→v2，明天改成 v2→v3，可以只修改用户提示词，继续使用原验收文件吗？

参考解释：不可以。目标、资料和验收依据必须一起版本化；旧验收文件仍然在检查 v1/v2 的固定三项，会拒绝新的正确结果，或接受不相关的旧结果。此时应创建新任务或新任务版本，再生成新的运行记录。修改执行计划则通常不需要改变任务版本，因为要交付的内容没变。

接着读 [Agent Loop](02-agent-loop.md)，看这些约定如何进入一次次模型调用；返回[核心组件入口](04-core-components.md)。
