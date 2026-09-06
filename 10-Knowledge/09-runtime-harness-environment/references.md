# Runtime 来源与验证边界

> 状态：draft；核验日期：2026-09-06。

| 一手来源 | 使用范围 |
|---|---|
| [AWS Builders Library：幂等 API](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) | 幂等请求身份与重试安全的背景 |
| [AWS：Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) | 指数退避和抖动机制 |
| [Python asyncio tasks](https://docs.python.org/3/library/asyncio-task.html) | wait_for、协作式取消和清理语义 |
| [Python sqlite3](https://docs.python.org/3/library/sqlite3.html) | 事务与参数化 SQL；本实现使用 Python 3.11 已有 API |
| [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) | Checkpoint 与恢复的进一步阅读 |
| [Little 1961：A Proof for the Queuing Formula L = λW](https://doi.org/10.1287/opre.9.3.383) | 稳定排队系统的平均量关系 |
| [NIST SP 800-207](https://csrc.nist.gov/pubs/sp/800/207/final) | 围绕资源进行身份与权限检查的原则 |

本库的 Harness 分层、事件字段、账本与故障设计为教学实现。没有宣称来源规定统一 Agent Runtime 标准，也没有做线上可用性或灾备认证。运行证据见[实验](04-labs/01-recovery-and-idempotency.ipynb)，返回[导航](README.md)。
