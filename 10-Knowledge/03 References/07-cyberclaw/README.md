# CyberClaw

[References 总览](../README.md)

行为可追踪的 Agent 架构。学习行为审计、两段式技能调用、双水位上下文裁剪与心跳任务。

原仓：[ttguy0707/CyberClaw](https://github.com/ttguy0707/CyberClaw)。

## 阅读入口

| 入口 | 阅读重点 |
|---|---|
| [运行结构](https://github.com/ttguy0707/CyberClaw/tree/12b7c6d52fcc38e134cd0f1aeb7aba420ad23274/cyberclaw) | 沿状态图查看 agent、tools、会话保存与上下文整理。 |
| [两段式调用](https://github.com/ttguy0707/CyberClaw/blob/12b7c6d52fcc38e134cd0f1aeb7aba420ad23274/README.md) | 跟踪 help → help_token → run 的凭据校验和消费过程。 |
| [日志与心跳](https://github.com/ttguy0707/CyberClaw/tree/12b7c6d52fcc38e134cd0f1aeb7aba420ad23274/docs) | 结合运行说明检查行为日志、定时任务与子任务关联。 |
| [验证入口](https://github.com/ttguy0707/CyberClaw/tree/12b7c6d52fcc38e134cd0f1aeb7aba420ad23274/tests) | 对照测试阅读凭据重用、上下文裁剪与恢复的边界。 |

对应仓库为 ttguy0707/CyberClaw。其“双水位”按对话回合控制上下文；长期画像另存为文件。两段式凭据校验与用户授权是不同检查。

## 对应组件

[06 上下文管理](../../02%20Agent%20Harness/06-context-management/README.md) · [09 持久化与故障恢复](../../02%20Agent%20Harness/09-persistence-and-recovery/README.md) · [11 Trace 与可观测性](../../02%20Agent%20Harness/11-trace-and-observability/README.md) · [12 权限与资源控制](../../02%20Agent%20Harness/12-permissions-and-resources/README.md) · [14 技能库](../../02%20Agent%20Harness/14-skills/README.md)

## 阅读版本

核对日期：2026-09-21。索引固定到提交 [12b7c6d52fcc](https://github.com/ttguy0707/CyberClaw/tree/12b7c6d52fcc38e134cd0f1aeb7aba420ad23274)。
