# 索引生命周期：保证查到的是当前有权使用的知识

> 状态：draft
> 资料核验：2026-09-06；单进程替换、删除与过期引用失效已测试，多副本一致性未实现。

“新文档上传成功”不等于“旧知识已不可见”。如果向量库新增了 v2，而倒排索引仍保留 v1，混合检索可能同时返回两个相反操作。真正需要维护的对象是一组相互对应的版本：原文、块、向量、词法索引和引用。

## 区分四种版本

| 版本 | 改变什么 | 必须做的动作 |
| --- | --- | --- |
| 来源版本 | 文档事实和适用范围 | 重新解析受影响块，撤下被替代块 |
| 解析/切块版本 | 文本结构、边界和位置 | 重建块、标注映射与派生索引 |
| Embedding 版本 | 向量空间与维度 | 重新编码文档；查询端切换同一空间 |
| 索引配置版本 | 分词器、距离度量、检索规则 | 回放查询集，确认排序与过滤兼容 |

两个 embedding 模型即使输出维度相同，坐标含义也未必相同。把模型 A 的查询向量与模型 B 的文档向量做点积，程序可以运行，分数却没有可靠意义。模型名、权重 revision、归一化方式、查询/文档前缀应一起记录。

余弦相似度为：

$$
s(q,d)=\frac{q^\top d}{\lVert q\rVert_2\lVert d\rVert_2}.
$$

$q,d\in\mathbb R^m$ 必须来自兼容空间且范数非零。若都已 L2 归一化，余弦就等于点积。例如 $q=(1,0),d=(3,4)$，余弦为 $3/5=0.6$。这表示方向相近程度，不表示有 60% 的概率支持答案。

## 增量更新的最小可靠做法

给每个文档稳定业务 ID，并把租户加入存储键，避免两个租户的 `manual-001` 相互覆盖。内容变化时比较哈希，生成新块；先写候选状态并完成验证，再替换当前可见指针。大系统还要记录失败重试与清理未引用旧块的任务。

本仓内存索引有意只演示其中的单进程部分：

```python
from rag_pipeline import Document, Index

index = Index()
index.upsert(Document("manual", "旧内容", tenant="a", version="1"))
index.upsert(Document("manual", "新内容", tenant="a", version="2"))
assert index.search("旧内容", tenant="a", version="1") == []
index.delete("manual", tenant="a")
assert index.search("新内容", tenant="a") == []
```

`upsert` 先切块，再替换当前文档。这里的替换键是 `(tenant, doc_id)`，所以 v2 会使同 ID 的 v1 不再可查。若业务要比较历史版本，必须另外保留归档记录，或把版本加入存储键并维护“当前版”指针；不能对这个覆盖式索引直接查询已经被替换的 v1。进阶工程的 [compare_versions](../../../20-Projects/learning-workbench/src/learning_workbench/retrieval.py)使用保留版本的证据记录，演示分别取两侧证据再比较。旧版本引用在 `verify_citation` 中失效，不会悄悄指向新原文。完整实现见[retrieval.py](../05-code/rag-pipeline-python/src/rag_pipeline/retrieval.py)和[更新删除测试](../05-code/rag-pipeline-python/tests/test_pipeline.py)。这一实现是内存对象，不具备数据库事务、跨进程原子切换和故障后持久恢复；并发服务应加锁或采用存储事务。

## 删除与撤权不是同一件事

删除通常撤掉某来源及派生物；撤权可能只改变谁能看，文档本身仍保留。生产删除链路要覆盖原文、块、向量、词法索引、缓存、摘要、生成报告以及保留策略允许清理的日志。只删向量不会让缓存回答自动消失。

权限检查至少在两个位置存在：查询候选范围和按引用回读原文。模型无法补救之前已经读取的越权文本。系统也不能盲信客户端传来的 `tenant`：教学 API 的参数应由经过认证的服务端绑定，而不是由模型从问题里自由填写。

过滤还影响 Top-k 语义。假设全库前 10 名都无权访问，“全库取 10 再过滤”会返回空，即使授权范围第 11 名就是答案。本仓先过滤再计算 BM25 和排名。大型向量引擎需核对 pre-filter/post-filter 的实际执行方式，不能只看请求里写了一个 filter 字段。

## 一次升级应看哪些证据

用同一组查询对比旧索引与候选索引，保留逐查询结果。特别检查：旧版本是否混入、权限切片是否漏过滤、已删除文档能否从缓存回读、维度不符是否明确报错、索引切换失败时是否继续服务已验证版本。

离线语料的“当前版本”仅指本 fixture 最后一次成功 upsert。本仓没有自动抓取来源来验证其时效，也没有宣称知识在现实世界持续最新。接下来读[查询规划](06-query-planning-and-graph-retrieval.md)和[引用验证](07-citations-and-grounding.md)。模型编码的一手说明：[Sentence Transformers](https://sbert.net/docs/sentence_transformer/usage/usage.html)；检索融合接口示例：[Elasticsearch RRF](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)。
