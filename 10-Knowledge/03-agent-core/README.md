# Agent Core

> 状态：seed

本领域建立最小 Agent 模型：系统如何围绕目标持续观察、决策、行动、更新状态并终止。

## 建议顺序

1. 区分 Chatbot、Workflow 与 Agent。
2. 理解 Goal、Constraint、Observation、State、Action 和 Termination。
3. 建立 `observe → decide → act → observe` 最小循环。
4. 再学习 ReAct、Plan-and-Execute 与 Reflection，避免先把复杂框架当成 Agent 定义。
5. 通过[Agent Loop 实验入口](04-labs/README.md)和[Python 工程骨架](05-code/agent-loop-python/README.md)连接概念与实现。

当前只有范围和未实现代码骨架，不能视为已验证实现。下一步进入[Context Engineering](../04-context-engineering/README.md)。
