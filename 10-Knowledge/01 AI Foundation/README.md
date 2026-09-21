# 01｜AI Foundation

[知识库总览](../README.md)

这里集中学习大模型的技术基础与公开架构。先理解 Transformer 和语言模型的训练、推理过程，再对照具体模型阅读论文与源码。

## 阅读目录

| 顺序 | 章节 | 内容范围 | 当前入口 |
|---|---|---|---|
| 01 | [Transformer 与大模型基础](01-transformer-and-llm-basics/README.md) | Token、Embedding、Attention、Transformer、预训练、对齐、解码与 KV Cache | 已有基础正文与实验；新章节安排 |
| 02 | [DeepSeek 与 MoE](02-deepseek/README.md) | 专家路由、共享专家、MLA、负载均衡与多 Token 预测 | DeepSeekMoE、V2、V3 论文与官方源码索引 |
| 03 | [GPT 架构](03-gpt/README.md) | Decoder-only、因果注意力、自回归训练与生成 | GPT-1、GPT-2 源码与 GPT-3 论文索引 |
| 04 | [Qwen 架构](04-qwen/README.md) | Dense 与 MoE、注意力、位置编码、归一化与模型配置 | Qwen3 技术报告与官方仓库索引 |

各架构目录目前提供章节安排与资料索引，正文和配套实验后续逐章补充。资料按明确的模型版本组织。

## 配套资料

论文、官方源码与模型配置链接随对应章节保存。跨项目的参考仓与阅读笔记统一进入 [03 References](../03%20References/README.md)。

已有的[数学、机器学习与深度学习基础](../_archive/01-ai-foundations/README.md)和[基础模型实验](../_archive/02-foundation-models/README.md)保留为阅读材料。
