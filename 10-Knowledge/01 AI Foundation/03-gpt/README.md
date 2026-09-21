# GPT 架构

[AI Foundation](../README.md) · 前置：[Transformer 与大模型基础](../01-transformer-and-llm-basics/README.md)

本章从 GPT-1、GPT-2 的公开实现学习 Decoder-only 架构，再结合 GPT-3 论文理解模型规模与上下文学习。当前收录章节安排与一手资料，正文与实验待补充。

| 顺序 | 小节 | 重点 | 一手资料 |
|---|---|---|---|
| 01 | Decoder-only | Token 与位置表示、因果注意力、残差与前馈层 | [GPT-1 官方代码与模型](https://github.com/openai/finetune-transformer-lm) |
| 02 | GPT-2 Block | 注意力、归一化位置、输出 logits 与模型配置 | [GPT-2 论文](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)、[官方源码](https://github.com/openai/gpt-2) |
| 03 | 自回归训练与生成 | 标签移位、交叉熵、逐 Token 生成与采样 | [GPT-2 官方源码](https://github.com/openai/gpt-2) |
| 04 | 规模与上下文学习 | GPT-3 的公开结构、训练设置与 few-shot 评测 | [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165) |
| 05 | 最小实验 | 因果 Mask、下一 Token 分布与生成轨迹 | [已有 Tiny Transformer 实验](../../../20-Projects/tiny-transformer/README.md) |

GPT-3 的资料入口是论文；可逐行阅读的官方实现以 GPT-1、GPT-2 为主。其他版本按已公开资料补充，未披露的架构细节不作推测。
