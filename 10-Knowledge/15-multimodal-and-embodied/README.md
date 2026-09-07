# 多模态与具身：保留空间、时间和动作语义

> 状态：draft · 更新：2026-09-06

先学如何将不同模态变成可用证据，再讨论根据观察采取动作。能描述画面并不等于能读准数字，能识别按钮也不等于可以可靠提交。

| 主题 | 重点 | 代码/实验 |
|---|---|---|
| [视觉与文档](01-concepts/01-vision-and-document-ai.md) | Patch、VLM、OCR、表格与版面 | [文档证据实验](04-labs/01-document-evidence.ipynb) |
| [语音音频与视频](01-concepts/02-speech-audio-and-video.md) | 波形、转写、WER、时间轴与抽帧 | 文内采样反例 |
| [多模态上下文与检索](01-concepts/03-multimodal-context-and-rag.md) | 多向量匹配、区域证据和引用 | [evidence.py](05-code/evidence.py) |
| [Computer Use 与 VLA](01-concepts/04-computer-use-vla-and-embodied.md) | 目标定位、动作契约与恢复边界 | [本地浏览器工程](../13-application-engineering/05-code/browser-agent-typescript/README.md) |

[来源索引](references.md)对应 ViT、CLIP、Whisper、ColPali、OpenVLA 等一手资料。[实验说明](04-labs/README.md)覆盖人工结构化文档证据；配套工作台进一步实际解析原创 PDF 文本与页码。两者都没有运行这些视觉/音频大型模型或机器人。

## 配套项目扩展（2026-09-06）

[原创 PDF→文字/页码/位置证据及无文字页拒答](../../20-Projects/learning-workbench/README.md)已提供源码、输入数据、运行入口和实际结果。默认机制验证与可选真实模型结果分开记录，具体适用范围见项目说明。
