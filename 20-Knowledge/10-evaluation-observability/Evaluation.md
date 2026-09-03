# Agent Evaluation

> 状态：draft
> 定位：专题总览；原长文已拆为可独立链接的笔记。

## 定义

Agent Evaluation 是在固定任务、环境和系统配置下，多次运行 Agent，记录轨迹与最终状态，并用可校准的评分器判断质量、可靠性、效率和风险。

Agent 评测的基本单位不是单个模型回答，而是整个系统的一次运行：

```text
Task + Initial State
        │
        ▼
Model + Agent Harness + Tools + Environment
        │
        ├─> Trajectory：消息、工具调用、路由、错误和时间线
        └─> Outcome：文件、数据库、外部系统等最终状态
                              │
                              ▼
           Deterministic + Model + Human Graders
                              │
                              ▼
                  Metrics + Failure Analysis
```

## 为什么不能只看最终回答

- Agent 可能声称动作成功，但环境没有变化。
- 同一个任务多次运行可能得到不同结果。
- 结果正确也可能伴随越权、泄露或不可接受的成本。
- 模型相同但 Harness、工具或环境不同，系统表现会不同。
- 评分器本身也可能有缺陷，需要版本化和校准。

因此要把 `Outcome`、`Trajectory`、系统配置和评分结果放在同一个评测记录中。

## 专题索引

1. [评测对象与系统模型](01-evaluation-model.md)
2. [任务、数据集与多次试验](02-tasks-datasets-and-trials.md)
3. [评分器与组合计分](03-graders-and-scoring.md)
4. [统计与可靠性](04-statistics-and-reliability.md)
5. [Trace 与失败归因](05-traces-and-failure-analysis.md)
6. [Multi-Agent 评测](Multi-Agent-Evaluation-Guide.md)
7. [评测运营与发布门禁](07-evaluation-operations.md)
8. [模板与检查清单](08-templates-and-checklists.md)

## 最小评测闭环

1. 把真实需求和失败写成无歧义任务。
2. 固定系统、模型、工具、数据和环境版本。
3. 建立简单基线，再运行多个 Trial。
4. 优先用确定性检查验证最终状态。
5. 用模型或人工评分补充开放式质量判断。
6. 阅读失败轨迹，区分模型、上下文、工具、环境和评分器责任。
7. 把确认的失败加入回归集。
8. 在发布前检查质量、可靠性、成本和安全门禁。

## 证据边界

本模块整理了评测设计方法，但 [Evaluation Labs](../../50-Labs/evaluation/README.md) 和 [Eval Harness 工程](../../60-Code/eval-harness-python/README.md) 仍是占位。文中的任务、阈值和数字均为结构示例，不代表本仓库已经完成基准测试。

## 主要来源

- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [OpenAI: Working with evals](https://developers.openai.com/api/docs/guides/evals)
- [Chen et al.: Evaluating Large Language Models Trained on Code](https://arxiv.org/abs/2107.03374)

来源用途和复核日期见 [Evaluation 资源索引](../../90-Sources/source-notes/Evaluation-Resources.md)。
