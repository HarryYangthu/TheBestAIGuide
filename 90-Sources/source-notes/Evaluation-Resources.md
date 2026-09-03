# Evaluation 资源索引

> 状态：reviewed
> 最近复核：2026-09-03
> 用途：记录评测专题使用的一手资料、适用范围和版本风险；知识结论见 [Evaluation](../../20-Knowledge/10-evaluation-observability/README.md)。

## 核心资料

| 来源 | 类型 | 支撑内容 | 使用提醒 |
| --- | --- | --- | --- |
| [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | 官方工程文章，2026-01-09 | Task、Trial、Transcript、Outcome、Harness、三类 Grader 和 Agent 生命周期 | 来自单一厂商经验，具体流程仍需按系统验证 |
| [OpenAI: Working with evals](https://developers.openai.com/api/docs/guides/evals) | 官方 API 指南 | Eval 数据源、运行、测试标准和工作流 | 产品接口会变化，使用前检查当前 API |
| [OpenAI: Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) | 官方指南 | 任务设计、评分策略和持续评测 | 页面与接口版本需一起记录 |
| [Chen et al.: Evaluating Large Language Models Trained on Code](https://arxiv.org/abs/2107.03374) | 论文 | HumanEval、功能正确性与 pass@k 估计器 | pass@k 的采样假设不能直接外推长程 Agent |
| [openai/human-eval](https://github.com/openai/human-eval) | 官方参考实现 | pass@k 计算和代码执行评测 Harness | 会执行不可信代码，必须使用沙箱 |
| [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/) | 开放标准文档 | Trace、Span、属性命名与跨系统关联 | GenAI 约定仍在迁移和演进，固定版本使用 |

## 补充资料

| 来源 | 用途 |
| --- | --- |
| [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | 理解 Multi-Agent 的路由、并行、协作与成本取舍 |
| [OpenAI Evals API reference](https://platform.openai.com/docs/api-reference/evals) | 查看当前 Eval、Run 和 Grader 数据结构 |

## 阅读顺序

1. 先读 Anthropic 的 Agent Eval 术语和系统模型。
2. 再读 OpenAI 的 Eval 工作流与最佳实践，对照不同实现抽取共性。
3. 用 HumanEval 论文理解 `pass@k` 的明确统计定义和适用边界。
4. 最后看 OpenTelemetry，设计自己的 Trace Schema 与兼容层。

## 来源管理规则

- 优先论文、官方文档、标准和源代码。
- 厂商文章中的经验数字不自动成为本知识库结论。
- 任何 Benchmark 分数必须同时记录模型、Harness、数据集、环境和日期。
- 链接、API 或标准状态变化后，更新复核日期并说明迁移影响。
- 二手解读可以进入 Inbox，但不能单独支撑 `reviewed` 结论。
