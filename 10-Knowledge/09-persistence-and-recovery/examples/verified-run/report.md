# 故障恢复实验

Python 3.12.14 / SQLite 3.53.1

| 场景 | 中断后下一项 | 中断后操作 | 恢复后状态 | 尝试数 | 发布数 | 提交样本数 | 验收 |
|---|---:|---|---|---:|---:|---:|---|
| normal | 3 | confirmed | completed | 1 | 1 | 3 | True |
| after_item | 1 | None | completed | 1 | 1 | 3 | True |
| after_prepare | 3 | prepared | completed | 1 | 1 | 3 | True |
| after_effect | 3 | inflight | completed | 1 | 1 | 3 | True |
| after_receipt | 3 | confirmed | completed | 1 | 1 | 3 | True |
| retry_success | 3 | confirmed | completed | 3 | 1 | 3 | True |
| retry_exhausted | 3 | retryable | failed | 3 | 0 | 3 | False |
| timeout | 3 | inflight | completed | 2 | 1 | 3 | True |
| expired | 0 | None | timed_out | 0 | 0 | 0 | False |
| cancel_before | 0 | None | cancelled | 0 | 0 | 0 | False |
| cancel_after_item | 1 | None | cancelled | 0 | 0 | 1 | False |
| cancel_after_effect | 3 | inflight | cancelled | 1 | 1 | 3 | False |

幂等键实验：

```json
{
  "changed_payload_rejected": true,
  "effects_after_new_run_id": 2,
  "same_key_same_receipt": true
}
```
