# 仿真执行器：1.0 → 2.0

| 参数 | 旧值 | 新值 | 统一单位 | 变化 | 旧版证据 | 新版证据 |
|---|---:|---:|---|---|---|---|
| timeout | 30 | 10 | s | True | manual-v1@1.0: `timeout = 30 s` | manual-v2@2.0: `timeout = 10000 ms` |
| retry_limit | 3 | 2 | attempts | True | manual-v1@1.0: `retry_limit = 3 attempts` | manual-v2@2.0: `retry_limit = 2 attempts` |
| batch_size | 100 | 200 | items | True | manual-v1@1.0: `batch_size = 100 items` | manual-v2@2.0: `batch_size = 200 items` |

所有证据均来自指定已确认版本。单位换算使用随包版本化的单位表。
