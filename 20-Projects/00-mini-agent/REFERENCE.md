# 参考结果与完成判定

参考文件由 demo 模式运行生成。动作顺序和字段值是预设的，文件读取、报告写入和验收由程序执行。运行环境与复现命令见 [verification.json](reference/verification.json)。

| 对照项目 | 参考结果 | 自己运行时是否应相同 |
| --- | --- | --- |
| [升级清单](reference/stage-07/report.md) | auth、timeout、retry 三项 | 固定教学任务必须相同，行序可不同 |
| [结构化清单](reference/stage-07/report.json) | 每项 before/after、新旧路径、行号及原文 | 值和引用必须正确 |
| [验收报告](reference/stage-07/acceptance.md) | 所有检查 PASS | 成功任务必须如此 |
| [课程完成表](reference/completion.md) | 七阶段与五实验 PASS | 必须如此 |
| [上下文长度与读取耗时](reference/completion.json) | 4980 → 1128 字符；并行与串行结果相同 | 固定上下文实验应相同；耗时可变化 |
| [执行轨迹](reference/stage-07/trace.jsonl) | 工具失败后继续读取，写报告后结束 | demo 顺序相同；live 不要求相同顺序 |
| [运行记录](reference/stage-07/run.json) | mode=demo、status=completed、tool_errors=1 | live 的 mode 必须是 live；调用数可变化 |
| [预算不足](reference/expected-budget-failure/acceptance.md) | FAIL，没有完整产物 | 故障实验应失败 |
| [错误引用](reference/expected-citation-failure/acceptance.md) | auth:source 为 FAIL | 故障实验应失败 |
| [子 Agent 回执](reference/subagents/delegation.json) | 两个指定文件均已读取，两个 Reader 均结束 | 可选实验应一致，不代表总结质量 |

错误引用案例在成功运行后，将 `report.json` 中新版认证方式的引用路径改为 `preview.md`，再重新验收。该目录的 trace、messages 和 Markdown 清单保留修改前的记录，JSON 清单保存修改后的输入。

`status=completed` 表示模型停止请求工具，`acceptance.json` 的 `passed` 表示验收结果。每次运行的耗时、输出目录和 live 工具调用顺序可能不同。

用自己的运行结果填写 [实验记录](EXPERIMENT.md)。
