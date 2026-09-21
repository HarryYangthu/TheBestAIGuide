---
name: release-comparison
description: 比较指定产品的两个正式版本，生成单位一致且保留双侧原文的参数变更表；仅润色现有文字时不适用。
metadata:
  version: "1.0.0"
---

# 正式版本参数比较

先确认产品相同、两个版本都是 stable，版本编号与任务一致。
逐项提取 timeout、retry_limit、batch_size；每项保留双侧原文与来源编号。
核对引文与结构化的 key、value、unit 一致。两侧单位不同则返回 unit_conversion_required，不直接比较数字。
使用 assets/report.md；运行 scripts/compare.py，传入 --old、--new、--old-version、--new-version、--template、--output。
脚本退出 0 后检查 comparison.json 与 report.md，交给宿主验收器。缺证据时退出 2，不生成完成报告。
本版没有单位转换表；需要跨单位比较时先升级方法包。
