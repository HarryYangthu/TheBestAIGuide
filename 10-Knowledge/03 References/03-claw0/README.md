# claw0

[References 总览](../README.md)

从零构建 Agent Gateway。从 Agent Loop 逐步加入会话、消息入口、网关、记忆、心跳、投递、恢复与并发。

原仓：[shareAI-lab/claw0](https://github.com/shareAI-lab/claw0)。

## 阅读入口

| 入口 | 阅读重点 |
|---|---|
| [循环与会话](https://github.com/shareAI-lab/claw0/tree/0fbf0eb1bd6515fa5b8faf90067b47128df8f45a/sessions) | 先读 s01—s03：循环、工具、会话持久化与上下文。中文入口在 sessions/zh/。 |
| [消息与路由](https://github.com/shareAI-lab/claw0/tree/0fbf0eb1bd6515fa5b8faf90067b47128df8f45a/sessions) | 继续 s04—s05：将消息入口接到 Gateway，跟踪路由与会话隔离。 |
| [记忆与主动任务](https://github.com/shareAI-lab/claw0/tree/0fbf0eb1bd6515fa5b8faf90067b47128df8f45a/workspace) | 结合 s06—s07，查看记忆、技能、心跳与定时任务的配置样例。 |
| [可靠执行](https://github.com/shareAI-lab/claw0/tree/0fbf0eb1bd6515fa5b8faf90067b47128df8f45a/sessions) | 最后读 s08—s10：消息投递、重试恢复与并发队列。 |

## 对应组件

[03 Agent 执行循环](../../02%20Agent%20Harness/03-agent-loop/README.md) · [04 编排与调度](../../02%20Agent%20Harness/04-orchestration-and-scheduling/README.md) · [05 通信与交接](../../02%20Agent%20Harness/05-communication-and-handoff/README.md) · [06 上下文管理](../../02%20Agent%20Harness/06-context-management/README.md) · [09 持久化与故障恢复](../../02%20Agent%20Harness/09-persistence-and-recovery/README.md) · [13 长期记忆](../../02%20Agent%20Harness/13-memory/README.md)

## 阅读版本

核对日期：2026-09-21。索引固定到提交 [0fbf0eb1bd65](https://github.com/shareAI-lab/claw0/tree/0fbf0eb1bd6515fa5b8faf90067b47128df8f45a)。
