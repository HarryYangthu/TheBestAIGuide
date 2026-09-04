# 运维 RAG 双索引检索设计

> 状态：draft / architecture decision
> 决策：同时使用语义检索与词法/精确字段检索，并在候选层融合。

## 背景

运维 Query 往往同时包含两类信息：

- “风扇异常怎么处理”这类自然语言现象；
- `S5735`、`ALM-12003`、`0x...`、接口名或命令这类精确标识。

Dense Retrieval 能连接不同说法，Embedding 却可能把相似编号视为相近；BM25 和精确字段能保护标识符，却可能漏掉口语化表达。因此单一通道无法同时覆盖两类需求。

## 决策

```text
Query
  -> Identifier Extractor
  -> Scope / ACL / Version Filter
  ├─> Dense Retrieval
  ├─> BM25 Retrieval
  └─> Exact Field Lookup
           │
           ▼
   Union + Deduplicate
           │
           ▼
 Fusion / Query-aware Routing
           │
           ▼
        Rerank
           │
           ▼
  Version/Conflict Check
```

这里沿用“双索引”名称，但实现上实际包含三种信号：向量、BM25 文本和 `keyword` 精确字段。BM25 是词法相关性算法，不等同于精确匹配。

## 索引字段

```json
{
  "mappings": {
    "properties": {
      "chunk_id": {"type": "keyword"},
      "source_id": {"type": "keyword"},
      "source_version": {"type": "keyword"},
      "text": {"type": "text"},
      "product_models": {"type": "keyword"},
      "fault_codes": {"type": "keyword"},
      "commands": {"type": "keyword"},
      "active": {"type": "boolean"},
      "valid_from": {"type": "date"},
      "valid_to": {"type": "date"},
      "embedding": {"type": "dense_vector"}
    }
  }
}
```

这是逻辑 Schema 示例。实际映射取决于搜索引擎版本、语言分析器、向量维度和索引策略。

## 查询处理

### 保护精确实体

对故障码、型号和命令使用规则、词典或结构化解析，保存：

```json
{
  "raw": "alm 12003",
  "normalized": "ALM-12003",
  "type": "fault_code",
  "confidence": 0.96,
  "method": "regex+dictionary"
}
```

数值只是格式示例。规范化过程必须可审计，并为低置信结果保留原字符串。

### BM25 与 Exact 的分工

- `match`/BM25：匹配“风扇告警 处理步骤”等分词后的术语。
- `term`/keyword：精确匹配 `ALM-12003`、`S5735` 和版本。
- filter：执行 ACL、有效状态、产品和时间范围约束。

精确字段命中可以作为硬过滤或排序加成，取决于任务。例如明确给出故障码时，召回其他代码通常应作为硬负例；型号不明确时，可能需要返回多个适用范围供确认。

## 融合选择

### 方案 A：归一化加权

```text
score = alpha * dense_score
      + beta  * sparse_score
      + gamma * exact_bonus
```

适合需要表达领域权重的系统，但必须在验证集上校准分数分布。原方案的 `0.3/0.7` 只作为待验证假设。

### 方案 B：RRF

按各通道排名融合，避免直接比较不同量纲的分数。实现稳健，但精确故障码这种硬要求仍需单独规则。

### 方案 C：Query-aware Routing

根据 Query 类型选择通道和候选预算。路由器本身需要标注集、回退策略和 Trace。

初版可以从“并行召回 + RRF + 精确命中规则”开始，待数据足够后再训练或引入复杂路由。这是实施建议，不是已验证最优方案。

## Rerank

Reranker 输入 Query 与候选 Chunk，对候选集重新排序。应把标题、版本、型号等必要信息一起提供，并记录：

- Reranker 模型和版本；
- 输入截断方式；
- 候选数与返回数；
- 分数是否可跨 Query 比较；
- 失败和超时的回退顺序。

Rerank 解决候选排序，不解决 ACL、错误版本和来源权威性。

## 备选方案

| 方案 | 结论 | 原因 |
| --- | --- | --- |
| 仅 Dense | 不采用为默认 | 对相似编号和精确版本风险高 |
| 仅 BM25/keyword | 不采用为默认 | 难覆盖口语、同义词和现象描述 |
| 直接让生成模型从全部文档选择 | 不采用 | 成本、窗口、权限和可追溯性不可控 |
| 单一混合分数且无 Trace | 不采用 | 难以解释和校准通道贡献 |

## 结果与代价

预期收益：提高语义表达和精确标识的联合覆盖，并能针对 Query 类型调整策略。

新增代价：维护多路索引和同步、融合校准、Rerank 延迟、更多 Trace 字段以及更复杂的评测集。

## 验证标准

- 标注集覆盖精确编码、口语表达、版本冲突和无答案 Query；
- Dense only、Sparse/Exact only、Union、Fusion、Rerank 逐层消融；
- 单独报告精确代码硬负例；
- 检查 Recall@k、MRR/nDCG、端到端 Groundedness、延迟和成本；
- 多 Trial 检查 Query Rewrite、路由和生成的波动；
- 验证文档更新、删除、ACL 与过期版本不会泄露。

当前仓库没有这些实验结果，因此该决策保持 `draft`。

通用原理见[混合检索与重排](../01-concepts/02-hybrid-retrieval-and-reranking.md)，完整案例见[运维领域 RAG 问答系统](运维领域-RAG-问答系统.md)。
