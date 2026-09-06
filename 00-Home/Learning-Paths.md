# 连续学习路线

> 状态：draft
> 原则：先理解模型和最小 Agent，再学习信息、行动、编排、验证与生产系统。

## 如何阅读一个知识领域

先读领域 README，再进入概念和模式。用案例理解取舍，在 Notebook 中修改输入，最后去源码查执行过程。

每次学习至少回答三个问题：它实际做了什么？在什么条件下会错？对应代码在哪里？

## 完整主线

1. [AI 基础](../10-Knowledge/01-ai-foundations/README.md)：数学、机器学习、深度学习、搜索、规划和强化学习。
2. [基础模型](../10-Knowledge/02-foundation-models/README.md)：Tokenization、Transformer、训练、对齐、推理和模型选择。
3. [Agent Core](../10-Knowledge/03-agent-core/README.md)：目标、观察、状态、动作、循环和终止条件。
4. [Context Engineering](../10-Knowledge/04-context-engineering/README.md)：为每次模型决策选择、压缩和组织信息。
5. [Tools、Skills 与协议](../10-Knowledge/05-tools-skills-protocols/README.md)：表达、校验和执行动作。
6. [RAG 与知识系统](../10-Knowledge/06-rag-and-knowledge-systems/README.md)：接入外部知识并保留证据链。
7. [State 与 Memory](../10-Knowledge/07-state-and-memory/README.md)：先理解当前权威状态与 Checkpoint，再学习跨轮次记忆。
8. [Planning、Workflow 与 Multi-Agent](../10-Knowledge/08-planning-workflow-multi-agent/README.md)：分解、路由、交接和合并任务。
9. [Runtime、Harness 与 Environment](../10-Knowledge/09-runtime-harness-environment/README.md)：管理执行、重试、恢复、权限和环境副作用。
10. [Evaluation 与 Observability](../10-Knowledge/10-evaluation-observability/README.md)：用任务、结果、轨迹、评分器和统计判断系统表现。
11. [Safety、Security 与 Governance](../10-Knowledge/11-safety-security-governance/README.md)：约束身份、数据、权限和危险动作。
12. [Agent Learning](../10-Knowledge/12-agent-learning/README.md)：利用轨迹、反馈和验证器改进系统。
13. [应用工程](../10-Knowledge/13-application-engineering/README.md)与[生产工程](../10-Knowledge/14-production-engineering/README.md)：把能力接入产品并可靠运行。
14. [多模态与具身智能](../10-Knowledge/15-multimodal-and-embodied/README.md)及[研究前沿](../10-Knowledge/16-research-frontiers/README.md)：在核心闭环之后扩展。

前两层已补齐原入口的 13 篇基础教程。数学基础薄弱时从 AI 基础开始；已有模型基础时可以直接进入 Agent Loop。

## 三种起点

| 起点 | 推荐阅读和实验 | 学完应能做什么 |
| --- | --- | --- |
| 数学与模型 | AI 基础 → Attention → 解码/缓存实验 | 解释核心公式并读懂中间张量 |
| 系统设计 | Agent Loop → Context/RAG → Tools/Memory → Runtime | 做出有限步数、可拒答、可恢复的程序 |
| 已有项目 | Evaluation → Safety → 生产工程 → 综合案例 | 找出失败位置，并用回归任务验证修改 |

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

## 如何使用配套实验

先阅读 Notebook 的问题和预期现象，再执行代码，最后改变一个参数：例如 Attention 的维度、Context 预算、检索查询或记忆有效期。不要一次改多个条件，否则很难解释结果为什么变了。

[统一运行说明](../scripts/README.md)提供依赖安装、Python/TypeScript 测试和 Notebook 执行命令。[综合项目](../20-Projects/domain-research-agent/README.md)把多个领域的真实源码连起来，可以作为第二轮阅读的入口。

## 证据边界

正文、源码测试、Notebook 和外部系统复现分别记状态。本地小实验可检验机制和边界，不能直接推出真实 LLM、真实用户流量或生产环境的效果。具体已执行范围见[建设状态](Knowledge-Status.md)。
