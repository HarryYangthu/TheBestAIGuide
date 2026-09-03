# 开始阅读

> 状态：draft

这个仓库把内容分为四层：知识结论、可复用模式、系统案例、可执行实验/工程。阅读时先看知识地图，再沿链接进入正文；不要把案例参数、Notebook 占位或代码骨架当成已验证结论。

## 完整知识顺序

1. [AI 基础](../10-Maps/01-AI-Foundations-Map.md)：数学、机器学习、深度学习、搜索和强化学习。
2. [基础模型](../10-Maps/02-Foundation-Models-Map.md)：Tokenizer、Transformer、训练、对齐与推理。
3. [Agent 系统](../10-Maps/03-Agent-Systems-Map.md)：Loop、Context、Tools、RAG、Memory 和 Workflow。
4. [Runtime 与 Harness](../10-Maps/06-Runtime-Harness-Map.md)：执行、状态、恢复、环境和可靠性。
5. [Evaluation 与 Observability](../10-Maps/07-Evaluation-Observability-Map.md)：任务、Trial、Grader、Trace、统计和发布门禁。
6. [Safety 与 Governance](../10-Maps/08-Safety-Governance-Map.md)：权限、沙箱、数据和风险治理。

AI 基础与基础模型目前主要是目录和待补范围，还不是完整教材。

## 现在可直接阅读

### Context 主线

1. [Context Engineering 总览](../20-Knowledge/04-context-engineering/Context-Engineering.md)
2. [上下文模型](../20-Knowledge/04-context-engineering/01-context-model.md)
3. [Context Builder](../20-Knowledge/04-context-engineering/02-context-builder.md)
4. [失败模式与优化策略](../20-Knowledge/04-context-engineering/03-failure-modes.md)
5. [上下文评测](../20-Knowledge/04-context-engineering/05-context-evaluation.md)

### RAG 主线

1. [RAG 端到端流程](../20-Knowledge/06-rag-and-knowledge-systems/01-rag-pipeline.md)
2. [混合检索与重排](../20-Knowledge/06-rag-and-knowledge-systems/02-hybrid-retrieval-and-reranking.md)
3. [Hybrid Retrieval 模式](../30-Patterns/rag/hybrid-retrieval.md)
4. [运维 RAG 案例](../40-Cases/rag-systems/运维领域-RAG-问答系统.md)

### Evaluation 主线

1. [Agent Evaluation 总览](../20-Knowledge/10-evaluation-observability/Evaluation.md)
2. [评测对象与数据集](../20-Knowledge/10-evaluation-observability/01-evaluation-model.md)
3. [评分器与统计](../20-Knowledge/10-evaluation-observability/03-graders-and-scoring.md)
4. [Trace 与失败归因](../20-Knowledge/10-evaluation-observability/05-traces-and-failure-analysis.md)
5. [Multi-Agent 评测](../20-Knowledge/10-evaluation-observability/Multi-Agent-Evaluation-Guide.md)
6. [模板与检查清单](../20-Knowledge/10-evaluation-observability/08-templates-and-checklists.md)

## 案例入口

- [AgentGuide 仓库走读](../40-Cases/external-repositories/AgentGuide/repository-walkthrough.md)：区分知识内容、站点代码、派生数据和可运行 Agent。
- [运维 RAG 案例](../40-Cases/rag-systems/README.md)：把通用 RAG 原理放回领域约束中检查。

## 当前不应执行的入口

[Labs](../50-Labs/README.md) 和 [Code](../60-Code/README.md) 当前主要是规划骨架。只有状态升级为 `verified` 且附运行记录后，才可作为可复现实验或可复用工程使用。

建设优先级见[待补充计划](待补充计划.md)，覆盖状态见[知识库建设状态](Knowledge-Status.md)。
