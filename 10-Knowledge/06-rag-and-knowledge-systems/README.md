# RAG 与知识系统

> 状态：draft
> 学习目标：理解外部知识如何被接入、检索、筛选并作为可追溯证据进入模型上下文。

## 前置知识

- Embedding、相似度与基础信息检索。
- Context Builder 的来源、信任、选择和预算模型。

## 连续学习顺序

1. [RAG 端到端流程](01-concepts/01-rag-pipeline.md)：从知识接入到带证据回答。
2. [混合检索与重排机制](01-concepts/02-hybrid-retrieval-and-reranking.md)：Dense、Sparse、Exact、融合与 Rerank。
3. [Hybrid Retrieval 模式](02-patterns/hybrid-retrieval.md)：何时组合多路检索以及如何验证。
4. [运维领域 RAG 案例](03-cases/运维领域-RAG-问答系统.md)：把通用机制放回业务约束。
5. [双索引设计决策](03-cases/运维RAG-双索引检索设计.md)：查看具体选择及其未验证假设。
6. [实验入口](04-labs/README.md)与[Python 工程](05-code/rag-pipeline-python/README.md)：读取教学语料、实际运行和评分结果。

## 深入专题

| 入口 | 学习问题 |
| --- | --- |
| [接入与解析](01-concepts/03-ingestion-and-parsing.md) | OCR、表格、阅读顺序怎样影响知识质量 |
| [切块与元数据](01-concepts/04-chunking-and-metadata.md) | 如何保留条件、父子关系和原文位置 |
| [索引生命周期](01-concepts/05-index-lifecycle.md) | 文档/模型版本、更新、删除和权限如何协同 |
| [查询规划与图检索](01-concepts/06-query-planning-and-graph-retrieval.md) | 改写、分解、路由与 GraphRAG 的适用任务 |
| [引用与 Grounding](01-concepts/07-citations-and-grounding.md) | 相关、原文一致和真正支持结论的差别 |
| [来源索引](references.md) | 回到原论文与官方说明核对机制 |

多模态扩展见[多模态知识域](../15-multimodal-and-embodied/README.md)。

## 当前证据边界

- 案例参数是待实验的候选配置，不是本仓实测结论。
- Lab 与代码已完成离线教学链路并保存输出；真实模型、PDF/OCR、图引擎和业务生产效果尚未运行。
