# learn-claude-code

[References 总览](../README.md)

从零构建 Agent Harness。从最小循环逐步复刻 Claude Code-like Harness。

原仓：[shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code)。

## 阅读入口

| 入口 | 阅读重点 |
|---|---|
| [最小循环与工具](https://github.com/shareAI-lab/learn-claude-code/tree/0dcafa2ae053a1ddd6a72f265431104b08a5aa13/s01_agent_loop) | 从模型响应找到工具请求，再跟踪工具结果如何回到消息历史。 |
| [权限与 Hooks](https://github.com/shareAI-lab/learn-claude-code/tree/0dcafa2ae053a1ddd6a72f265431104b08a5aa13/s03_permission) | 先读权限判断，再沿 s04_hooks 查看调用前后的扩展点。 |
| [上下文与复用](https://github.com/shareAI-lab/learn-claude-code/tree/0dcafa2ae053a1ddd6a72f265431104b08a5aa13/s08_context_compact) | 对照 s06_subagent、s07_skill_loading、s09_memory，区分独立上下文、按需加载、压缩与记忆。 |
| [完整 Harness](https://github.com/shareAI-lab/learn-claude-code/tree/0dcafa2ae053a1ddd6a72f265431104b08a5aa13/s15_integrated_harness) | 再读 s16_workflow_runtime 与 s17_goal_loop，观察编排、恢复与结束判断。 |

当前路线为根目录 s01—s17；docs/ 和 agents/ 保留旧的 12 课路线。阅读时按同一套编号推进。

## 对应组件

[03 Agent 执行循环](../../02%20Agent%20Harness/03-agent-loop/README.md) · [06 上下文管理](../../02%20Agent%20Harness/06-context-management/README.md) · [08 工具与执行环境](../../02%20Agent%20Harness/08-tools-and-environment/README.md) · [12 权限与资源控制](../../02%20Agent%20Harness/12-permissions-and-resources/README.md) · [14 技能库](../../02%20Agent%20Harness/14-skills/README.md)

## 阅读版本

核对日期：2026-09-21。索引固定到提交 [0dcafa2ae053](https://github.com/shareAI-lab/learn-claude-code/tree/0dcafa2ae053a1ddd6a72f265431104b08a5aa13)。
