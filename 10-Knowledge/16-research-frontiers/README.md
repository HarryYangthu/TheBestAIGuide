# 研究前沿：带版本和边界地理解方法

> 状态：draft · 更新：2026-09-06

研究快照日期：2026-09-06。本域选择代表论文解释机制与可迁移思想，固定论文版本，不声称覆盖当天全部前沿或复现论文成绩。

| 主题 | 读完要分清 | 实践连接 |
|---|---|---|
| [长程 Agent](01-concepts/01-long-horizon-agents.md) | 单步质量、外置状态和可恢复任务 | [浏览器故障恢复](../13-application-engineering/03-cases/browser-agents/README.md) |
| [自改进与群体协作](01-concepts/02-self-improvement-and-agent-swarms.md) | 反思、技能、权重更新与独立证据 | [概率算例](05-code/research_checks.py) |
| [世界模型与神经符号](01-concepts/03-world-models-and-neuro-symbolic.md) | 预测后果、符号约束与事实验证 | [科研应用案例](../13-application-engineering/03-cases/domain-agents/science/README.md) |
| [推理时学习与监督](01-concepts/04-test-time-learning-and-oversight.md) | 加上下文、加计算和更新学习状态 | [标量更新算例](05-code/research_checks.py) |
| [Research Agent](03-cases/01-research-and-science-agents.md) | 想法、资料、实验、评审与结论 | [研究案例导航](03-cases/README.md) |

[来源表](references.md)记录代表论文版本、日期、支持范围与未复现事项。[代码说明](05-code/README.md)记录本库真正执行的数值与规则检查，避免把数学算例包装成真实 AI 科研成绩。

## 把论文观点变成能检查的问题

读前沿方法时，先写下“改变了什么、输入是什么、与谁比较、什么结果会推翻它”。在[工作台](../../20-Projects/learning-workbench/README.md)中先运行 `practice science`，对照训练数据、验证数据和基线；再看 `research` 的固定论文证据链。CPU 训练、引文定位、模型生成是三个独立证据层，不能因为其中一个通过就宣布科研任务成功。
