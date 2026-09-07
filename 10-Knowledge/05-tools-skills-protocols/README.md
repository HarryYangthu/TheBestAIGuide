# Tools、Skills与协议

> 状态：draft | 来源核验：2026-09-06；配套离线执行与MCP stdio集成已实测

本域把“模型提出动作”连接到“程序执行动作”，再说明工作方法与跨系统通信怎样复用。

先用一个任务区分四层：“按证据比较两份手册”由 Skill 描述步骤；`search_docs` 工具实际搜索；MCP 让宿主以统一格式发现和调用它；若把整项比较任务交给另一个独立 Agent，才涉及 A2A 的任务、状态和产物交接。它们可以组合使用，各自解决的问题不同。

| 阅读 | 核心问题 | 可运行对应物 |
| --- | --- | --- |
| [结构与工具契约](01-concepts/01-structured-output-and-tool-contracts.md) | JSON合法为什么仍不能执行 | [6类共享Schema](05-code/shared-schemas/README.md) |
| [Skills](01-concepts/02-skills-and-progressive-disclosure.md) | 工作方法怎么按需加载 | [教学包](../../20-Projects/learning-workbench/skills/evidence-comparison/SKILL.md)、预算算例 |
| [MCP](01-concepts/03-mcp.md) | 能力如何被发现与调用 | [官方SDK Server/Client](05-code/mcp-server-typescript/README.md) |
| [Agent通信](01-concepts/04-agent-communication-protocols.md) | 怎样交接任务、状态和产物 | [A2A 0.3.0本地HTTP子集](../../20-Projects/learning-workbench/src/learning_workbench/a2a_demo.py) |
| [委托授权](01-concepts/05-delegated-authorization.md) | 谁允许访问什么 | Runtime主体/scope检查 |
| [执行层模式](02-patterns/01-tool-runtime.md) | 参数错、超时、取消和重复如何处理 | [TS Runtime](05-code/tool-runtime-typescript/README.md) |

[实验Notebook](04-labs/01-tool-contracts-and-errors.ipynb)串起Schema验证与TS故障测试。MCP当前规范为2026-07-28；可运行示例固定SDK 1.29.0，明确演示旧协议兼容路线，升级差异在正文单独说明。[来源表](references.md)记录核验入口。

## 从学习机制到组合使用

跑通 Schema → Runtime → MCP 后，再按 [workbench](../../20-Projects/learning-workbench/README.md)组合 Skill 和 A2A。学习后应能分别解释：为什么“参数符合 Schema”仍可能被拒绝、为什么“超时”不能证明动作没发生、为什么“对方任务完成”仍需检查产物。前两项查看 Runtime 故障测试；第三项对照 A2A 演示中仅回传文本的工作者，避免把通信成功当成内容正确。
