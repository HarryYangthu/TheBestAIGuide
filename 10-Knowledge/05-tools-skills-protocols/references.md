# 工具与协议一手来源

> 状态：draft | 核验日期：2026-09-06

| 来源 | 版本/用途 | 本库验证范围 |
| --- | --- | --- |
| [JSON Schema](https://json-schema.org/understanding-json-schema/reference/object) | 2020-12对象语义 | Python与TS共同验证12个基础正反例和47个边界反例 |
| [Agent Skills](https://agentskills.io/specification) | 持续更新格式，按核验日阅读 | 格式解释、加载预算算例与本仓教学包；宿主自动触发未测 |
| [MCP当前变更](https://modelcontextprotocol.io/specification/2026-07-28/changelog) | 2026-07-28 | 文档核验，未实现新协议完整服务器 |
| [MCP工具](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) | 2025-11-25兼容示例依据 | 发现、调用、错误与stdio关闭 |
| [官方TypeScript SDK v1](https://github.com/modelcontextprotocol/typescript-sdk/tree/v1.x) | npm固定1.29.0 | 安装、编译、内存及子进程集成 |
| [MCP授权](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization) | 2026-07-28 | 机制说明，未接OAuth服务 |
| [A2A规范](https://a2a-protocol.org/v0.3.0/specification/) | 配套教学端点固定0.3.0 | 两个本地HTTP端点的文本/JSON-RPC子集；未声称完整一致性 |
| [A2A任务生命周期](https://a2a-protocol.org/latest/topics/life-of-a-task/) | 持续更新文档 | 恢复与产物版本问题 |
| [RFC 8693](https://www.rfc-editor.org/rfc/rfc8693) | OAuth令牌交换标准 | 委托概念，不要求所有系统强制采用 |
