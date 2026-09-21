# Transformer 与大模型基础

[AI Foundation](../README.md)

本章按文本输入、网络计算、训练和生成的顺序组织。下表列出章节安排与可立即阅读的已有材料。

| 顺序 | 小节 | 重点 | 已有材料 |
|---|---|---|---|
| 01 | Token 与 Embedding | 分词、词表、Token ID、向量与张量形状 | [Tokenization](../../_archive/02-foundation-models/01-concepts/tokenization/README.md) |
| 02 | Attention | Q、K、V，缩放点积、Softmax、Mask 与多头 | [Transformer](../../_archive/02-foundation-models/01-concepts/transformer/README.md) |
| 03 | Transformer Block | 位置编码、残差、归一化与前馈网络；Encoder 和 Decoder | [Attention 实验](../../_archive/02-foundation-models/04-labs/01-tokenization-and-attention.ipynb) |
| 04 | 语言模型训练 | 下一 Token 预测、损失、反向传播、预训练与微调 | [训练与对齐](../../_archive/02-foundation-models/01-concepts/training/README.md) |
| 05 | 推理与生成 | 自回归、采样、KV Cache 与精度 | [推理与服务](../../_archive/02-foundation-models/01-concepts/inference/README.md) |
| 06 | 最小实现 | 从字符 ID 写到参数更新与文本生成 | [Tiny Transformer](../../../20-Projects/tiny-transformer/README.md) |

原论文：[Attention Is All You Need](https://arxiv.org/abs/1706.03762)。阅读时对照论文中的 Encoder–Decoder 结构，再进入 [GPT](../03-gpt/README.md)、[DeepSeek](../02-deepseek/README.md) 与 [Qwen](../04-qwen/README.md) 分支。

上述链接指向已有正文与实验；本目录后续按该顺序整理独立章节与配套代码。
