# 03｜References

[知识库总览](../README.md) · [Agent Harness](../02%20Agent%20Harness/README.md)

这里收录 8 个参考入口：1 份官方产品文档与 7 个代码仓。每个目录提供原始链接、阅读重点、版本记录和对应组件。

| System | Best For | Learn This If You Want To |
|---|---|---|
| [Claude Code Docs](01-claude-code-docs/README.md) · [官方文档](https://code.claude.com/docs/en/overview) | Coding agent product | 学真实 Coding Agent 的 CLI、工具、权限、Hooks、Subagents、MCP |
| [learn-claude-code](02-learn-claude-code/README.md) · [原仓](https://github.com/shareAI-lab/learn-claude-code) | From-scratch agent harness | 从最小循环逐步复刻 Claude Code-like Harness。 |
| [claw0](03-claw0/README.md) · [原仓](https://github.com/shareAI-lab/claw0) | From-scratch OpenClaw gateway | 从 Agent Loop 逐步加入会话、消息入口、网关、记忆、心跳、投递、恢复与并发。 |
| [hello-agents](04-hello-agents/README.md) · [原仓](https://github.com/datawhalechina/hello-agents) | Chinese agent tutorial | 系统补齐 Agent 原理、框架实践、上下文、记忆、协议与评估。 |
| [OpenClaw](05-openclaw/README.md) · [原仓](https://github.com/openclaw/openclaw) | Local-first personal agent | 学习长运行 Agent、Skills、消息入口、系统工具与安全边界。 |
| [Hermes Agent](06-hermes-agent/README.md) · [原仓](https://github.com/NousResearch/hermes-agent) | Self-hosted growing agent | 学习长期记忆、Skills、Toolsets、多平台消息网关与迁移能力。 |
| [CyberClaw](07-cyberclaw/README.md) · [原仓](https://github.com/ttguy0707/CyberClaw) | Transparent agent architecture | 学习行为审计、两段式技能调用、双水位上下文裁剪与心跳任务。 |
| [LangGraph](08-langgraph/README.md) · [原仓](https://github.com/langchain-ai/langgraph) | Stateful graph orchestration | 学习状态图、可恢复执行、检查点、子图、流式输出与人工介入。 |

## 阅读路线

| 目标 | 阅读顺序 |
|---|---|
| 从零实现 Harness | learn-claude-code → Claude Code Docs，对照最小实现与产品行为 |
| 构建长运行个人 Agent | claw0 → OpenClaw → Hermes Agent，依次阅读网关、完整系统与记忆/技能复用 |
| 补齐原理与编排 | hello-agents → LangGraph，先理解范式，再实现有状态执行 |
| 研究审计与调用约束 | CyberClaw，对照日志、凭据校验、上下文水位与心跳 |

核对日期：2026-09-21。已核对上游 README、目录或官方文档，未运行这些外部项目。各项目的具体配置与运行方式见其上游说明。

模型架构资料见 [AI Foundation](../01%20AI%20Foundation/README.md)；论文、教材与协议来源见 [90-Sources](../../90-Sources/README.md)。
