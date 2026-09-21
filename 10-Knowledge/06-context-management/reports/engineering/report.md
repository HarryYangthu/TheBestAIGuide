# 上下文工程对照实验

固定任务：checkout production 发布审核；全部为本地机制实验。

| 策略 | 请求编码 token | 预算内 | 证据召回 | 证据精确率 |
|---|---:|---|---:|---:|
| current | 881 | True | 1.0 | 0.6666666666666666 |
| without_deduplication | 1036 | True | 1.0 | 0.6666666666666666 |
| without_log_compaction | 1816 | True | 1.0 | 0.6666666666666666 |
| full_authorized | 2400 | True | 1.0 | 0.2857142857142857 |
| minimal | 245 | True | 0.0 | None |

## 机制检查

| 检查 | 结果 |
|---|---|
| foreign_body_not_read | True |
| foreign_body_not_in_request | True |
| wrong_scope_excluded | True |
| duplicate_excluded | True |
| expired_excluded | True |
| conflict_rejected | True |
| overflow_rejected | True |
| failure_not_rewritten | True |
| failure_source_preserved | True |
| action_group_preserved | True |
| read_back_preserves_failure | True |
| policy_change_invalidates_key | True |
| refresh_missing_is_unknown | True |
| untrusted_note_remains_data | True |

结构化事实保留：1/3 → 3/3。

真实模型调用：0；位置效应与模型抵抗注入的结果需运行 live_evaluate.py。
