# 任务协议实验

数据由 code/experiments.py 实际执行生成。

| 场景 | 预期错误 | 实际错误 | 任务通过 | 检查符合预期 |
|---|---|---|---|---|
| valid | none | none | True | True |
| invalid_json | invalid_json | invalid_json | False | True |
| hours_as_text | input_schema | input_schema | False | True |
| duplicate_id | invalid_input | invalid_input | False | True |
| row_limit | constraint_violation | constraint_violation | False | True |
| no_done | empty_selection | empty_selection | False | True |
| missing_mean | output_schema | output_schema | False | True |
| wrong_total | acceptance_failed | acceptance_failed | False | True |
| wrong_task | acceptance_failed | acceptance_failed | False | True |
| wrong_digest | acceptance_failed | acceptance_failed | False | True |
| minimum_done | acceptance_failed | acceptance_failed | False | True |
| path_escape | constraint_violation | constraint_violation | False | True |
