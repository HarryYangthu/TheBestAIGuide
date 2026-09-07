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

## Dense 与 Cross-encoder 差在哪一步

Dense 检索先将查询编码成向量 $q\in\mathbb R^m$，将各文档编码成 $d_i\in\mathbb R^m$，再用点积或余弦比较它们。若文档向量逐行放入 $D\in\mathbb R^{n\times m}$，则 $Dq\in\mathbb R^n$ 给出 $n$ 个文档的点积分数。文档向量可提前保存，每次查询只需编码查询并搜索这些向量，所以适合先从大语料找候选。

例如归一化后的 $q=(1,0)$，$d_1=(0.8,0.6)$，$d_2=(0,1)$，分数分别为 0.8 和 0。这里是人为向量，用于看懂计算，不是模型实际输出。模型学习的是文本到向量的映射；这并不保证相似编号、否定句或本行业术语一定被正确区分。余弦值也不是“答案正确概率”。

Cross-encoder 把“查询 + 一篇候选文本”一起交给模型计算分数，使两段文本在编码时就能交互。换一个查询，同一篇文档也要重新参与计算，不能只复用一个预存文档向量完成评分，因此通常先召回再重排。两者也可能都使用 Transformer；区别是**先独立编码再比较，还是成对共同编码后评分**。实现入口见 [Sentence Transformers bi-encoder](https://sbert.net/docs/sentence_transformer/usage/usage.html) 与 [cross-encoder](https://sbert.net/docs/cross_encoder/usage/usage.html)。

重排不能补回候选池中不存在的证据。例如召回只保留前 10 篇，正确证据却排在第 11 篇，无论怎么重排这 10 篇也找不回来。先用 Recall@M 检查候选池是否包含证据，再用 MRR/nDCG@k 检查最终前 $k$ 篇排得怎样；这里通常 $M\ge k$。

## BM25 到底在算什么

BM25 把查询中的词逐个打分后相加：稀有词区分力更强，重复出现的词有帮助但收益逐渐饱和，长文档则避免只因字数多而占便宜。本仓采用正值 IDF 的常见形式：

$$
\mathrm{BM25}(q,d)=\sum_{t\in q}\log\left(1+\frac{N-df_t+0.5}{df_t+0.5}\right)
\frac{tf_{t,d}(k_1+1)}{tf_{t,d}+k_1(1-b+b|d|/\overline{dl})}.
$$

查询里的重复词在本实现中只计一次，即求和遍历去重后的词集合。$N$ 为参与检索的文档数，$df_t$ 为含词 $t$ 的文档数，$tf_{t,d}$ 为词频，$|d|$ 与 $\overline{dl}$ 为本篇和平均文档长度，均按同一分词器计数。$k_1>0$ 控制词频饱和，$b\in[0,1]$ 控制长度归一化。不同实现的 IDF 变体可能不同，不应期待所有搜索引擎输出完全相同的分数。[BM25 原论文综述](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)给出其概率检索背景。

手算一个词：设 $N=3,df=1,tf=2,|d|=\overline{dl},k_1=1.2,b=0.75$。IDF 为 $\ln(1+2.5/1.5)\approx0.9808$，词频项为 $2\times2.2/(2+1.2)=1.375$，贡献约 $1.3486$。词频从 2 增到 4，贡献不会翻倍，因为分母也在增加。完整函数见 [bm25](../05-code/rag-pipeline-python/src/rag_pipeline/retrieval.py)。

在 `Index.search` 中，传给 BM25 的“文档”实际是权限、产品、版本、编号过滤后的候选块，所以 $N$、文档频率和平均长度也在这个子集内计算。换一个候选范围，分数可能改变；它们不适合直接跨查询比较。

本仓英文按词/完整编码、中文按单字分词，这是方便阅读的基线。中文同字但不同义的片段会造成噪声，不能据此评价生产搜索引擎的中文分析器。

## 候选融合

### 分数归一化与加权

```text
score = alpha * normalized_dense
      + beta  * normalized_sparse
      + gamma * exact_match_bonus
```

优点是可表达业务偏好；风险是不同分数分布随查询、索引和模型变化，简单 min-max 归一化容易不稳定。`alpha/beta/gamma` 必须通过验证集校准。

### Reciprocal Rank Fusion：融合排名支持度

定义 $\mathrm{RRF}(d)=\sum_{i:d\in L_i}1/(c+r_i(d))$，其中 $L_i$ 是第 $i$ 路排名列表，$r_i(d)$ 从 1 开始计数，$c\ge0$ 是平滑常数；不在某一路出现的文档在该路贡献 0。它只用名次，不要求不同通道的原始分数同量纲。

把两个通道排名写成 A=`[a,b]`、B=`[b,c]`，平滑常数设 60。a 只在 A 第 1 位，得 $1/61\approx0.01639$；b 在 A 第 2 位、B 第 1 位，得 $1/62+1/61\approx0.03252$；c 得 $1/62\approx0.01613$。因此 b 排第一。它综合的是排名支持度，没有把 BM25 2.3 和 cosine 0.8 当同一种分数相加。

缺席的文档贡献为 0；同一通道重复返回同一块只能算一次。常数越大，同一路前后名次差距越平缓；它不是 top-k。实现：[ranking.py](../05-code/rag-pipeline-python/src/rag_pipeline/ranking.py)。这不能覆盖精确编号的硬要求，所以本仓先过滤编号再融合。


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

## Recall、MRR、nDCG 各看一件事

假设 gold 有两篇：good 的等级 2，okay 的等级 1；返回 `[bad, good, okay]`。Recall@3 为 2/2=1，本题的 RR@3 为第一个相关项排名的倒数 1/2。定义增益 $g(rel)=2^{rel}-1$，则：

$$
DCG@k=\sum_{r=1}^{k}\frac{2^{rel_r}-1}{\log_2(r+1)},\qquad
nDCG@k=\frac{DCG@k}{IDCG@k}.
$$

$r$ 是从 1 开始的排名，$rel_r$ 是该位置的人工相关性等级，$IDCG$ 是把全部已知相关项按等级从高到低排列后取前 $k$ 项所得的 DCG；需要在同一标注集和同一增益定义下比较。MRR 是逐查询倒数排名的平均值，本例单条查询先得到 RR=1/2。

当前 DCG 为 $3/\log_2 3+1/\log_2 4\approx2.3928$，理想顺序 `[good,okay,bad]` 的 IDCG 为 $3+1/\log_2 3\approx3.6309$，nDCG 为约 0.6590。它指出“都找到了，但重要证据没排在最前”。无相关证据的查询分母为零，单独计拒答，不能强设 nDCG=1。

公式与数值都在 [Notebook](../04-labs/01-hybrid-retrieval-evaluation.ipynb)实际运行。实验按文档 ID 去重，5 条可回答查询中跨语言查询失败，BM25 与 hybrid 的平均 Recall@3 都为 0.8；这不构成 hybrid 优于 BM25 的证据。

## 一个已运行的反例：融合可能把正确证据排低

[Learning Workbench 的 24 条检索结果](../../../20-Projects/learning-workbench/artifacts/real-models/retrieval.json)使用同一组 6 道英文构造题比较四种模式。看 q3 `The internet connection stopped working.`，正确证据是 `network`：

| 模式 | 返回前三名 | Recall@3 | 首个相关结果倒数排名 |
| --- | --- | --- | --- |
| BM25 | memory、fan-v1、rain | 0 | 0 |
| Dense | network、fan-v1、fan-v2 | 1 | 1 |
| Hybrid | fan-v1、memory、network | 1 | 1/3 |
| Hybrid + rerank | network、battery、memory | 1 | 1 |

这道题展示了两种不同错误：BM25 没有召回正确文档；融合召回了，却把 Dense 原本排第一的证据挤到第三。最后重排改善了位置。不能由此说 Hybrid 总优于 Dense，也不能用本组英文题与本域另一组中文题的 0.8 直接比较。逐题看排名，比只报一个平均分更容易定位下一步要改哪里。

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

相关模式：[Hybrid Retrieval](../02-patterns/hybrid-retrieval.md)。
