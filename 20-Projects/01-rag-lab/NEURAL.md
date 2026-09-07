# 从词项匹配到语义检索与重排

这一轮使用真实预训练模型，不把 TF-IDF 向量叫作语义向量。四种方案使用相同的题目、单句分块、Top-5 和1800字符预算，所以检索结果可以逐题比较。

| 方案 | 实际执行 | 与其他方案的关系 |
| --- | --- | --- |
| bm25 | 查询词与文档词匹配 | 词项基线 |
| dense | MiniLM 编码查询和文档，归一化后点积 | 独立的语义检索 |
| neural-hybrid | BM25与dense的排名做RRF融合 | 同时利用词项与语义信号 |
| rerank | 从neural-hybrid前20块取候选，用Cross-Encoder重新打分 | 只改变已有候选顺序，不能找回前20之外的证据 |

## 向量检索在计算什么

编码器将查询与每块文档各自变成向量：$q=f(\text{query})$、$d=f(\text{document})$。归一化后，点积就是余弦相似度：

$$s(q,d)=\frac{q^Td}{\|q\|\|d\|}.$$

它比较的是模型学到的表示，而不是逐个词是否相同。语义相关不等于能回答问题：一段文字可能与人物生平很相关，却不包含问题需要的出生地点。需要对照支持事实检查。

代码在 [retrieval.py](rag_lab/retrieval.py) 的 `Neural.dense`。查询和文档独立编码意味着文档向量可预先缓存；当前教学实现每题重新编码候选块，便于直观看到输入，不把该实现的耗时当生产向量库性能。

## 重排为什么可能更准确，也更慢

Cross-Encoder把“问题＋候选文档”一起输入模型，让问题和文档的token在同一次计算中交互，再输出相关性分数。每对输入都要运行模型，因此只对前20块进行重排。

查看页面的“现排名←原排名”：原排名是融合结果，现排名是重排结果。不能把Cross-Encoder分数和BM25分数直接相加；它们的尺度和含义不同。重排之后仍受Top-K和上下文预算限制。

## 如何解释对照图

Recall@5是支持事实的逐题召回比例再平均。“完整证据覆盖率”要求一题所需的全部支持事实都在上下文中。对某题多找到一个支持句会提高Recall，但可能仍不能完整回答。

“逐题改善／退化”图分别统计相对BM25的改善、不变和退化题数。它是固定100题上的描述统计，不是显著性检验，也不是泛化结论。不要只挑改进题展示。

检索耗时包含每种方案实际做的编码、打分和排序，不含模型加载与索引初始化。CPU线程固定为2；没有复用上一个方案已算出的向量给下一个方案“免费加速”。下载、模型加载和批量缓存的优化应另做实验。

## 固定版本与运行

```bash
python -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r 20-Projects/01-rag-lab/requirements-neural.txt
python 20-Projects/01-rag-lab/run.py --methods bm25 dense neural-hybrid rerank --output .runs/rag-neural
python 20-Projects/01-rag-lab/verify.py --output .runs/rag-neural
```

编码器：`sentence-transformers/all-MiniLM-L6-v2`，revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`。

重排器：`cross-encoder/ms-marco-MiniLM-L6-v2`，revision `233902d25c440f23af6f7d6e94d2946bac0bee0a`。

模型在源码中绑定revision，CPU线程可用 `RAG_CPU_THREADS` 设置。默认使用官方模型；若通过 `RAG_ENCODER_PATH` / `RAG_RERANKER_PATH` 指定本地文件，则 `local_override=true`，不能仅凭配置中的官方revision宣称本地权重与其相同。

参考文档：[编码器模型卡](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)、[重排器模型卡](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2)。
