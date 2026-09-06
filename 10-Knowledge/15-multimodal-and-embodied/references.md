# 多模态与具身：一手来源与实验边界

> 状态：draft · 更新：2026-09-06

核验日期：2026-09-06。下列论文页面已实际打开核对；本库讲解机制，未加载论文模型或复现论文基准。

| 来源 | 版本 | 支持的内容 | 使用限制 |
|---|---|---|---|
| [ViT](https://arxiv.org/abs/2010.11929v2) | v2，2021-06-03 | 图像 patch 序列与 Transformer | Patch 数教学公式不覆盖任意高分辨率方案 |
| [CLIP](https://arxiv.org/abs/2103.00020) | 按核验日作者页面 | 视觉语言对比学习 | 相似度不是事实为真的概率 |
| [Whisper](https://arxiv.org/abs/2212.04356v1) | v1，2022-12-06 | 大规模弱监督语音识别 | 不代表语音生成或实时对话全链路 |
| [ColPali](https://arxiv.org/abs/2407.01449v6) | v6，2025-02-28 | 页面图像、多向量与 late interaction | 本库没有执行 ColPali 推理 |
| [OpenVLA](https://arxiv.org/abs/2406.09246v3) | v3，2024-09-05 | 视觉语言动作模型与适配 | 不代表任意机器人可直接使用 |
| [Playwright Auto-waiting](https://playwright.dev/docs/actionability) | 官方动态文档 | 浏览器动作与可操作性 | DOM 执行实验不等于 VLM Computer Use |

[文档证据实验](04-labs/01-document-evidence.ipynb)只用人工给定的表格结构、数值、单位和区域坐标，检查检索与引用关系。音视频采样、坐标与时间对齐建议为本库工程归纳。真实 OCR、语音、视觉模型和机器人执行需要各自的数据集与实际评测。
