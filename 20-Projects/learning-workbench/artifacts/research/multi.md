# 两篇论文的范围比较

| 材料 | 讨论层次 | 定位 | 阅读笔记 |
| --- | --- | --- | --- |
| attention | architecture | https://arxiv.org/pdf/1706.03762v7，p.1 | Transformer uses attention to combine sequence representations; this defines an architecture, not a parameter-efficient adaptation recipe. |
| lora | adaptation | https://arxiv.org/pdf/2106.09685v2，p.1 | LoRA learns a low-rank weight update while keeping pretrained weights fixed; it can be applied within a Transformer. |

The compared notes concern architecture and adaptation; these methods are compatible. The supplied evidence does not establish a performance ranking.

阅读笔记由作者编写；定位脚本只验证短引文与页码。模型读法（若启用）见 JSON trace。
