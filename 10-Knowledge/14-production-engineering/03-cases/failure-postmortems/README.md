# 故障复盘：已成功写入的动作在恢复后又执行了一次

> 状态：draft · 更新：2026-09-06

这是本库原创故障注入，非真实企业事故。输入为业务动作 `op-1: create-ticket`。我们在外部写入之后、本地记录完成之前模拟中断，再恢复同一动作。

| 时间 | 外部系统 | 本地状态 | 发生什么 |
|---|---|---|---|
| t0 | 无记录 | pending | 领取动作 |
| t1 | 已有工单 | pending | 外部提交成功 |
| t2 | 已有工单 | pending | 完成 checkpoint 前中断 |
| t3 | 恢复时仍有工单 | pending | 仅看本地状态无法确定是否执行 |
| t4 | 取决于恢复策略 | completed | 盲写得 2 条，按 ID 去重得 1 条 |

根因不是“程序偶尔崩溃”，而是跨系统完成状态存在不确定窗口。只增加重试次数会放大问题。本地脚本 [production_checks.py](../../05-code/production_checks.py)对比两种策略，实际输出 naive_record_count=2 与 idempotent_record_count=1。

修复策略把 operation_id 传给下游，由下游唯一约束或幂等接口决定是否已处理；恢复先查询结果。还要把 operation_id 与参数摘要绑定，防止同一个 ID 意外对应不同任务。脚本的列表去重只有单线程教学语义，不能当作并发数据库原子保证。

真实浏览器层的同类验证见[Browser Agent 案例](../../../13-application-engineering/03-cases/browser-agents/README.md)：提交后注入中断，页面 reload 后查询稳定动作标记，最终 UI 只有一条记录，并有截图证据。测试未覆盖浏览器存储丢失或多个 Worker 同时提交。

复盘的后续检查是：所有写工具是否有同类窗口、是否能查询未决动作、是否能安全补偿，以及恢复执行是否保留原权限。回滚 Runtime 代码不会自动撤销已创建工单，相关解释见[发布与恢复](../../01-concepts/03-release-and-recovery.md)。
