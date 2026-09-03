# Evaluation and Observability

> 状态：draft
> 已完成结构重写；尚未完成本仓 Eval Harness 与实验验证。

## 阅读顺序

1. [Agent Evaluation 总览](Evaluation.md)
2. [评测对象与系统模型](01-evaluation-model.md)
3. [任务、数据集与多次试验](02-tasks-datasets-and-trials.md)
4. [评分器与组合计分](03-graders-and-scoring.md)
5. [统计与可靠性](04-statistics-and-reliability.md)
6. [Trace 与失败归因](05-traces-and-failure-analysis.md)
7. [Multi-Agent 系统评测](Multi-Agent-Evaluation-Guide.md)
8. [评测运营与发布门禁](07-evaluation-operations.md)
9. [模板与检查清单](08-templates-and-checklists.md)

## 相关层

- 资源：[Evaluation 资源索引](../../90-Sources/source-notes/Evaluation-Resources.md)
- 实验：[Evaluation Labs](../../50-Labs/evaluation/README.md)
- 工程：[Eval Harness Python](../../60-Code/eval-harness-python/README.md)
- 模式：[Evaluation Patterns](../../30-Patterns/evaluation/README.md)

## 当前证据边界

- 旧长文中的口语化表达、重复段落、虚构团队案例和无来源成本数字已删除。
- 术语与方法已按一手资料重新组织。
- Schema 和发布门禁是设计模板，不是运行结果。
- `50-Labs/evaluation/` 与 `60-Code/eval-harness-python/` 仍为占位，因此模块状态保持 `draft`。
