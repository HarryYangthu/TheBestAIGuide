# 基础模型

> 状态：draft · 6篇概念正文；2个教学Notebook已实跑，具体范围见[运行记录](04-labs/run-report.md)。

沿着“文本输入→网络计算→训练→推理→验证与选型”学习。正文讲清核心机制，Notebook展示中间量和反例，源码提供可直接复用的完整函数。本域不需要GPU、API key或下载大模型。

| 顺序 | 学习主题 | 阅读重点 | 对应实践 |
|---|---|---|---|
| 1 | [Tokenization](01-concepts/tokenization/README.md) | 编码流程、BPE/WordPiece/Unigram、特殊token与模板 | [BPE合并过程](04-labs/01-tokenization-and-attention.ipynb) |
| 2 | [Transformer](01-concepts/transformer/README.md) | QK匹配、缩放推导、Softmax/Mask、V读取、头与位置 | [手算Attention、方差、因果与RoPE](04-labs/01-tokenization-and-attention.ipynb) |
| 3 | [训练与对齐](01-concepts/training/README.md) | 预训练、SFT mask、RLHF/DPO/GRPO、LoRA/QLoRA | [DPO损失与LoRA矩阵](04-labs/02-decoding-cache-and-precision.ipynb) |
| 4 | [推理与服务](01-concepts/inference/README.md) | 解码分布、KV/Prefix缓存、batch、推测解码与压缩 | [Top-p、缓存等价与精度误差](04-labs/02-decoding-cache-and-precision.ipynb) |
| 5 | [推理模型](01-concepts/reasoning/README.md) | CoT、候选采样、Verifier、预算与错误边界 | [候选与精确验证](04-labs/02-decoding-cache-and-precision.ipynb) |
| 6 | [模型选择](01-concepts/model-selection/README.md) | 同任务配对比较、成本、硬约束、Pareto与路由 | [虚构配置的可行集与前沿](04-labs/02-decoding-cache-and-precision.ipynb) |

[实验运行方法](04-labs/README.md) · [完整源码](05-code/README.md) · [一手来源与版本](references.md)。下一域：[Agent Core](../03-agent-core/README.md)。

## 两条实践路线

学结构和训练，按上表 1–4 顺序完成 NumPy 算例，再运行 [tiny-transformer](../../20-Projects/tiny-transformer/README.md)：从字符 ID、Attention、标签移位一直走到参数更新与生成。学模型能力和选型，读完 5–6 后进入[学习工作台](../../20-Projects/learning-workbench/README.md)，检查真实任务的成功与失败。小模型训练 loss 下降和系统任务完成率回答不同问题。
