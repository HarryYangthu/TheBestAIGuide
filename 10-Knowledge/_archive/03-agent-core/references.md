# Agent Core 参考资料

> 状态：draft | 核验日期：2026-09-06

| 来源 | 类型与用途 | 使用边界 |
| --- | --- | --- |
| [ReAct，arXiv:2210.03629](https://arxiv.org/abs/2210.03629) | 原论文；行动与观察交替 | 本库规则策略不复现论文模型结果 |
| [Plan-and-Solve，arXiv:2305.04091](https://arxiv.org/abs/2305.04091) | 原论文；先规划再求解 | 不等同于完整持久执行框架 |
| [Reflexion，arXiv:2303.11366](https://arxiv.org/abs/2303.11366) | 原论文；语言反馈与后续尝试 | 不自动更新模型权重 |
| [JSON Schema对象](https://json-schema.org/understanding-json-schema/reference/object) | 官方文档；必填与额外字段 | Schema校验不能代替业务授权 |

论文按上述标识定位；正文引用的是机制，没有把论文benchmark成绩当作本库实验成绩。
