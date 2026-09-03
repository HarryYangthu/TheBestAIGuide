# Evaluation 与 Observability 知识地图

> 状态：draft
> 主线：用可复现任务和可观察证据判断 Agent 系统是否正确、稳定、高效且安全。

## 评测闭环

```text
Requirements + Incidents
        ↓
Task / Dataset / Fixture
        ↓
System Under Test + Evaluation Harness
        ↓
Trials ──> Trajectory + Outcome
        ↓
Graders + Statistics + Failure Attribution
        ↓
Regression / Release Gate / Production Monitoring
        └──────────────────────────────> 新任务
```

## 当前专题

| 主题 | 内容入口 |
| --- | --- |
| 总览 | [Agent Evaluation](../20-Knowledge/10-evaluation-observability/Evaluation.md) |
| 评测对象 | [Task、Trial、Trajectory、Outcome、Harness](../20-Knowledge/10-evaluation-observability/01-evaluation-model.md) |
| 数据集 | [任务、数据集与多次试验](../20-Knowledge/10-evaluation-observability/02-tasks-datasets-and-trials.md) |
| 评分器 | [确定性、模型、人工与组合计分](../20-Knowledge/10-evaluation-observability/03-graders-and-scoring.md) |
| 统计 | [pass@k、稳定性、区间与配对比较](../20-Knowledge/10-evaluation-observability/04-statistics-and-reliability.md) |
| 可观测性 | [Trace、Outcome Snapshot 与失败归因](../20-Knowledge/10-evaluation-observability/05-traces-and-failure-analysis.md) |
| Multi-Agent | [路由、交接、共享状态、协作与成本](../20-Knowledge/10-evaluation-observability/Multi-Agent-Evaluation-Guide.md) |
| 运营 | [套件维护、发布门禁与生产反馈](../20-Knowledge/10-evaluation-observability/07-evaluation-operations.md) |
| 模板 | [Task、Trial、Grader、报告与检查清单](../20-Knowledge/10-evaluation-observability/08-templates-and-checklists.md) |

## 关键区分

- 模型评测 vs Agent 系统评测；
- Transcript 声称成功 vs Outcome 真实完成；
- Capability Eval vs Regression Eval；
- 离线 Eval vs 线上监控和 A/B；
- 确定性测试 vs Model Judge vs Human Review；
- 单次成功 vs 多 Trial 可靠性；
- 产品回归 vs 基础设施噪声 vs Grader 错误。

## 依赖关系

- Context 与 RAG Eval：[Context 评测](../20-Knowledge/04-context-engineering/05-context-evaluation.md)、[RAG 流程](../20-Knowledge/06-rag-and-knowledge-systems/01-rag-pipeline.md)
- Runtime 和回放：[Runtime 与 Harness](../20-Knowledge/09-runtime-harness-environment/README.md)
- 安全门禁：[Safety 与 Governance](../20-Knowledge/11-safety-security-governance/README.md)
- 来源：[Evaluation 资源索引](../90-Sources/source-notes/Evaluation-Resources.md)

## 当前边界

知识笔记已完成结构重写，但 `50-Labs/evaluation/` 和 `60-Code/eval-harness-python/` 仍为占位。当前没有本仓 Eval 结果，不应把模板或示例阈值当作基准。
