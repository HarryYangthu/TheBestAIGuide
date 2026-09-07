# 项目 00：从一个循环写起的 Mini Agent

给出一个资料目录，让 Agent 找到 Pine SDK 从 v1 升级到 v2 的三项变化，读取原文并写出升级清单。Pine 是本项目虚构的教学产品，不是实际 SDK。你不需要领域知识，只需要能读懂 Python 函数、列表和字典。

**完成后，你应该拿到一份有出处的清单、一份执行记录和一份可以失败的验收报告。** 七个阶段使用同一任务，逐步加入错误处理、上下文管理、记忆、计划、并发和 Harness。先跑通，再按章节修改代码、制造故障、解释结果。

## 先运行，看到具体结果

要求 Python 3.11 或更高版本，全部代码只依赖标准库。以下命令从**仓库根目录**运行，Windows PowerShell、macOS 和 Linux 写法相同。若系统使用 `python3`，统一替换 `python`。不需要先安装整个仓库的训练或 Notebook 依赖。

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

注意：`preview.md` 中的 5 秒和 5 次属于废弃预览稿，不能当成正式版结论。对照 [v1 原文](fixtures/docs/v1.md)、[v2 原文](fixtures/docs/v2.md) 检查上表。JSON 清单还保存每项新旧两侧的完整原文。

`demo` 使用**预先编写的工具调用轨迹和答案字段**，实际执行读文件、写报告等工具。它帮助观察程序机制，不证明模型会自主调查问题。`live` 才由真实模型决定动作。两种模式的结果都标注模式，不能混在一起报告成功率。

## 一次跑完七步，并生成完成报告

```bash
python 20-Projects/00-mini-agent/learn.py --output .runs/mini-course
```

这条命令执行七次独立任务，以及上下文、记忆、并行、预算耗尽和错误引用实验。打开 `.runs/mini-course/completion.md`，七个阶段和五项实验都应该是 PASS。对应机器可读文件是 `completion.json`，顶层 `passed` 应为 `true`。

| 你应该得到的报告 | 位置（相对单次运行目录） | 用它判断什么 |
| --- | --- | --- |
| 升级清单 | `report.md`、`report.json` | 三项变化齐全；新旧字段正确；每项有双方原文引用 |
| 独立验收报告 | `acceptance.md`、`acceptance.json` | 全部检查 PASS；漏项、假引用、错版本都应失败 |
| 工具调用轨迹 | `trace.jsonl` | 调用了什么工具、参数是什么、工具返回什么、失败后有没有继续 |
| 完整消息记录 | `messages.json` | 模型消息、tool_call_id 与工具响应怎样配对 |
| 运行记录 | `run.json` | 模式、模型名、结束原因、调用次数、工具错误数、格式来源、上下文统计、实际用量（服务提供时） |
| 全课程完成报告 | `mini-course/completion.md`、`completion.json` | 七步结果和五个实验是否达到预期 |
| 子 Agent 回执〔选学〕 | `delegation.json`、两份 `*.trace.json` | 两个独立上下文分别读取了指定文件并正常结束 |

可以先看仓库中实际执行后保存的 [参考清单](reference/stage-07/report.md)、[参考验收报告](reference/stage-07/acceptance.md)、[参考完成报告](reference/completion.md)、[参考运行记录](reference/stage-07/run.json)。用 [结果对照说明](REFERENCE.md) 区分固定结果与每次会变化的计时数据。

**两个故障目录应当是 FAIL：** `expected-budget-failure` 表示在任务完成前用尽步数；`expected-citation-failure` 表示引用被改成了废弃文档。完成表对这两项显示 PASS，是因为系统成功识别了预设错误，而不是错误任务成功了。

## 七步怎么学

每一步都能单独运行，例如把第一条命令改成 `--stage 3 --output .runs/mini-stage3`。每次使用新的输出目录，程序拒绝覆盖已有实验，避免把上次成功文件误认为本次产物。

