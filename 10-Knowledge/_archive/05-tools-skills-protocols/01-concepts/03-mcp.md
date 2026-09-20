# MCP：统一能力接口，协议版本必须说清楚

> 状态：draft | 来源核验：2026-09-06 | 当前规范：2026-07-28；配套实测工程：SDK 1.29.0 / 2025-11-25兼容路线

如果同一个“查资料”功能要接多个Agent宿主，分别为每个宿主写一套发现和调用协议会重复工作。MCP提供统一消息接口：服务端说明提供哪些能力，客户端发现并调用，宿主决定何时向模型提供这些能力及是否允许执行。协议解决互操作，不替代检索算法，也不保证被调用工具安全或答案正确。

| 角色/对象 | 在教学案例中的对应物 |
| --- | --- |
| Host | 运行Agent、构造上下文、控制授权的应用 |
| Client | Host里与某个MCP Server通信的连接/请求组件 |
| Server | 对外暴露 `search_docs` 的本地进程 |
| Tool | 可调用的搜索动作及输入输出Schema |
| Resource / Prompt | 可读取的资料与可复用提示模板；不等于可执行工具 |

先跟着下方的固定版本工程跑通一次发现和调用，再看版本对照；不需要一开始背下全部协议变更。`tools/list` 只是在询问“有哪些工具”，`tools/call` 才请求执行工具。Host 可以发现十个工具，只给当前模型调用提供其中两个；服务端暴露的全部能力不必原样塞进每次上下文。

## 先看版本，再看生命周期

截至核验日期，官方最新规范是2026-07-28。它将核心请求设计为自包含请求，取消旧版必需的 `initialize/notifications/initialized` 握手及协议级会话；版本和客户端能力随请求元数据传递。客户端可以调用 `server/discover` 了解服务端信息，随后发现和调用工具。不能把旧教程的握手流程无日期地写成“MCP永远如此”。

| 对照项 | 本库可运行兼容示例 | 当前规范学习重点 |
| --- | --- | --- |
| 协议版本 | 2025-11-25 | 2026-07-28 |
| SDK | 固定 `@modelcontextprotocol/sdk@1.29.0` | 新一代SDK接口需按官方迁移文档适配 |
| 初始化 | SDK完成初始化握手 | 请求携带版本/能力；可先发现 |
| 工具调用 | `tools/list`、`tools/call` | 仍须处理发现、参数与结果，不能只替换版本字符串 |
| 本库验证 | 内存传输与真实stdio子进程 | 未宣称已经完成新版本端到端兼容测试 |

本例选择固定可重现的兼容版本，是为了同时学习线上可能遇到的旧接口与新规范差异。升级时要替换依赖、生命周期与结果解析并重跑测试，不能把 `protocolVersion` 改成新日期就算完成。

## 搜索请求实际经过什么

[server.ts](../05-code/mcp-server-typescript/src/server.ts)注册工具，声明`query`是非空字符串，输出是带ID和原文的文档列表。[client.ts](../05-code/mcp-server-typescript/src/client.ts)启动子进程、建立连接、列出工具、调用搜索，并在`finally`关闭客户端。stdio使用标准输入输出传输协议消息，所以服务器的调试日志必须写stderr；往stdout写“服务启动成功”会污染消息流。

```typescript
const listing = await client.listTools();
const result = await client.callTool({
  name: "search_docs", arguments: { query: "上下文" }
});
if (result.isError) { /* 处理业务错误，不能当作空结果 */ }
```

SDK示例返回`structuredContent`，同时提供JSON文本，便于兼容消费方。参数只有空格会通过字符串类型检查，但被业务代码拒绝；这正好用于验证结构校验与业务校验的区别。

## 错误分层与实现差异

传输故障、JSON-RPC错误和工具业务错误不是同一回事。协议文档区分协议错误与`isError:true`的工具失败；本库实测的v1高层SDK还会把未知工具和部分参数错误归一化为`isError`结果，所以客户端要同时捕获异常和检查结果标志。测试按照真实SDK行为断言，不能只照预期写一个永远不运行的例子。

本地stdio成功不等于远程部署完成。远程HTTP还涉及TLS、认证、受众校验、超时和反向代理。相关身份边界见[委托授权](05-delegated-authorization.md)。运行步骤见[工程README](../05-code/mcp-server-typescript/README.md)。

一手来源：[2026-07-28变更](https://modelcontextprotocol.io/specification/2026-07-28/changelog)、[2025-11-25工具规范](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)、[官方v1 SDK](https://github.com/modelcontextprotocol/typescript-sdk/tree/v1.x)。
