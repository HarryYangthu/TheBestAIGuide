# Context Engineering

> 状态：draft
> 学习目标：理解如何为每一次模型调用选择、转换、排序和组织可信信息。

## 前置知识

- 基础模型的上下文窗口、Token 与 Attention。
- Agent 的 Goal、State、Observation 和 Tool Call。

## 连续学习顺序

1. [主题总览](01-concepts/00-overview.md)：建立 Context Engineering 的系统边界。
2. [上下文模型](01-concepts/01-context-model.md)：理解信息类型、生命周期、信任和预算。
3. [失败模式](01-concepts/02-failure-modes.md)：识别中毒、干扰、冲突、腐化和泄露。
4. [Context Builder](02-patterns/01-context-builder.md)：把候选信息构造成模型输入。
5. [优化策略](02-patterns/02-optimization-strategies.md)：选择、压缩、隔离、卸载和缓存。
6. [评测方法](01-concepts/03-context-evaluation.md)：通过任务、消融和 Trace 验证策略。
7. [实验入口](04-labs/README.md)：运行 Token Budget 与 Context Compaction Notebook。
8. [来源索引](references.md)：回到一手来源核对重要结论。

## 与相邻领域的关系

- [RAG](../06-rag-and-knowledge-systems/README.md)提供外部证据候选，Context Builder 决定如何使用。
- [Memory](../07-memory-and-state/README.md)负责跨轮次保存和读取，Context 负责本轮装载。
- [Runtime](../09-runtime-harness-environment/README.md)执行动作并把观察结果送回下一轮。

## 当前证据边界

- 正文已完成概念去重、术语统一和来源整理。
- Schema、流程和数值是设计示例，不是生产基准。
- 两个 Notebook 仍是占位，未产生本仓可复现实验结果。
