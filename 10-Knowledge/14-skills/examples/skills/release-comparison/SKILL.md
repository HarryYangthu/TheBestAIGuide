---
name: release-comparison
description: 比较指定产品的两个正式版本，生成单位一致且保留双侧原文的参数变更表；仅润色现有文字时不适用。
metadata:
  version: "1.1.0"
---

# 正式版本参数比较

输入是两份结构化版本资料及明确的旧版、新版编号。先检查 product 相同、status 为 stable、version 与任务匹配。

1. 逐项核对 timeout、retry_limit、batch_size。每项同时保留旧值、新值、原单位、来源编号与原文。
2. 引文必须是资料正文中的完整行，并与结构化字段的 key、value、unit 一致。缺字段或引文不符时停止生成完成版报告。
3. 两侧单位不同时，才加载 `references/units.json`。按 scale 转为 canonical 单位；未知单位或量纲不同就返回单位错误。
4. 使用 `assets/report.md` 生成表格，调用 `scripts/compare.py`，不由调用者自由改写脚本的确定性数值。
5. 打开 comparison.json 和 report.md。检查版本、三项参数、双侧来源和转换后的数值；宿主调用验收器，passed 为真才交付。

在章节目录中的执行命令：

```bash
python examples/skills/release-comparison/scripts/compare.py --old examples/inputs/v1.json --new examples/inputs/v2.json --old-version 1.0 --new-version 2.0 --units examples/skills/release-comparison/references/units.json --template examples/skills/release-comparison/assets/report.md --output runs/direct
```

脚本退出 0 表示生成成功；退出 2 表示输入或证据不合格，查看输出目录的 error.json。输出目录必须尚不存在。它只读取显式传入的资料并写入该目录，不联网，不搜索其他版本，也不发布文件。

验收入口：`python code/validate_output.py --output runs/direct --old examples/inputs/v1.json --new examples/inputs/v2.json`。