| 阶段 | 阅读入口 | 本次增加什么 | 学完应能解释 |
| --- | --- | --- | --- |
| 01 | [最小循环](lessons/01-loop.md) | 三个工具与模型循环 | 模型输出调用请求，Python 执行函数，结果再进入下一轮 |
| 02 | [错误与停止](lessons/02-errors.md) | 错误转为工具反馈、明确失败状态 | 为什么一次工具失败不必结束整个任务 |
| 03 | [上下文](lessons/03-context.md) | 分段读取、完整消息组裁剪、请求预算 | 裁剪省下什么，也可能丢掉什么 |
| 04 | [记忆](lessons/04-memory.md) | 显式偏好持久化、当前覆盖、删除 | 会话历史与跨会话记忆有什么区别 |
| 05 | [计划](lessons/05-planning.md) | 计划工具与状态修改 | 计划如何因新证据而改变，为什么计划完成不等于结果正确 |
| 06 | [并发与子 Agent〔选学〕](lessons/06-parallel.md) | 真线程读取、独立模型上下文实验 | 并发工具与多 Agent 分别多了什么 |
| 07 | [Harness 与验收](lessons/07-harness.md) | 组织全部实验、独立评分、汇总报告 | 哪些条件意味着任务完成，哪些只是程序停止 |

代码保留一个可直接阅读的 [主循环](mini_agent/runtime.py)，各阶段通过 `stage` 开启新增能力，避免七份复制代码产生不一致。工具在 [tools.py](mini_agent/tools.py)，模型适配在 [providers.py](mini_agent/providers.py)，其他模块与章节同名。第 07 步的新增入口是 [learn.py](learn.py) 和 [harness.py](mini_agent/harness.py)，单独 `--stage 7` 使用第 06 步已有运行能力。

## 接入真实模型

使用支持 Chat Completions 工具调用格式的服务。端点应是兼容 API 的基础地址，程序在后面追加 `/chat/completions`。不同服务对工具 schema 的支持可能不同；HTTP 错误不能当成模型能力评测结果。

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

`--mode live` 没有配置时会报错，不会偷偷切换到 demo。模型请求超时是 60 秒，不自动重试；默认最多 16 次主循环模型调用，一轮最多 8 次工具调用。`usage` 只记录服务实际返回的 token 计数，未返回则为空；不估算费用。程序不向模型开放 Shell，也不开放参考答案文件。

本次提交验证了离线实验和网络请求的序列化契约，**没有验证某个真实模型的完成率**。使用者需自行运行 live 并保留 `run.json` 与 `acceptance.json`；模型可能选错文件、漏项、用错值或超出步数，这些都是有效失败记录。

## 怎样算完成这个项目

| 层次 | 达成标准 | 不能据此声称什么 |
| --- | --- | --- |
| 环境与机制跑通 | `learn.py` 的整体 `passed=true`；能找到上述报告 | 不能声称真实模型成功 |
| 模型任务跑通 | 一次 live 运行 `mode=live` 且独立验收全部 PASS | 不能声称换模型、换资料后仍可靠 |
| 理解并能修改 | 完成各章练习，能解释一次失败轨迹；修改错误后让验收重新通过 | 仅复制参考结果不等于掌握代码 |

建议留下自己的实验小结：运行模式与模型、清单、失败轨迹、改动、前后验收差异。可复制 [实验报告模板](EXPERIMENT.md) 填写。这里不规定模型必须得到完全一致的工具顺序；以证据和最终结果验收。

重新检查已有产物：

```bash
python 20-Projects/00-mini-agent/run.py verify --output .runs/mini-first
python -m unittest discover -s 20-Projects/00-mini-agent/tests -v
```

任何验收失败时退出码为 1，成功为 0。只输出了“已完成”但没有写清单，也会失败。

## 范围与下一步

上下文预算使用序列化文本**字符数**，不伪装成模型 token 上限；只限制发送给模型的消息，宿主保留完整轨迹。记忆仅处理显式输出格式偏好，不做自然语言记忆抽取。计划没有复杂调度器；运行记录不提供崩溃后自动恢复。子 Agent 实验只检验独立上下文与工具权限，不宣称协作收益。文件路径限制适用于这个没有任意代码执行能力的教学工具，不是操作系统级沙箱。

先用小资料理解这些边界，再进入 [领域资料研究助手](../domain-research-agent/README.md) 和 [学习工作台](../learning-workbench/README.md)。本项目使用 Markdown 讲解与 JSON 轨迹，运行不依赖 Jupyter；已有资料足以在普通编辑器逐条检查消息。

教学形式参考 [nanoAgent](https://github.com/sanbuphy/nanoAgent)：用小型循环逐步增加能力。本项目代码独立编写；未复制其源码。正式知识背景见各章节链接。
