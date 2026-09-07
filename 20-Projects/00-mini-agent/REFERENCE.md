# 参考结果与完成判定

这里的参考文件来自实际运行本项目的 demo 模式，不是人工编造的成功报告。demo 内部动作顺序和字段值是预设的，文件读取、报告写入、线程并发和独立验收是真实执行的。它不等于真实模型表现。运行环境与复现命令见 [verification.json](reference/verification.json)。

| 对照项目 | 参考结果 | 自己运行时是否应相同 |
| --- | --- | --- |
| [升级清单](reference/stage-07/report.md) | auth、timeout、retry 三项 | 固定教学任务必须相同，行序可不同 |
| [结构化清单](reference/stage-07/report.json) | 每项 before/after、新旧路径、行号及原文 | 值和引用必须正确 |
| [验收报告](reference/stage-07/acceptance.md) | 所有检查 PASS | 成功任务必须如此 |
| [课程完成表](reference/completion.md) | 七阶段与五实验 PASS | 必须如此 |
| [上下文与并行测量](reference/completion.json) | 4980 → 1128 字符；并行与串行结果相同 | 固定上下文实验应相同；时间可变化 |
| [执行轨迹](reference/stage-07/trace.jsonl) | 工具失败后继续读取，写报告后结束 | demo 顺序相同；live 不要求相同顺序 |
| [运行记录](reference/stage-07/run.json) | mode=demo、status=completed、tool_errors=1 | live 的 mode 必须是 live；调用数可变化 |
| [预算不足](reference/expected-budget-failure/acceptance.md) | FAIL，没有完整产物 | 故障实验应失败 |
| [错误引用](reference/expected-citation-failure/acceptance.md) | auth:source 为 FAIL | 故障实验应失败 |
| [子 Agent 回执](reference/subagents/delegation.json) | 两个指定文件均已读取，两个 Reader 均结束 | 可选实验应一致，不代表总结质量 |

错误引用案例是在成功运行后修改 `report.json` 的引用路径，再重新验收。因此该案例中的原始 trace、messages 和 Markdown 清单记录的是修改前运行，JSON 清单记录人为破坏后的输入。这是为了展示验收器能够识别产物损坏，不应当被当作一次模型自己生成错误引用的测量。

`status=completed` 仅代表模型停止请求工具；是否满足任务看 `acceptance.json` 的 `passed`。`live_model_validated=false` 明确表示本次参考执行没有调用真实模型。时间、绝对输出路径、模型 token 用量以及 live 动作顺序均不能逐字照抄参考值。

实际完成时，请保留自己的报告，并填写 [实验记录](EXPERIMENT.md)。只读这份参考结果，不等于已经执行或掌握了项目。
