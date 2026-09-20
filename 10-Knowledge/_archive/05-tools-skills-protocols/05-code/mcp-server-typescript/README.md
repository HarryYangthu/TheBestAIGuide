# MCP Server与Client兼容示例

> 状态：verified | 实测：2026-09-06；SDK固定1.29.0，Zod 3.25.76，Node 24.19.0

这是官方v1 SDK的2025-11-25协议教学实现。当前规范已是2026-07-28，生命周期存在变化，见[MCP文章](../../01-concepts/03-mcp.md)。本工程不宣称实现当前新规范全部能力。

从本目录运行：

```bash
npm ci
npm test
node dist/src/client.js 上下文
```

客户端真实启动一个本地stdio子进程，发现`search_docs`工具，搜索教学文档，读取结构化输出，最后关闭连接。无需模型API或外部资料。服务端stdout只写协议消息，诊断应写stderr。

[server.ts](src/server.ts)注册工具与参数/输出Schema；[client.ts](src/client.ts)完成发现/调用/关闭；[integration.test.ts](test/integration.test.ts)验证内存传输、业务错误、未知工具、错误参数及真实子进程。高层SDK把部分错误转为`isError`，所以消费方必须检查该字段，不能只捕获异常。

未实现HTTP部署、OAuth、多租户资源授权、生产监控或新协议迁移；固定锁文件用于重现本地测试，不代表依赖永远无需升级。
