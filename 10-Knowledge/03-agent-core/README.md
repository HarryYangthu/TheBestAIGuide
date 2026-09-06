# Agent Core

> 状态：draft | 配套工程与Notebook的离线控制流程已运行验证；真实LLM效果未评测

从“检索资料并带证据回答”理解Agent。先掌握动作与状态如何变化，再增加计划、验证和恢复。

| 阅读顺序 | 解决的问题 | 对应实践 |
| --- | --- | --- |
| [边界与组成](01-concepts/01-agent-boundaries.md) | 什么时候需要Agent，哪些控制仍应写成程序 | 目标、状态、动作字段 |
| [Agent Loop](01-concepts/02-agent-loop.md) | 循环如何推进，怎么防止不停执行 | [Loop源码](05-code/agent-loop-python/src/agent_loop/loop.py) |
| [模型适配器](01-concepts/03-model-adapters.md) | 如何把API输出接入执行器 | [动作与模型接口](05-code/agent-loop-python/src/agent_loop/models.py) |
| [ReAct与计划执行](02-patterns/01-react-and-plan-execute.md) | 逐步探索与预先分解怎样选 | 同工具、同Loop组合子任务 |
| [反思与验证](02-patterns/02-reflection-verification-human-loop.md) | 完成后如何检查，失败后怎么修 | 引用检查与有界修订 |

先照[工程README](05-code/agent-loop-python/README.md)运行一次，再打开[实验Notebook](04-labs/01-agent-loop.ipynb)比较成功、重复与预算耗尽。教学策略是确定性的，不把它称作模型推理效果。

来源见[参考资料](references.md)。下一站：[上下文工程](../04-context-engineering/README.md)与[工具契约](../05-tools-skills-protocols/README.md)。

## 配套项目扩展（2026-09-06）

[真实模型适配、两工具和 12 条任务评测](../../20-Projects/learning-workbench/README.md)已提供源码、输入数据、运行入口和实际结果。默认机制验证与可选真实模型结果分开记录，具体适用范围见项目说明。
