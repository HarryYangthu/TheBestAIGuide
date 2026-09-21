# 项目 00：从一个循环写起的 Mini Agent

本项目让 Agent 读取两份资料，整理 Pine SDK 从 v1 升级到 v2 的三项变化，并写出带原文引用的升级清单。Pine SDK 是虚构的教学案例，输入文件是 [v1.md](fixtures/docs/v1.md) 和 [v2.md](fixtures/docs/v2.md)。

资料目录还包括 [preview.md](fixtures/docs/preview.md)，这是一份已废弃的预览稿，用于检查 Agent 是否选对版本。

七个阶段使用同一任务，逐步加入错误处理、上下文管理、记忆、计划、并发，以及运行与验收程序（Harness）。每次运行都会保存清单、执行记录和验收报告。

相关知识见 [Agent 组件学习路线](../../10-Knowledge/02%20Agent%20Harness/README.md)。

## 先运行，看到具体结果

要求 Python 3.11 或更高版本，只依赖标准库。在 VS Code 中打开仓库根目录（如 `TheBestAIGuide_run`），以下命令均从该目录运行。若系统使用 `python3`，将命令中的 `python` 替换为 `python3`。

```bash
python 20-Projects/00-mini-agent/run.py run --stage 1 --mode demo --output .runs/mini-first
```

输出末尾应包含：

```json
{"mode": "demo", "status": "completed", "passed": true}
```

终端还会显示实际输出目录。打开 `.runs/mini-first/report.md`，应看到：

| 项目 | 旧版 | 新版 | 原文位置（旧 / 新） |
| --- | --- | --- | --- |
| auth | X-API-Key | Authorization: Bearer | v1.md:2 / v2.md:2 |
| timeout | 30 秒 | 10 秒 | v1.md:3 / v2.md:3 |
| retry | 3 次 | 0 次 | v1.md:4 / v2.md:4 |

`report.json` 保存字段值，以及新旧两侧的引用路径、行号和完整原文。

`demo` 按预设顺序调用工具，使用固定答案字段；`live` 由真实模型选择工具并填写参数。

## 一次跑完七步，并生成完成报告

```bash
python 20-Projects/00-mini-agent/learn.py --output .runs/mini-course
```

这条命令执行七个阶段及五项实验。结果保存在 `.runs/mini-course/completion.md` 和 `completion.json` 中，全部通过时 `passed` 为 `true`。

| 你应该得到的报告 | 位置（相对单次运行目录） | 用它判断什么 |
| --- | --- | --- |
| 升级清单 | `report.md`、`report.json` | 三项变化齐全；新旧字段正确；每项有双方原文引用 |
| 独立验收报告 | `acceptance.md`、`acceptance.json` | 全部检查 PASS；漏项、假引用、错版本都应失败 |
| 工具调用轨迹 | `trace.jsonl` | 调用了什么工具、参数是什么、工具返回什么、失败后有没有继续 |
| 完整消息记录 | `messages.json` | 模型消息、tool_call_id 与工具响应怎样配对 |
| 运行记录 | `run.json` | 模式、模型名、结束原因、调用次数、工具错误数、格式来源、上下文统计、实际用量（服务提供时） |
| 子 Agent 回执〔选学〕 | `delegation.json`、两份 `*.trace.json` | 两个独立上下文分别读取了指定文件并正常结束 |

运行后可对照 [参考清单](reference/stage-07/report.md) 和 [参考完成报告](reference/completion.md)。字段值应一致；每次运行的耗时可能不同。各项结果的含义见 [结果对照说明](REFERENCE.md)。

两个故障实验会主动制造错误：`expected-budget-failure` 用尽运行步数，`expected-citation-failure` 将新版引用改为已废弃的 `preview.md`。单次验收应为 FAIL，完成表中的 PASS 表示成功检出了错误。

## 七步怎么学

每一步都能单独运行，例如 `--stage 3 --output .runs/mini-stage3`。每次使用新的输出目录，程序不覆盖已有结果。

| 阶段 | 阅读入口 | 本次增加什么 | 学完应能解释 |
| --- | --- | --- | --- |
| 01 | [最小循环](lessons/01-loop.md) | 三个工具与模型循环 | 模型输出调用请求，Python 执行函数，结果再进入下一轮 |
| 02 | [错误与停止](lessons/02-errors.md) | 错误转为工具反馈、明确失败状态 | 为什么一次工具失败不必结束整个任务 |
| 03 | [上下文](lessons/03-context.md) | 分段读取、完整消息组裁剪、请求预算 | 裁剪省下什么，也可能丢掉什么 |
| 04 | [记忆](lessons/04-memory.md) | 显式偏好持久化、当前覆盖、删除 | 会话历史与跨会话记忆有什么区别 |
| 05 | [计划](lessons/05-planning.md) | 计划工具与状态修改 | 计划如何因新证据而改变，为什么计划完成不等于结果正确 |
| 06 | [并发与子 Agent〔选学〕](lessons/06-parallel.md) | 真线程读取、独立模型上下文实验 | 并发工具与多 Agent 分别多了什么 |
| 07 | [Harness 与验收](lessons/07-harness.md) | 组织全部实验、独立评分、汇总报告 | 哪些条件意味着任务完成，哪些只是程序停止 |

