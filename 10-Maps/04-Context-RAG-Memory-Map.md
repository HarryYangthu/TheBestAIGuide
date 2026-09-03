# Context、RAG 与 Memory 知识地图

> 状态：draft
> 主线：从外部信息与历史状态中，选择当前决策真正需要的可信内容。

## 三者的关系

```text
Knowledge Sources ──> RAG ───────┐
Conversation / State ────────────┼─> Context Builder ─> Model
Long-term Store ──> Memory Read ─┘         │
                                            └─> 新观察 / 新状态 / 候选记忆
```

| 模块 | 核心职责 | 不负责什么 |
| --- | --- | --- |
| Context Engineering | 为单次模型调用选择、转换、排序和校验输入 | 不直接持久化全部历史，不执行工具副作用 |
| RAG | 从外部知识源检索可追溯证据 | 不保证模型一定正确使用证据 |
| Memory | 决定跨轮次或跨会话保存和读取什么 | 不等于把全部对话永久保存 |
| State | 保存当前任务的权威运行事实 | 不等于可模糊召回的长期记忆 |

## Context Engineering

- [总览](../20-Knowledge/04-context-engineering/Context-Engineering.md)
- [上下文模型](../20-Knowledge/04-context-engineering/01-context-model.md)
- [Context Builder](../20-Knowledge/04-context-engineering/02-context-builder.md)
- [失败模式](../20-Knowledge/04-context-engineering/03-failure-modes.md)
- [优化策略](../20-Knowledge/04-context-engineering/04-optimization-strategies.md)
- [评测方法](../20-Knowledge/04-context-engineering/05-context-evaluation.md)
- [Context Builder 模式](../30-Patterns/context/context-builder.md)

## RAG 与知识系统

- [RAG 端到端流程](../20-Knowledge/06-rag-and-knowledge-systems/01-rag-pipeline.md)
- [混合检索与重排](../20-Knowledge/06-rag-and-knowledge-systems/02-hybrid-retrieval-and-reranking.md)
- [Hybrid Retrieval 模式](../30-Patterns/rag/hybrid-retrieval.md)
- [运维 RAG 设计案例](../40-Cases/rag-systems/README.md)

## Memory 与 State

- [Memory 与状态模块](../20-Knowledge/07-memory-and-state/README.md)

待补：Working/Session/Episodic/Semantic/Procedural Memory、Checkpoint、写入验证、冲突、遗忘、隐私删除和 Memory Eval。

## 建议阅读顺序

1. 先理解 Context 的信息模型与 Builder。
2. 再学习 RAG 的离线知识链和在线检索链。
3. 用混合检索案例理解语义、关键词和精确字段的互补。
4. 再进入 State 与 Memory，避免把对话历史、运行状态和长期记忆混为一谈。
5. 最后用 Evaluation 检查压缩、检索和记忆是否真正改善任务结果。

## 当前边界

Context 与 RAG 已有重构后的 `draft` 正文；Memory 仍为 `seed`。Notebook、RAG Pipeline 和相关 Eval Harness 均未实现，因此尚无本仓 `verified` 结论。
