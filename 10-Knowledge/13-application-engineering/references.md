# 应用工程：标准、官方文档与案例来源

> 状态：draft · 更新：2026-09-06

核验日期：2026-09-06。已打开官方原文；动态文档按核验日理解，不把当前 API 保证为永久不变。

| 来源 | 定位 | 支持的内容 | 本库验证范围 |
|---|---|---|---|
| [WHATWG HTML：Server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html) | EventSource、Last-Event-ID、事件解析 | 流协议与重连语义 | 本域接口为设计说明，未部署 SSE 后端 |
| [PostgreSQL Row Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) | 行策略、默认拒绝、角色绕过 | 数据库隔离边界 | 仅 Python 列表权限反例实际运行，SQL 未执行 |
| [Playwright Auto-waiting](https://playwright.dev/docs/actionability) | fill/click 可操作性 | 动作等待、超时与定位 | Playwright 1.55.0 + Chromium 140 本地 E2E |
| [Playwright Screenshots](https://playwright.dev/docs/screenshots) | page.screenshot | 截图证据生成 | PNG 实际生成并查看 |
| [SWE-agent](https://arxiv.org/abs/2405.15793v1) | v1，2024-05-06，ACI 方法 | Coding Agent 的接口设计 | 公开方法分析，非基准复现 |
| [The AI Scientist](https://arxiv.org/abs/2408.06292v1) | v1，2024-08-12，研究流程 | 提案、实验与报告组织 | 仅本库合成搜索算例运行 |
| [Google SRE：Implementing SLOs](https://sre.google/workbook/implementing-slos/) | 用户视角 SLI/SLO | 运维案例的验收口径 | 没有连接真实监控或生产系统 |

模型网关的能力过滤、批准摘要绑定与领域案例是供应商中立的工程归纳。没有引用未经验证的模型价格或声称调用某个商业模型。完整实现入口见[代码目录](05-code/README.md)。
