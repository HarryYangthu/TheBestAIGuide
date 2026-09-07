# 跨模块JSON交换契约

> 状态：verified | 2026-09-06，Python jsonschema与TS AJV对同一12个正反例校验通过

这些是TheBestAIGuide内部v1教学对象，采用JSON Schema 2020-12；不等同于MCP/A2A在线消息。各模块内部可以使用不同数据类，跨模块传输时显式映射。

| Schema | 必填字段 | 用途 |
| --- | --- | --- |
| [ToolCall](tool-call.schema.json) | call_id、name、arguments | 动作请求 |
| [ToolResult](tool-result.schema.json) | call_id、ok，以及data或error | 成功失败互斥；error含code/retryable |
| [AgentState](agent-state.schema.json) | task、run_id、status、steps、observations、answer、stop_reason | 最小Loop状态快照 |
| [TraceEvent](trace-event.schema.json) | run_id、seq、kind、data | 有序运行事件；seq从0开始 |
| [EvalTask](eval-task.schema.json) | task_id、input、expected、metadata | 任务、验收期望及数据来源 |
| [TrialResult](trial-result.schema.json) | task_id、trial_id、status、score、output、errors | 单次实验结果，score限制0到1 |

每个对象有[正例与反例](examples/)，共 12 个基础对象；另有 [47 个边界反例](examples/boundaries.json)，覆盖缺字段、错类型、空 ID、非法状态/分数与成功失败互斥。Python 和 TS 当前都读取这两组文件，共 59 项对象判定。Schema校验仅检查数据形状，不保证引用正确、身份可信或任务成功。

从本目录运行`python validate_examples.py`（需安装`jsonschema`）。TS侧在[tool-runtime-typescript](../tool-runtime-typescript/README.md)运行`npm test`，共用相同JSON文件，不维护两份手写类型验证规则。

修改字段含义、枚举或必填项应升级契约并提供适配；本版本没有自动schema迁移器。
