# 模型接入协议实验

由显式协议样本实际回放生成；未调用模型。

| 场景 | 预期 | 实际 | 观察到 total_tokens | 符合预期 |
|---|---|---|---|---|
| interleaved_tools | none | none | True | True |
| missing_finish | incomplete_response | incomplete_response | False | True |
| missing_usage | none | none | False | True |
| length_limit | output_truncated | output_truncated | False | True |
| broken_arguments | invalid_arguments | invalid_arguments | False | True |

三个请求的已知 token 合计与覆盖情况：

| 字段 | 已知合计 | 有值请求 | 缺失请求 |
|---|---:|---:|---:|
| prompt_tokens | 12 | 2 | 1 |
| completion_tokens | 2 | 1 | 2 |
| total_tokens | 10 | 1 | 2 |

结构化字段通过 Schema，但事实验收：False。
