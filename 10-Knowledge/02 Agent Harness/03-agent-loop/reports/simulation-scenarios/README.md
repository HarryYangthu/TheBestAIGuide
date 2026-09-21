# 执行循环仿真实验

预设响应控制循环分支；文件读写、Python 仿真和产物验收实际执行。

| 场景 | 停止原因 | 调用次数 | 验收 | 记录 |
|---|---|---:|---|---|
| normal | finish | 5 | True | [report.md](normal/report.md) |
| bad_tool | finish | 6 | True | [report.md](bad_tool/report.md) |
| early_finish | finish | 1 | False | [report.md](early_finish/report.md) |
| step_limit | step_limit | 3 | True | [report.md](step_limit/report.md) |
| empty_response | empty_response_limit | 2 | False | [report.md](empty_response/report.md) |
| duplicate_id | duplicate_call_id | 2 | False | [report.md](duplicate_id/report.md) |
| stale_test | finish | 6 | False | [report.md](stale_test/report.md) |
| failing_test | finish | 3 | False | [report.md](failing_test/report.md) |
| transient_model | finish | 6 | True | [report.md](transient_model/report.md) |
