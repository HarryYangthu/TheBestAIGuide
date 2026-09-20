"""汇总 runs/ 下各次实际运行；无需再次请求模型。"""
import json
from pathlib import Path
from artifacts import ROOT, write_json


def build_report(root=None):
    root = Path(root or ROOT / "runs")
    root.mkdir(parents=True, exist_ok=True)
    rows = []
    for file in sorted(root.glob("*/result.json")):
        r = json.loads(file.read_text(encoding="utf-8"))
        a = r.get("acceptance")
        rows.append({"run": file.parent.name, "stage": r.get("stage"), "mode": r.get("execution_mode"),
                     "reason": r.get("reason"), "model_calls": r.get("model_calls"),
                     "passed": a["passed"] if a is not None else None})
    lines = ["# 执行循环运行对照", "", "| 运行 | 阶段 | 执行方式 | 退出原因 | 调用次数 | 检查通过 |", "|---|---|---|---|---:|---|"]
    for r in rows:
        link = f"[{r['run']}]({r['run']}/report.md)"
        lines.append(f"| {link} | {r['stage']} | {r['mode']} | {r['reason']} | {r['model_calls']} | {r['passed'] if r['passed'] is not None else '不适用'} |")
    if not rows:
        lines += ["", "暂无运行记录，请先运行 code/v0_model_call.py 或后续阶段。"]
    (root / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(root / "comparison.json", rows)
    print(f"runs={len(rows)}")
    print(f"report={root / 'comparison.md'}")
    return rows


if __name__ == "__main__":
    build_report()
