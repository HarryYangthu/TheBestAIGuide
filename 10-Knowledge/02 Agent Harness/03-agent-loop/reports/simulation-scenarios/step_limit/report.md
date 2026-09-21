# 本次运行记录

- 阶段：v4
- 执行方式：offline_scripted
- 模型：
- 状态：stopped / step_limit
- 模型请求尝试：3

## 输出

本次未生成正文。

## 当前文件检查

整体通过：True

| 检查项 | 通过 | 详情 |
|---|---|---|
| two_values | True | actual=3.0, expected=3 |
| negative_values | True | actual=0.0, expected=0 |
| singleton | True | actual=10.0, expected=10 |
| empty_raises | True | ValueError |
| simulation_artifacts | True | {"passed": true, "metrics": {"samples": 64, "window": 3, "input_mse": 0.09, "output_mse": 0.01008204565537388, "improvement_db": 9.506938496805722, "passed": true, "config_sha256": "102b87c25e277ce879f9ec0bd2c51492901f9be7dc891434266005d9513499de", "stats_sha256": "3c935b4c1acc33062edb51d263ba1dc9981a0bc0411d8238300d5021a6cc7420"}, "checks": {"metrics": true, "samples": true, "input_versions": true, "report": true}} |

文件 SHA-256：`3c935b4c1acc33062edb51d263ba1dc9981a0bc0411d8238300d5021a6cc7420`

## 代码变化

```diff
--- before/stats.py
+++ after/stats.py
@@ -1,2 +1,4 @@
 def mean(values):
-    return sum(values) / (len(values) + 1)
+    if not values:
+        raise ValueError('values must not be empty')
+    return sum(values) / len(values)
```

## 对照文件

- requests.jsonl：模型输入；离线场景保存预设模型收到的消息。
- responses.jsonl：API 模式保存原始响应；离线预设响应见 trace.jsonl。
- messages.json：循环保存的完整消息。
- trace.jsonl：执行事件。
- workspace/：本次使用与修改的文件。
- workspace/runs/simulation/：执行仿真后生成的指标、波形数据和报告；提前停止时可能不存在。
