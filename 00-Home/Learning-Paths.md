# 连续学习路线

> 状态：draft
> 原则：先理解模型和最小 Agent，再学习信息、行动、编排、验证与生产系统。

## 如何阅读一个知识领域

```text
领域 README
    ↓
Concepts：理解概念和机制
    ↓
Patterns：学习可复用设计方法
    ↓
Cases：观察真实约束下的选择
    ↓
Labs：运行实验验证关键结论
    ↓
Code：阅读或实现可测试代码
```

如果某一阶段尚无内容，领域 README 会明确标记缺口，不用进入空目录寻找。

## 完整主线

1. [AI 基础](../10-Knowledge/01-ai-foundations/README.md)：数学、机器学习、深度学习、搜索、规划和强化学习。
2. [基础模型](../10-Knowledge/02-foundation-models/README.md)：Tokenization、Transformer、训练、对齐、推理和模型选择。
3. [Agent Core](../10-Knowledge/03-agent-core/README.md)：目标、观察、状态、动作、循环和终止条件。
4. [Context Engineering](../10-Knowledge/04-context-engineering/README.md)：为每次模型决策选择、压缩和组织信息。
5. [Tools、Skills 与协议](../10-Knowledge/05-tools-skills-protocols/README.md)：表达、校验和执行动作。
6. [RAG 与知识系统](../10-Knowledge/06-rag-and-knowledge-systems/README.md)：接入外部知识并保留证据链。
7. [Memory 与 State](../10-Knowledge/07-memory-and-state/README.md)：区分当前权威状态与跨轮次记忆。
8. [Planning、Workflow 与 Multi-Agent](../10-Knowledge/08-planning-workflow-multi-agent/README.md)：分解、路由、交接和合并任务。
9. [Runtime、Harness 与 Environment](../10-Knowledge/09-runtime-harness-environment/README.md)：管理执行、重试、恢复、权限和环境副作用。
10. [Evaluation 与 Observability](../10-Knowledge/10-evaluation-observability/README.md)：用任务、结果、轨迹、评分器和统计判断系统表现。
11. [Safety、Security 与 Governance](../10-Knowledge/11-safety-security-governance/README.md)：约束身份、数据、权限和危险动作。
12. [Agent Learning](../10-Knowledge/12-agent-learning/README.md)：利用轨迹、反馈和验证器改进系统。
13. [应用工程](../10-Knowledge/13-application-engineering/README.md)与[生产工程](../10-Knowledge/14-production-engineering/README.md)：把能力接入产品并可靠运行。
14. [多模态与具身智能](../10-Knowledge/15-multimodal-and-embodied/README.md)及[研究前沿](../10-Knowledge/16-research-frontiers/README.md)：在核心闭环之后扩展。

前两层目前主要是范围和占位，适合用于确认前置知识，但还不是完整教材。

## 当前可直接阅读：Context Engineering

1. [主题总览](../10-Knowledge/04-context-engineering/01-concepts/00-overview.md)
2. [上下文模型](../10-Knowledge/04-context-engineering/01-concepts/01-context-model.md)
3. [上下文失败模式](../10-Knowledge/04-context-engineering/01-concepts/02-failure-modes.md)
4. [Context Builder](../10-Knowledge/04-context-engineering/02-patterns/01-context-builder.md)
5. [上下文优化策略](../10-Knowledge/04-context-engineering/02-patterns/02-optimization-strategies.md)
6. [上下文评测](../10-Knowledge/04-context-engineering/01-concepts/03-context-evaluation.md)
7. [配套实验](../10-Knowledge/04-context-engineering/04-labs/README.md)

## 当前可直接阅读：RAG

1. [RAG 端到端流程](../10-Knowledge/06-rag-and-knowledge-systems/01-concepts/01-rag-pipeline.md)
2. [混合检索与重排机制](../10-Knowledge/06-rag-and-knowledge-systems/01-concepts/02-hybrid-retrieval-and-reranking.md)
3. [Hybrid Retrieval 模式](../10-Knowledge/06-rag-and-knowledge-systems/02-patterns/hybrid-retrieval.md)
4. [运维领域 RAG 案例](../10-Knowledge/06-rag-and-knowledge-systems/03-cases/运维领域-RAG-问答系统.md)
5. [双索引设计决策](../10-Knowledge/06-rag-and-knowledge-systems/03-cases/运维RAG-双索引检索设计.md)
6. [实验入口](../10-Knowledge/06-rag-and-knowledge-systems/04-labs/README.md)与[代码入口](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/README.md)

## 当前可直接阅读：Evaluation

1. [Agent Evaluation 总览](../10-Knowledge/10-evaluation-observability/01-concepts/00-overview.md)
2. [评测对象与系统模型](../10-Knowledge/10-evaluation-observability/01-concepts/01-evaluation-model.md)
3. [任务、数据集与多次试验](../10-Knowledge/10-evaluation-observability/01-concepts/02-tasks-datasets-and-trials.md)
4. [评分器与组合计分](../10-Knowledge/10-evaluation-observability/01-concepts/03-graders-and-scoring.md)
5. [统计与可靠性](../10-Knowledge/10-evaluation-observability/01-concepts/04-statistics-and-reliability.md)
6. [Trace 与失败归因](../10-Knowledge/10-evaluation-observability/01-concepts/05-traces-and-failure-analysis.md)
7. [Multi-Agent 系统评测](../10-Knowledge/10-evaluation-observability/01-concepts/06-multi-agent-evaluation.md)
8. [评测运营](../10-Knowledge/10-evaluation-observability/02-patterns/01-evaluation-operations.md)和[模板清单](../10-Knowledge/10-evaluation-observability/02-patterns/02-templates-and-checklists.md)

## 当前证据边界

- Context、RAG 和 Evaluation 已有可阅读正文。
- Context Notebook、RAG Pipeline、Agent Loop 和 Eval Harness 仍是未验证骨架。
- 只有实际运行并记录环境、输入、输出和结果后，实验或代码才能标记为 `verified`。
