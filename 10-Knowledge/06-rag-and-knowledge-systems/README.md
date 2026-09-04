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
6. [实验入口](04-labs/README.md)与[Python 工程骨架](05-code/rag-pipeline-python/README.md)：后续建立数据和实现闭环。

## 待补主题

Parsing/OCR、Chunking、Metadata、Embedding、索引更新、Query Rewrite、Parent-child Retrieval、Citation Grounding、GraphRAG、多模态 RAG、知识新鲜度和安全。

## 当前证据边界

- 案例参数是待实验的候选配置，不是本仓实测结论。
- Lab 与代码仍为占位；没有数据集、任务和基线前不报告效果提升。
