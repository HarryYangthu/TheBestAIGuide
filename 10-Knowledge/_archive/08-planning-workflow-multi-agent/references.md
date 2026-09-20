# 来源与验证边界

> 状态：draft；以下网页已于 2026-09-06 打开核验。本文是机制教学与本地实现，不代表来源方对本库实现背书。

| 一手来源 | 本域使用范围 | 版本边界 |
|---|---|---|
| [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | 工作流、路由、并行、动态编排的基本区别 | 原文发表于 2024-12-19；本文不采纳其产品名称作为当前选型结论 |
| [Python: Coroutines and tasks](https://docs.python.org/3/library/asyncio-task.html) | await、任务生命周期和协作式取消 | 本例仅使用 Python 3.11 已有 API |
| [LangGraph: Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) | 持久化状态和恢复的背景阅读 | 在线文档；示例不是 LangGraph API 封装 |

本文的候选模型数据、预算数字、并行耗时算例、投票概率推导及代码均为教学构造。实际输出见[Notebook](04-labs/01-single-vs-multi-agent.ipynb)，原理阅读从[本域导航](README.md)开始。
