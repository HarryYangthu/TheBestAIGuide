# 应用工程：把 Agent 变成读者能操作和验证的系统

> 状态：draft · 更新：2026-09-06

本域连接后端、用户交互、数据权限与模型请求，再用具体案例说明每一层如何验收。

| 主题 | 核心问题 | 对应实践 |
|---|---|---|
| [后端与流式事件](01-concepts/01-backend-and-streaming.md) | 断线后任务和事件如何恢复 | [浏览器 checkpoint](05-code/browser-agent-typescript/README.md) |
| [人机交互](01-concepts/02-human-agent-interaction.md) | 计划、证据、批准与取消如何一致 | [浏览器案例](03-cases/browser-agents/README.md) |
| [存储与多租户](01-concepts/03-storage-and-multitenancy.md) | 谁能读哪个对象 | [企业案例](03-cases/domain-agents/enterprise/README.md) |
| [模型网关](01-concepts/04-model-gateways.md) | 能力约束、回退和成本如何统一 | [Python 选择算例](05-code/application_cases.py) |

按任务阅读：[Coding Agent](03-cases/coding-agents/README.md)、[Browser Agent](03-cases/browser-agents/README.md)、[企业知识](03-cases/domain-agents/enterprise/README.md)、[运维](03-cases/domain-agents/operations/README.md)、[科研](03-cases/domain-agents/science/README.md)。[领域案例导航](03-cases/domain-agents/README.md)比较它们的验收差异。

[代码目录](05-code/README.md)提供本地运行命令；浏览器工程真实执行 Chromium E2E，Python 案例使用标准库教学数据。所有案例区分公开方法与本库模拟，没有连接真实业务账号。[来源索引](references.md)给出标准与官方文档。
