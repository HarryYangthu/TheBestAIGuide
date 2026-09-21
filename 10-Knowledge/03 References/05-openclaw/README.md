# OpenClaw

[References 总览](../README.md)

本地运行的个人 Agent。学习长运行 Agent、Skills、消息入口、系统工具与安全边界。

原仓：[openclaw/openclaw](https://github.com/openclaw/openclaw)。

## 阅读入口

| 入口 | 阅读重点 |
|---|---|
| [运行与架构](https://github.com/openclaw/openclaw/tree/f392a4226c4e40099133a3c15d0ae4b9712aa63f/docs) | 先阅读 Gateway、会话与消息入口的文档，建立一次请求的路径。 |
| [运行实现](https://github.com/openclaw/openclaw/tree/f392a4226c4e40099133a3c15d0ae4b9712aa63f/src) | 沿文档中的入口回到实现，跟踪消息路由、工具执行与状态更新。 |
| [扩展能力](https://github.com/openclaw/openclaw/tree/f392a4226c4e40099133a3c15d0ae4b9712aa63f/skills) | 结合 extensions/ 查看技能和消息渠道的扩展方式。 |
| [安全边界](https://github.com/openclaw/openclaw/blob/f392a4226c4e40099133a3c15d0ae4b9712aa63f/SECURITY.md) | 核对部署的信任模型、权限与隔离条件。 |

## 对应组件

[04 编排与调度](../../02%20Agent%20Harness/04-orchestration-and-scheduling/README.md) · [05 通信与交接](../../02%20Agent%20Harness/05-communication-and-handoff/README.md) · [08 工具与执行环境](../../02%20Agent%20Harness/08-tools-and-environment/README.md) · [09 持久化与故障恢复](../../02%20Agent%20Harness/09-persistence-and-recovery/README.md) · [12 权限与资源控制](../../02%20Agent%20Harness/12-permissions-and-resources/README.md) · [14 技能库](../../02%20Agent%20Harness/14-skills/README.md)

## 阅读版本

核对日期：2026-09-21。索引固定到提交 [f392a4226c4e](https://github.com/openclaw/openclaw/tree/f392a4226c4e40099133a3c15d0ae4b9712aa63f)。
