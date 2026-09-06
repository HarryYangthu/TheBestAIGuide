# RAG 资源索引

> 状态：draft
> 一手页面核验：2026-09-06；不表示已复现论文或验证所有产品 API。

| 来源及版本 | 支持哪些机制 | 本库使用边界 |
| --- | --- | --- |
| [Lewis et al., RAG，arXiv v4](https://arxiv.org/abs/2005.11401v4) | 参数化生成与外部检索记忆的结合 | 本仓不是论文训练系统复现 |
| [Robertson & Zaragoza, BM25 and Beyond，2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf) | 概率检索框架、词频饱和与长度归一化 | 代码使用正值 IDF 变体；分词器为教学设计 |
| [Cormack et al., RRF，2009，作者 PDF](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf) | 用排名融合异质量纲通道 | 论文收益不外推本教学集 |
| [Docling Technical Report，v5](https://arxiv.org/abs/2408.09869v5) | 文档转换中版面与表格结构识别 | 没有实际运行 Docling/OCR |
| [Sentence Transformers bi-encoder 文档](https://sbert.net/docs/sentence_transformer/usage/usage.html) | 编码向量、query/document 编码入口 | 页面会变化，真实模型运行需另锁版本和权重 |
| [Sentence Transformers cross-encoder 文档](https://sbert.net/docs/cross_encoder/usage/usage.html) | Query—文档成对评分 | 模型未运行，不报告重排收益 |
| [Elasticsearch RRF 文档](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion) | 检索器排名融合的产品实现 | 本代码不依赖 Elasticsearch，未验证部署 |
| [Edge et al., GraphRAG](https://arxiv.org/abs/2404.16130) | 面向语料全局问题的图与社区摘要 | 只说明原论文任务定位，未复现 |

新文章的切块规则、权限契约、引用字段、fixture 和数值例子为本库工程化教学设计，不把它们写成论文统一标准。固定生产 API 前检查对应版本文档，不能仅凭本表的核验日期判断接口永远有效。
