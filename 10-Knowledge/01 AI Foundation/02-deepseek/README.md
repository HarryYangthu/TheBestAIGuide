# DeepSeek 与 MoE

[AI Foundation](../README.md) · 前置：[Transformer 与大模型基础](../01-transformer-and-llm-basics/README.md)

本章以 DeepSeekMoE、DeepSeek-V2、DeepSeek-V3 为阅读对象，按下表系统展开架构。当前收录章节安排与一手资料，正文与实验待补充。

| 顺序 | 小节 | 要解释的问题 | 对照资料 |
|---|---|---|---|
| 01 | MoE 与专家路由 | Dense 前馈层怎样变成专家网络；总参数量与激活参数量如何区分 | [DeepSeekMoE 论文](https://arxiv.org/abs/2401.06066) |
| 02 | 细粒度专家与共享专家 | 专家如何划分，哪些专家共同参与计算 | [DeepSeekMoE 论文](https://arxiv.org/abs/2401.06066) |
| 03 | MLA | 注意力与 KV Cache 如何组织 | [DeepSeek-V2 论文](https://arxiv.org/abs/2405.04434) |
| 04 | 负载均衡与训练目标 | V3 的专家负载均衡、多 Token 预测解决什么问题 | [DeepSeek-V3 技术报告](https://arxiv.org/abs/2412.19437) |
| 05 | 架构与源码对照 | 将路由、专家、注意力与模型配置对应到实现 | [DeepSeek-V3 官方仓库](https://github.com/deepseek-ai/DeepSeek-V3) |
| 06 | 最小实验 | 用小张量展示路由分数、专家选择、合并输出与激活量 | 配套代码待补充 |

阅读顺序为 DeepSeekMoE → V2 → V3。每次比较注明版本，并将模型结构、训练方法和推理实现分别说明。
