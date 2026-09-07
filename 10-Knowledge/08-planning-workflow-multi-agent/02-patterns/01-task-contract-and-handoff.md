# 任务契约与交接：交付什么，比扮演谁更重要

> 状态：draft；来源核验：2026-09-06；配套实现已进行本地 fixture 验证，非真实模型性能评测。


主 Agent 说“帮我看一下模型能不能用”，子 Agent 返回一篇优缺点分析。主 Agent 想要的是能否通过 20 ms 时延约束，子 Agent 却主要谈效果；两边都执行了自己的理解，最后仍没法合并。这是任务契约缺失，不一定是模型能力不足。

任务契约是交接双方都能检查的数据约定。它把自然语言目标变成输入范围、允许动作、输出格式和完成条件。

```python
from multi_agent import Task

Task(
    task_id="constraints",
    kind="constraints",
    payload={"candidates": [{"name": "A", "quality": 0.91,
                             "latency_ms": 18, "memory_mb": 200}]},
    required_keys=("feasible",),
    timeout_s=1.0,
)
```

这个真实可运行的构造来自[contracts.py](../05-code/multi-agent-runtime-python/src/multi_agent/contracts.py)。`task_id` 供追踪和重试引用；`kind` 路由到有对应能力的 Worker；`payload` 只包含完成此任务需要的数据；`required_keys` 防止返回另一种答案；`timeout_s` 为包含排队时间的超时阈值，等待并发名额也会消耗它。底层 `asyncio.wait_for` 到点会请求取消并等待清理，因此超时阈值不是强制中止进程的墙钟保证；Worker 阻塞事件循环或不配合取消时，实际返回可能更晚。

## 三次交接，各检查一层

| 时点 | 应检查的事实 | 本例怎么做 |
|---|---|---|
| 委派前 | ID 唯一、输入可序列化、总任务预算足够 | 构造 Task 和 `Supervisor.run` 时拒绝非法请求 |
| Worker 返回后 | 返回值是否符合输出契约 | 必须是 JSON 对象且键恰好符合 required_keys |
| 合并前 | 必要子任务是否成功、同一字段是否冲突 | 缺失任务显式保留，冲突抛出异常 |

“格式正确”还不等于事实正确。当前实验中输入是可信结构化表格，质量分数由代码复制。接入模型后，还需验证候选 ID 是否属于输入集合、数值单位是否一致、引用是否支持结论。JSON Schema 能限制类型与必填字段，无法独自验证一段论文是否支持一个科学判断。

## 为什么不给子 Agent 整段历史

完整历史可能包含另一个用户的资料、与任务无关的讨论、已被推翻的中间结论。子 Agent 只需要候选的测量表和约束，就不必看到主 Agent 的所有对话。这个收缩既降低上下文干扰，也缩小数据可见范围。

本例在每次执行前对 `payload` 做深拷贝，所以 Worker 修改嵌套列表不会污染别人的输入。这是内存级别隔离，不是安全沙箱：同一 Python 进程中的恶意函数仍能访问全局变量和文件系统。面对不可信代码，要采用[工作区与隔离环境](../../09-runtime-harness-environment/01-concepts/04-workspaces-sandboxes-and-artifacts.md)。

## 错误也属于交付结果

正常结果是 `WorkerResult(status="ok", values=...)`；超时或错误以显式状态返回。不要使用 `{}` 同时表示“没有可行候选”“工具失败”和“没有运行”。这三种情况分别意味着可以形成否定结论、需要恢复、还没有证据。

生产契约还应增加 `schema_version`、父任务 ID、证据版本、成本统计、授权上下文 ID。授权上下文由运行时注入，不能由 Worker 自行声明“我是管理员”。增加字段时要说明谁填、谁验证、何时作废，而非只把字段名列满。

交接失败可直接复现：运行[测试](../05-code/multi-agent-runtime-python/tests/test_runtime.py)中的 `test_bad_route_contract_and_input_isolation`。它同时检查未知路由拒绝、错误返回键拒绝、原始输入没有被修改。异步取消语义参考[Python 文档](https://docs.python.org/3/library/asyncio-task.html)，更多来源见[索引](../references.md)。
