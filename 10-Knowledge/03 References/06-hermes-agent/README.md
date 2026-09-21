# Hermes Agent

[References 总览](../README.md)

可自行部署的长期 Agent。学习长期记忆、Skills、Toolsets、多平台消息网关与迁移能力。

原仓：[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)。

## 阅读入口

| 入口 | 阅读重点 |
|---|---|
| [执行入口](https://github.com/NousResearch/hermes-agent/blob/afc3b7c6f397c6d21fd2c129ca17b18b544dd8dc/run_agent.py) | 从主入口进入 agent/，跟踪一次对话中的模型调用与工具结果。 |
| [工具与技能](https://github.com/NousResearch/hermes-agent/blob/afc3b7c6f397c6d21fd2c129ca17b18b544dd8dc/toolsets.py) | 对照 tools/ 与 skills/，查看工具集合与技能说明的组织方式。 |
| [消息与定时任务](https://github.com/NousResearch/hermes-agent/tree/afc3b7c6f397c6d21fd2c129ca17b18b544dd8dc/gateway) | 结合 cron/ 观察多平台消息入口、任务触发与结果投递。 |
| [记忆与迁移](https://github.com/NousResearch/hermes-agent/blob/afc3b7c6f397c6d21fd2c129ca17b18b544dd8dc/README.md) | 沿 README 的 Memory、Architecture 与 Migrating from OpenClaw 入口阅读。 |

## 对应组件

[05 通信与交接](../../02%20Agent%20Harness/05-communication-and-handoff/README.md) · [06 上下文管理](../../02%20Agent%20Harness/06-context-management/README.md) · [09 持久化与故障恢复](../../02%20Agent%20Harness/09-persistence-and-recovery/README.md) · [13 长期记忆](../../02%20Agent%20Harness/13-memory/README.md) · [14 技能库](../../02%20Agent%20Harness/14-skills/README.md)

## 阅读版本

核对日期：2026-09-21。索引固定到提交 [afc3b7c6f397](https://github.com/NousResearch/hermes-agent/tree/afc3b7c6f397c6d21fd2c129ca17b18b544dd8dc)。
