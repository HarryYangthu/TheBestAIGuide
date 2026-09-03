# RAG 端到端流程

> 状态：draft

## 定义

Retrieval-Augmented Generation（RAG）在生成前从外部知识源取得证据，并把可追溯的证据交给模型。RAG 的价值不只在“搜到相似文本”，而在于建立从知识版本到最终主张的证据链。

```text
Sources
  -> Parse / Normalize
  -> Segment / Enrich Metadata
  -> Index / Version

User Query
  -> Understand / Rewrite / Filter
  -> Retrieve Candidates
  -> Fuse / Rerank / Deduplicate
  -> Context Pack
  -> Generate or Abstain
  -> Cite / Verify / Observe
```

## 离线知识链路

### 1. Source Registry

每个来源记录：

- 稳定 `source_id`；
- 所有者与访问范围；
- 版本、生效和失效时间；
- 内容类型与解析器版本；
- 更新、删除和保留策略；
- 原始位置与校验值。

没有来源注册表，就难以处理文档更新、引用失效和数据删除。

### 2. Parse 与 Normalize

PDF、网页、Word、数据库和代码需要不同解析器。统一中间表示应保留：

- 标题与层级；
- 表格、列表、代码块和图片说明；
- 页码、段落或字符位置；
- 原始文件和解析版本；
- 无法解析或 OCR 低置信区域。

解析失败不能静默生成空文档。

### 3. Chunking

Chunk 是检索单元，不一定等于展示段落。选择边界时同时考虑：

- 语义或任务是否完整；
- 单个事实是否能独立解释；
- 标题和父级上下文是否保留；
- 过长会降低检索粒度，过短会丢失条件；
- 表格、故障步骤和代码不可机械切断。

Chunk 长度没有普适最优值，需要针对语料、查询和模型评测。

### 4. Metadata

典型字段：

```json
{
  "chunk_id": "manual-001#section-3.2#chunk-01",
  "source_id": "manual-001",
  "source_version": "2.3",
  "title_path": ["维护手册", "告警处理", "风扇告警"],
  "valid_from": "...",
  "valid_to": null,
  "product_models": ["example-model"],
  "fault_codes": ["EXAMPLE-001"],
  "acl": ["operations"],
  "content_hash": "..."
}
```

字段和值只是示例。Metadata 同时服务过滤、精确匹配、权限、新鲜度、引用和删除。

### 5. Index 与版本

索引可以包含向量、倒排、`keyword`、图或结构化数据库。必须明确：

- 文档版本如何替换；
- 旧 Chunk 和向量如何删除；
- Embedding、分词器和索引配置如何版本化；
- 增量更新期间如何避免新旧内容混用；
- 索引能否由事实源重建。

## 在线查询链路

### 1. Query Understanding

识别意图、实体、时间、产品、语言和精确编码。Query 改写不能丢失型号、故障码、数字和否定条件，改写结果要与原始 Query 一起保留。

### 2. Candidate Retrieval

不同通道解决不同召回问题：

- Dense：自然语言、同义表达和语义接近；
- Sparse/BM25：关键词和术语匹配；
- Exact/structured：标识符、版本、权限和枚举字段；
- Graph/relational：明确关系和多跳依赖。

### 3. Fusion 与 Rerank

先合并候选、去重，再用分数融合或排名融合。Reranker 对较小候选集做更精细的 Query—Passage 判断。融合和重排不能替代权限与版本过滤。

### 4. Context Packing

把证据按相关性、来源、覆盖和冲突组织进模型输入：

- 保留引用标识和位置；
- 合并重复片段；
- 避免同一来源挤占全部窗口；
- 显式呈现冲突版本；
- 为回答和工具往返预留 Token。

### 5. Generate、Cite 或 Abstain

模型应区分：

- 来源直接支持的事实；
- 基于多条证据的推断；
- 资料不足、冲突或过期时无法回答的部分。

引用必须指向真正支持主张的原文位置，而不是仅列出检索到的文档。

## 评测分层

| 层 | 典型问题 | 典型指标 |
| --- | --- | --- |
| Parsing | 内容和结构是否正确提取 | 字段准确率、结构保留、失败率 |
| Retrieval | 必要证据是否进入候选 | Recall@k、MRR、nDCG、过滤正确性 |
| Rerank | 相关证据是否排到前面 | nDCG、MRR、Top-k Recall |
| Context | 证据是否被正确选择和组织 | Evidence precision/recall、冲突覆盖 |
| Generation | 主张是否正确且被证据支持 | 正确性、Groundedness、引用精度 |
| System | 是否稳定、及时且成本可控 | 任务成功、多 Trial、延迟、成本、错误率 |

不能只评最终回答，否则很难区分“没检索到”和“检索到了但没用对”。

## 失败模式

- 解析丢失表格、标题或页码；
- Chunk 切断条件和结论；
- 向量召回混淆相似编码；
- 关键词检索无法覆盖口语化同义表达；
- Query 改写删除关键实体；
- 旧版本和新版本同时进入上下文；
- Reranker 偏好表面相关但不支持结论的片段；
- 引用指向相关文档，却不支持具体主张；
- 没有证据时仍生成确定答案；
- ACL 只在生成后检查，导致未授权内容已进入模型。

## 来源

- [Lewis et al.: Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
- [Elasticsearch: Reciprocal rank fusion](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)

下一步：[混合检索与重排](02-hybrid-retrieval-and-reranking.md)。
