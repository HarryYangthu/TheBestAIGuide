# 基础模型

> 状态：seed

本领域解释大语言模型和其他基础模型的输入表示、网络结构、训练、推理与选择方法，为理解 Agent 的能力边界建立前置知识。

## 建议顺序

1. [Tokenization](01-concepts/tokenization/README.md)：文本如何映射为模型输入。
2. [Transformer](01-concepts/transformer/README.md)：Attention、位置表示和层结构。
3. [训练与对齐](01-concepts/training/README.md)：预训练、监督微调、偏好优化与数据质量。
4. [推理与服务](01-concepts/inference/README.md)：KV Cache、Batch、量化、延迟与吞吐。
5. [Reasoning Models](01-concepts/reasoning/README.md)：推理时计算、验证与能力边界。
6. [模型选择](01-concepts/model-selection/README.md)：质量、成本、延迟、上下文和安全权衡。
7. [实验入口](04-labs/README.md)：模型行为与推理参数实验。

当前内容主要保存在[完整知识地图](../../00-Home/Knowledge-Map.md)，尚未拆成正式专题。下一步进入[Agent Core](../03-agent-core/README.md)。
