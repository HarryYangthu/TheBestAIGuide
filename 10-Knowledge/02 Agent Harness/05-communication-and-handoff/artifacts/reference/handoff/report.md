# 仿真任务通信记录

负责人：report-writer；epoch：2。

| 顺序 | 消息 | 接收决定 |
|---:|---|---|
| 1 | request-001 | delegated |
| 2 | message-002 | accepted_started |
| 3 | message-003 | accepted_result |
| 4 | — | handoff_offered |
| 5 | — | handoff_accepted |
| 6 | — | rejected_stale_owner |
| 7 | — | draft_created |

## 任务摘要

任务 report-017 要求 3 条事实，已找到 2 条，缺少 1 条。
任务：执行一次信号去噪仿真。
执行：python simulate.py --config simulation.json --output runs/simulation
产物：读取 runs/simulation/metrics.json，整理仿真结果。
待确认：退出码。
