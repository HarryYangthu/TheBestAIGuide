# 后端与流式事件：一次 Agent 运行不能依附一条 HTTP 连接

> 状态：draft · 来源核验：2026-09-06 · 教学示例均为本库原创，非生产成绩。

用户关掉网页后，正在处理的任务应该取消还是继续？这必须由产品语义决定，不能由网络连接是否断开决定。把一次任务执行建模为独立的 Run，可以让任务、状态和浏览器连接分离。

## 接口的职责

`POST /runs` 验证身份和输入，使用请求幂等键创建 Run，返回 run_id；Worker 从队列取任务执行。`GET /runs/{id}` 返回权威状态，`GET /runs/{id}/events` 返回执行进展，`POST /runs/{id}/cancel` 请求取消。这里是接口设计范例，本库浏览器实验实现的是动作执行层，并没有宣称已经部署完整后端。

Run 可以经历 `queued → running → waiting_approval → running → completed`，也可以进入 failed 或 cancelled。终态不能因为一个延迟到达的事件变回 running。把所有内容放在“Assistant message”里，会让前端难以区分文本暂时生成完与整个任务真正完成。

## 流式文本与流式状态分开

| 事件 | 内容 | 是否决定任务完成 |
|---|---|---|
| `text.delta` | 可合并的文本增量 | 否 |
| `tool.started` | 调用 ID、工具名、安全展示参数 | 否 |
| `tool.completed` | 调用 ID、结果引用、耗时 | 否 |
| `approval.requested` | 待批准的具体动作与参数摘要 | 否 |
| `artifact.created` | 产物 ID、名称、版本 | 否 |
| `run.completed` | 终态版本、最终产物引用 | 是 |

SSE 是服务端向浏览器发送事件的简单方式。每条持久事件带单调 ID，断线后客户端可通过 Last-Event-ID 请求补发。重连本身不提供持久队列，服务端仍须保存事件并实现补发、权限检查和过期处理。

```text
id: 17
event: tool.completed
data: {"run_id":"r1","call_id":"c3","artifact_id":"a8"}

```

上面的空行结束一个事件。客户端以 `(run_id,event_id)` 去重，避免重连后把同一产物显示两次。如果事件已过保留期，返回一个明确的重同步信号，再读取当前状态快照；不要假装缺失事件从未发生。

## 取消、并发与恢复

取消接口先把取消意图写入持久状态，Worker 在可中断边界检查。模型流可以中断，但已经提交给外部系统的写动作需要查询结果或补偿，不能把“停止读取响应”等同于“外部动作未发生”。一个 Run 的两个 Worker 同时工作会造成重复副作用，因此领取任务需要租约、版本条件更新或等价协调机制。

可执行的本地示例见[浏览器工程](../05-code/browser-agent-typescript/README.md)：动作有唯一 ID，执行前写 checkpoint，执行后根据页面标记确认结果。这里的 checkpoint 是单进程教学文件，不替代分布式事务。流协议依据[WHATWG SSE](https://html.spec.whatwg.org/multipage/server-sent-events.html)，更多来源见[索引](../references.md)。
