# TypeScript Tool Runtime

> 状态：verified | 验证日期：2026-09-06；Node 24.19.0，TypeScript 5.8.3，AJV 8.17.1

从本目录运行：

```bash
npm ci
npm test
```

`npm test`先编译，再执行Node内置测试；包含Runtime故障场景和共享Schema的12个正反例。首次安装依赖需要网络，运行测试不调用外部服务。Node要求22+。

[contracts.ts](src/contracts.ts)定义数据对象，[registry.ts](src/registry.ts)编译输入输出Schema，[runtime.ts](src/runtime.ts)实施授权、执行、取消与进程内去重。调用方式：`new ToolRuntime(registry).execute(call, identity, timeoutMs, signal)`。业务handler收到`{identity,signal}`，主体身份必须由可信宿主提供。

限制：scope是演示授权，资源级权限需handler检查；Map只做进程内去重，无持久化、跨进程互斥或自动淘汰；重复等待者复用首个请求的取消语义；AbortSignal是合作取消，不能杀死阻塞JS；超时结果不证明后端没有副作用。参数和返回对象须为可JSON序列化数据。

结合[执行层文章](../../02-patterns/01-tool-runtime.md)、[共享Schema](../shared-schemas/README.md)与[Notebook](../../04-labs/01-tool-contracts-and-errors.ipynb)阅读。
