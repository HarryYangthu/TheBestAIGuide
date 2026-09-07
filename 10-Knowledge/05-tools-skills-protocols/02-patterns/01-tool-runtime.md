# Tool Runtime：把失败限制在可处理的范围

> 状态：draft | 来源核验：2026-09-06 | TS实现与故障测试已运行

一个真正可用的工具执行层不仅要`await handler(args)`。它还要在执行前拒绝不合法动作，执行中响应超时/取消，执行后检查结果，并让重试不会轻易重复产生副作用。本例用同一个搜索工具说明这些控制。

| 失败模式 | 运行时处理 | 后续动作 | 代价/边界 |
| --- | --- | --- | --- |
| 整个调用缺ID、错类型或多余字段 | `invalid_request`，不执行 | 先修调用封装 | 还没有进入具体工具参数校验 |
| 参数不符合Schema | `invalid_arguments`，不执行 | 让调用方修参数 | 校验正确不等于业务语义正确 |
| 身份无scope | `permission_denied`，不执行 | 按真实授权流程处理 | 不能让模型自己补权限 |
| Handler抛异常 | `execution_error`，隐藏秘密 | 根据错误类别人工或程序处置 | 本例保守不自动重试 |
| 超出时限 | 返回`timeout`，发AbortSignal | 核查实际执行状态 | 返回超时不证明副作用没有发生 |
| 用户取消 | 返回`cancelled`，传播取消信号 | 停止尚未执行步骤 | Handler必须配合才能终止 |
| 输出结构错 | `invalid_output` | 修工具或适配器 | 不把错误留到下游模型猜测 |
| 相同ID、不同参数 | `idempotency_conflict` | 调用方纠正身份或ID | 防止误用旧结果 |

## 超时与取消为什么不是强制杀死

`Promise.race([handler(), timeout])`只是先返回先完成的结果，不会自动停止另一个Promise。因此本例同时向handler传`AbortSignal`。网络客户端和异步任务需要监听这个信号并释放资源。若handler执行一个阻塞事件循环的无限循环，定时器本身也无法按时触发；要获得硬时间上限，必须使用可终止的worker或进程隔离。

还有一种更实际的情况：写数据库已经成功，响应途中超时。重试可能写两遍。所以本例把超时标为不自动重试，业务层需要通过幂等ID查询或使用后端原子幂等操作。超时重试和权限错误重试都不是“多试几次总会好”。

## 幂等缓存要处理并发与冲突

执行入口先同步校验整个 ToolCall 结构，随即复制参数与可信身份，在进入异步 handler 前完成工具参数和权限检查。中间没有 `await`；普通调用者在 `execute()` 返回 Promise 后修改原对象，不会改变已经复制的内容。handler 启动前再检查取消信号，已经取消且尚未开始的动作不应执行。这是对象隔离，不是用来运行恶意 JavaScript 的沙箱。

本实现以`(subject,call_id)`为键，保存请求签名与正在执行的Promise。第二个完全相同的并发调用等待第一份结果，不再执行handler；若参数不同则拒绝。参数签名使用按键排序的JSON结构，避免仅因为字段顺序不同就误判冲突。

```typescript
const old = calls.get(key);
if (old) {
  if (old.signature !== signature) return conflict;
  return structuredClone(await old.promise);
}
```

复制结果是为了防止调用方修改返回对象后污染缓存。调用者取消其中一个等待者是否应取消共享底层任务，属于另一个策略问题；本例由首个调用的取消信号控制底层任务，后来的重复等待者复用其结果，文档明确这一点，避免误以为每个等待者完全独立。

内存缓存只在同一Runtime实例存活期间有效。进程重启、多实例部署、权限版本变化和缓存增长都需要额外设计；不能把这份Map称为跨服务exactly-once保证。写操作的强幂等应在真正产生副作用的后端完成。

## 怎样验证，先看哪些反例

[测试](../05-code/tool-runtime-typescript/test/runtime.test.ts)包含正确输入、错类型、额外字段、无权限、输出错误、重复并发、冲突ID、超时、取消、异常脱敏、调用对象篡改与启动前取消；[跨语言测试](../05-code/tool-runtime-typescript/test/schemas.test.ts)还校验同一组正反例。真实服务接入后，应继续测连接断开、写成功后响应丢失以及权限撤销。

运行入口：[工程README](../05-code/tool-runtime-typescript/README.md)。协议输入约束见[工具契约](../01-concepts/01-structured-output-and-tool-contracts.md)，持久恢复见[Runtime与Harness](../../09-runtime-harness-environment/README.md)。
