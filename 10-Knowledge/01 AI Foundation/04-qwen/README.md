# Qwen 架构

[AI Foundation](../README.md) · 前置：[Transformer 与大模型基础](../01-transformer-and-llm-basics/README.md)

本章以 Qwen3 为明确版本，组织 Dense 与 MoE 的结构对照。当前收录章节安排与一手资料，正文与实验待补充。

| 顺序 | 小节 | 重点 |
|---|---|---|
| 01 | 模型配置 | 层数、隐藏维度、注意力头与 KV 头，从配置读出网络结构 |
| 02 | 注意力与位置编码 | GQA、RoPE、归一化与一次前向计算的张量形状 |
| 03 | Dense 与 MoE | 前馈层、专家路由、总参数量与激活参数量 |
| 04 | 训练与推理 | 分清网络结构、后训练与思考模式的设置 |
| 05 | 配置与实验 | 对照一个 Dense 型号与一个 MoE 型号，保存结构比较表 |

## 资料索引

| 资料 | 用途 |
|---|---|
| [Qwen3 Technical Report](https://arxiv.org/abs/2505.09388) | 阅读公开模型结构、训练方法与评测 |
| [Qwen3 官方仓库](https://github.com/QwenLM/Qwen3) | 查找模型列表、模型卡、配置与推理入口 |

模型参数按具体型号记录；不同代际的结构放在各自版本下比较。
