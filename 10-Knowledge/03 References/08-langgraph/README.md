# LangGraph

[References 总览](../README.md)

有状态图编排。学习状态图、可恢复执行、检查点、子图、流式输出与人工介入。

原仓：[langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)。

## 阅读入口

| 入口 | 阅读重点 |
|---|---|
| [概念与快速开始](https://github.com/langchain-ai/langgraph/blob/ed384f3a124660db6dccd6c53eaad48e1457e0b5/README.md) | 从 StateGraph、节点、边和状态更新开始。 |
| [框架实现](https://github.com/langchain-ai/langgraph/tree/ed384f3a124660db6dccd6c53eaad48e1457e0b5/libs) | 沿 graph、checkpoint 与执行相关包阅读状态推进与持久化。 |
| [完整示例](https://github.com/langchain-ai/langgraph/tree/ed384f3a124660db6dccd6c53eaad48e1457e0b5/examples) | 选择带分支或子图的示例，再观察中断与恢复。 |

官方文档：[LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)。先实现状态图，再加入持久化与人工介入。

## 对应组件

[04 编排与调度](../../02%20Agent%20Harness/04-orchestration-and-scheduling/README.md) · [07 状态与产物](../../02%20Agent%20Harness/07-state-and-artifacts/README.md) · [09 持久化与故障恢复](../../02%20Agent%20Harness/09-persistence-and-recovery/README.md) · [12 权限与资源控制](../../02%20Agent%20Harness/12-permissions-and-resources/README.md)

## 阅读版本

核对日期：2026-09-21。索引固定到提交 [ed384f3a1246](https://github.com/langchain-ai/langgraph/tree/ed384f3a124660db6dccd6c53eaad48e1457e0b5)。
