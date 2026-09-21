# 实际本地并行轨迹

成功子任务 1；失败子任务 1；span 11。

| 时长指标 | 毫秒 |
|---|---:|
| 根任务墙钟 | 62.932 |
| 两个子任务时长相加 | 122.857 |
| 子任务区间并集 | 61.622 |
| 重叠区间量 | 61.235 |

模型边界为明确选择的 fixture_replay；输入输出 token 来自手写协议样本。示例费用公式值不表示发生了真实调用或账单。实际模型成本为 null。

![timeline](timeline.png)

## 关联和错误

| span | parent | task | kind | status | error origin |
|---|---|---|---|---|---|
| s0001 task.batch | None | batch | task | error |  |
| s0002 model.plan.fixture_replay | s0001 | batch | model | ok |  |
| s0003 handoff.normal | s0001 | batch | handoff | ok |  |
| s0004 handoff.invalid | s0001 | batch | handoff | error | s0009 |
| s0005 task.normal | s0003 | normal | task | ok |  |
| s0006 tool.read_csv | s0005 | normal | tool | ok |  |
| s0007 task.invalid | s0004 | invalid | task | error | s0009 |
| s0008 tool.read_csv | s0007 | invalid | tool | ok |  |
| s0009 tool.aggregate | s0007 | invalid | tool | error | s0009 |
| s0010 tool.aggregate | s0005 | normal | tool | ok |  |
| s0011 acceptance.summary | s0005 | normal | acceptance | ok |  |

最早记录到的直接异常：invalid_value: file=invalid.csv row=3 sample=w2。

向父级追溯：s0009 → s0007 → s0004 → s0001。
