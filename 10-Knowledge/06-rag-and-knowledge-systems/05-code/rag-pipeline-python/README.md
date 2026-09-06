# RAG Pipeline Python

> 状态：verified
> 验证：2026-09-06，Python 3.12.13；9 项测试通过，8 条查询已实际执行。

从文档到证据的可读参考实现。默认离线，无第三方运行依赖、无密钥。人工语料中的 DEMO 设备和步骤是虚构例子。

## 运行

从本工程目录运行（无需安装）：

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m rag_pipeline.cli
```

PowerShell：

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python -m rag_pipeline.cli
```

结果写入 [run-report.json](run-report.json)。[Notebook](../../04-labs/01-hybrid-retrieval-evaluation.ipynb)保存中间输出，适合逐步学习。核心依赖是标准库，见 [requirements.lock](requirements.lock)；可通过 `python -m pip install -e .` 安装，但构建需要 setuptools，离线时优先使用 PYTHONPATH。

## 公开接口

```python
from rag_pipeline import Document, Index, answer, verify_citation

index = Index()
index.upsert(Document("manual", "ALM-12003：先读取日志。", tenant="alpha",
                      product="DEMO-A", version="2", identifiers=("ALM-12003",)))
hits = index.search("ALM-12003", tenant="alpha", product="DEMO-A", version="2", k=3)
result = answer(index, "ALM-12003", tenant="alpha", product="DEMO-A", version="2")
assert all(verify_citation(index, c, tenant="alpha") for c in result.citations)
index.delete("manual", tenant="alpha")
```

| 文件 | 读代码时关注什么 | 对应知识 |
| --- | --- | --- |
| [ingest.py](src/rag_pipeline/ingest.py) | 输入契约、编码、完整编号 | [解析](../../01-concepts/03-ingestion-and-parsing.md) |
| [chunking.py](src/rag_pipeline/chunking.py) | 段落边界、原文偏移、版本化 ID | [切块](../../01-concepts/04-chunking-and-metadata.md) |
| [retrieval.py](src/rag_pipeline/retrieval.py) | 先过滤再打分、BM25、更新删除 | [混合检索](../../01-concepts/02-hybrid-retrieval-and-reranking.md) |
| [ranking.py](src/rag_pipeline/ranking.py) | RRF、Recall/MRR/nDCG | [公式与手算](../../01-concepts/02-hybrid-retrieval-and-reranking.md) |
| [citations.py](src/rag_pipeline/citations.py) | 版本/范围/原文验证 | [引用](../../01-concepts/07-citations-and-grounding.md) |
| [tests](tests/test_pipeline.py) | 编号/权限/旧引用/回调形状反例 | [实验说明](../../04-labs/README.md) |

## 接真实 Embedding/Reranker

`Index(embedder=..., reranker=...)` 接收两种可调用对象。embedder 输入 `[query, doc1, ...]`，返回同批量、同维度、有限浮点向量；查询和文档必须来自兼容空间。reranker 输入 `(query,[text1,...])`，返回等长分数列表，分数越大越相关。排序前已经过滤租户、产品、版本和编号。

可用 Sentence Transformers 的 `encode_query/encode_document` 与 CrossEncoder `predict` 适配这些接口；具体参考 [官方 bi-encoder](https://sbert.net/docs/sentence_transformer/usage/usage.html)与 [cross-encoder](https://sbert.net/docs/cross_encoder/usage/usage.html) 文档。应固定安装版本、权重 revision、设备、归一化及截断配置并记录运行环境。

本次没有下载权重或运行这些模型。单元测试仅用固定向量验证回调形状和权限边界，不构成语义质量实验。`mode="dense"` 未配置 embedder 会报错。当前回调对过滤后的全部候选编码/重排，属于小语料参考接口；大语料需要离线向量索引和候选 Top-M，不能直接复制其扫描成本。

## 结果与局限

可回答查询 5 条，BM25/Hybrid Recall@3 均 0.8，Exact 0.4；跨语言 `airflow obstruction` 无法命中中文“风道堵塞”，保留为失败。3 条无答案/旧版本/无权限查询都返回空。所有数字都只对应本教学 fixture，数据说明见 [fixtures/README.md](fixtures/README.md)。

`answer` 是原文抽取，不是 LLM 生成；有候选不表示足够回答。中文单字分词可能召回无关块。多编号文档按块中出现的编号匹配，避免把不同故障段落混入；没有显式元数据时会从正文提取编号，但规则不理解否定。单编号文档无编码段允许继承，复杂手册仍需节级上下文标注。默认 k 按块截断，`unit="document"` 在截断前按文档去重，文档以排名最高块代表；CLI/Notebook 指标使用后者。当前索引单进程、内存、不持久化，不提供并发事务。调用方必须从可信认证结果绑定 tenant。`verify_citation` 检查原文一致性，不检查语义蕴含或文档本身真假。PDF/OCR、数据库/图检索、模型生成和线上容量均未实现或验证。
