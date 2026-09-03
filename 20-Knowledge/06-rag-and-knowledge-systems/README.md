# RAG and Knowledge Systems

> 状态：draft
> 已从运维案例中提炼通用知识；尚未完成本仓实验和工程验证。

## 当前内容

1. [RAG 端到端流程](01-rag-pipeline.md)：从知识接入到带证据回答的完整链路。
2. [混合检索与重排](02-hybrid-retrieval-and-reranking.md)：Dense、Sparse、精确字段、融合和 Rerank。
3. [Hybrid Retrieval 模式](../../30-Patterns/rag/hybrid-retrieval.md)：可复用的设计决策卡。
4. [运维 RAG 系统案例](../../40-Cases/rag-systems/运维领域-RAG-问答系统.md)：领域设计与验证缺口。
5. [运维双索引决策记录](../../40-Cases/rag-systems/运维RAG-双索引检索设计.md)：为何同时使用语义和词法通道。

## 待补主题

Parsing/OCR、Chunking、Metadata、Embedding、索引更新、Query Rewrite、Parent-child Retrieval、Citation Grounding、GraphRAG、多模态 RAG、知识新鲜度和安全。

## 证据边界

- 案例中的模型、Chunk 长度、候选数和融合权重是待实验的候选配置，不是本仓实测结论。
- [RAG Labs](../../50-Labs/rag/README.md) 和 [RAG Pipeline Python](../../60-Code/rag-pipeline-python/README.md) 仍是占位。
- 在数据集、任务、基线和指标完成前，不报告“提升百分比”或“最优配置”。
