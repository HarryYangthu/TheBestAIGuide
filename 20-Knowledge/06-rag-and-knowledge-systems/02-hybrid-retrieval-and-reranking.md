# 混合检索与重排

> 状态：draft

## 为什么需要多通道

不同信号擅长不同问题：

| 通道 | 擅长 | 典型失败 |
| --- | --- | --- |
| Dense / Vector | 同义表达、语义相近、自然语言描述 | 混淆相似编号，受 Embedding 领域偏差影响 |
| Sparse / BM25 | 关键词、术语、稀有词 | 不理解深层语义和表达变体 |
| Exact / keyword | 型号、故障码、ID、版本 | 只能命中规范化后的精确值 |
| Metadata filter | 权限、时间、产品、语言、状态 | 字段抽取或维护错误会造成漏召回 |

Hybrid Retrieval 的目标不是让所有通道投票，而是覆盖不同失败模式，再用明确规则合并候选。

## 一条推荐链路

```text
Original Query
  -> Entity / Identifier Extraction
  -> ACL + Version + Scope Filter
  -> Dense Retrieval ───────┐
  -> Sparse Retrieval ──────┼─> Union + Deduplicate
  -> Exact Field Lookup ────┘          │
                                       ▼
                              Fusion / Routing
                                       │
                                       ▼
                                  Reranker
                                       │
                                       ▼
                              Diversity + Context Pack
```

权限过滤应尽可能在检索前或检索时执行，不能先把未授权内容取回给模型再过滤答案。

## Query 分析

先从原始 Query 中提取：

- 标识符、型号、错误码和命令；
- 产品、版本、语言和时间范围；
- 否定、比较和范围条件；
- 用户意图与期望结果。

正则、词典和结构化解析适合保护精确实体；模型改写适合补充同义词和标准术语。两者并用时保留原始 Query，避免改写丢失编码。

## 候选融合

### 分数归一化与加权

```text
score = alpha * normalized_dense
      + beta  * normalized_sparse
      + gamma * exact_match_bonus
```

优点是可表达业务偏好；风险是不同分数分布随查询、索引和模型变化，简单 min-max 归一化容易不稳定。`alpha/beta/gamma` 必须通过验证集校准。

### Reciprocal Rank Fusion

RRF 只使用各通道排名，不要求分数同量纲：

```text
RRF(d) = Σ 1 / (k + rank_i(d))
```

这里的 `k` 是平滑常数，不是检索 Top-k。RRF 实现简单、对分数量纲稳健，但不能天然表达精确字段必须命中的硬规则。

### Query Routing

当查询类型明显时，可以调整通道：

- 含规范故障码：Exact 与 Sparse 为主，Dense 补充解释。
- 只有自然语言现象：Dense 与 Sparse 并行。
- 有严格产品和版本：先做 Metadata Filter。
- 需要关系或依赖：进入结构化或图查询。

路由错误会造成系统性漏召回，因此保留安全的回退通道，并单独评测路由。

## 去重与多样性

候选合并后需要处理：

- 同一 Chunk 被多个通道召回；
- 相邻 Chunk 内容高度重叠；
- 同一文档占据所有位置；
- 多个版本互相冲突；
- 父子 Chunk 同时出现但信息重复。

去重不能只看文本相似度，还要利用 `source_id`、位置、版本和父子关系。

## Rerank

Cross-encoder 或模型 Reranker 同时读取 Query 与候选文本，通常比独立 Embedding 相似度提供更细的相关性判断。它适合处理召回后的几十个候选，而不适合直接扫描全部语料。

Rerank 输入应包含必要的标题、产品、版本和来源信息；输出记录模型版本、分数含义和截断策略。

Reranker 仍可能：

- 偏好词面重合；
- 忽略否定和时间条件；
- 将相关性误当作事实支持；
- 因候选过长被截断；
- 在领域外数据上失准。

因此需要人工标注 Query—Evidence 对和端到端任务共同验证。

## 评测

### Retrieval 集

每条 Query 至少标注：

- 必要证据 Chunk 或可接受证据集合；
- 明确的硬负例，特别是相似编码和旧版本；
- 允许的产品、时间和权限范围；
- 查询类型和关键实体。

### 分层消融

依次比较：

1. Dense only；
2. Sparse/Exact only；
3. Union；
4. 加权融合或 RRF；
5. 加 Reranker；
6. 加 Query Routing；
7. 加 Context Packing 和生成。

观察 Recall@k、MRR/nDCG、硬负例误召回、延迟和端到端任务成功。检索指标提升不保证最终回答提升。

## 运维类 Query 示例

```text
S5735 出现 ALM-12003 风扇告警怎么处理？
```

这只是结构示例。系统可以：

1. 从原始 Query 提取型号和故障码。
2. 用 `keyword` 字段做精确查询。
3. 用 Sparse 通道匹配告警术语和处理步骤。
4. 用 Dense 通道覆盖“风扇灯红了”等非标准表达。
5. 合并、去重并 Rerank。
6. 检查版本与产品范围后打包证据。

不能预先假设某个固定权重（例如 `0.3/0.7`）适合所有查询。权重和候选数要在领域数据上验证。

## 来源

- [Robertson and Zaragoza: The Probabilistic Relevance Framework: BM25 and Beyond](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- [Cormack et al.: Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
- [Elasticsearch: Hybrid search](https://www.elastic.co/docs/solutions/search/hybrid-search)

相关模式：[Hybrid Retrieval](../../30-Patterns/rag/hybrid-retrieval.md)。