七个阶段共用 [runtime.py](mini_agent/runtime.py) 的主循环，通过 `stage` 开启能力。工具实现在 [tools.py](mini_agent/tools.py)，模型调用在 [providers.py](mini_agent/providers.py)。第 07 步通过 [learn.py](learn.py) 和 [harness.py](mini_agent/harness.py) 组织整组实验；单独运行 `--stage 7` 时使用第 06 步已有的运行能力。

## 接入真实模型

使用支持 Chat Completions 工具调用格式的服务。填写 API 基础地址、密钥和模型名称；程序会在基础地址后追加 `/chat/completions`。

macOS/Linux：

```bash
export MINI_AGENT_API_KEY='替换为你自己的密钥'
export MINI_AGENT_BASE_URL='https://你的服务地址/v1'
export MINI_AGENT_MODEL='你的模型名称'
python 20-Projects/00-mini-agent/run.py run --stage 7 --mode live --output .runs/mini-live-01
```

Windows PowerShell：

```powershell
$env:MINI_AGENT_API_KEY='替换为你自己的密钥'
$env:MINI_AGENT_BASE_URL='https://你的服务地址/v1'
$env:MINI_AGENT_MODEL='你的模型名称'
python 20-Projects/00-mini-agent/run.py run --stage 7 --mode live --output .runs/mini-live-01
```

默认请求超时为 60 秒，最多进行 16 轮模型调用，每轮最多执行 8 次工具调用。

运行结束后，打开输出目录中的 `report.md` 查看清单，打开 `acceptance.md` 查看各项检查结果。

## live 未通过时，怎样定位和修改

下面以一次实际运行中的 `retry:values` 失败为例。这次运行共有 13 项检查，12 项通过。

### 1. 从验收报告找到失败项

在 VS Code 中打开 `.runs/mini-live-01/acceptance.json`，搜索 `false`，在 `checks` 数组中找到：

```json
{"check": "retry:values", "passed": false}
```

`retry` 是重试次数这一项，`values` 表示检查 `before` 和 `after` 的值。若失败项是 `source` 或 `old_source`，则检查对应引用的文件、行号和原文。

### 2. 对照输出、原文和验收代码

打开同目录的 `report.json`，找到 `"id": "retry"`：

```json
"before": "3 次",
"after": "0 次（调用方须显式配置）"
```

再打开 [fixtures/expected.json](fixtures/expected.json)，其中要求的 `after` 是 `"0 次"`。[evaluate.py](mini_agent/evaluate.py) 的 `check(key + ":values", ...)` 使用 `==` 比较字符串，因此附加说明也会造成不相等。

[v2.md](fixtures/docs/v2.md) 第 4 行确实包含“调用方必须显式配置”。这次 API 调用成功，JSON 结构也正确，但模型在 `after` 中多写了说明，未遵守“只填字段值”的要求。验收程序比较的是字段文字是否完全一致；完整原文另保存在引用的 `quote` 中。

在 `trace.jsonl` 中搜索 `write_report`，查看 `model_response` 中的调用参数，可以确认这段附加说明由模型填写。[tools.py](mini_agent/tools.py) 的 `write_report` 随后将参数写入 `report.json`。

### 3. 修改模型收到的要求

打开 [runtime.py](mini_agent/runtime.py)，找到文件开头的 `TASK`。原要求只说“before/after 只写字段值”，现改为：

```python
TASK = ("比较 Pine SDK v1 与 v2 正式版，输出 auth、timeout、retry 三项变更。"
        "before/after 只写字段值，保留数值和单位，不附加括号、解释或条件说明。"
        "每项引用旧版和新版的完整原文行，quote 保留原文中的说明。"
        "不要采用已废弃预览稿。调用 write_report 保存结果。")
```

[tools.py](mini_agent/tools.py) 的 `schemas` 函数也为 `before`、`after` 增加了同样的字段说明。模型选择 `write_report` 工具时能同时看到这些要求。

### 4. 用新目录重跑并比较

保存文件，在配置好模型环境变量的终端执行：

```bash
python 20-Projects/00-mini-agent/run.py run --stage 7 --mode live --output .runs/mini-live-02
```

保留 `mini-live-01` 作为修改前记录。检查新目录的 `report.json` 中是否只写了 `"0 次"`，再查看 `acceptance.json` 中 `retry:values` 及整体 `passed` 的结果。若还有失败项，按上面的顺序继续查找。

## 怎样算完成这个项目

| 阶段 | 达成标准 |
| --- | --- |
| 跑通离线实验 | `learn.py` 的整体 `passed=true` |
| 跑通真实模型 | live 运行的验收全部 PASS |
| 完成练习 | 能定位一次失败，修改后重新运行并比较结果 |

用 [实验报告模板](EXPERIMENT.md) 记录运行命令、失败原因、修改位置和前后结果。

## 下一步

完成后可进入 [领域资料研究助手](../domain-research-agent/README.md) 和 [学习工作台](../learning-workbench/README.md)。

教学形式参考 [nanoAgent](https://github.com/sanbuphy/nanoAgent)，代码独立编写。
