import argparse
import json
from pathlib import Path
from host import ROOT, run


def experiments(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    for name, task, packages, new in (
        ("v1_units", "compare", ROOT / "examples/skills-v1", ROOT / "examples/inputs/v2.json"),
        ("v11_units", "compare", ROOT / "examples/skills", ROOT / "examples/inputs/v2.json"),
        ("polish", "polish", ROOT / "examples/skills", ROOT / "examples/inputs/v2.json"),
        ("preview", "compare", ROOT / "examples/skills", ROOT / "examples/inputs/preview.json"),
    ):
        result = run(output / name, task=task, packages=packages, new_path=new)
        rows.append({"case": name, **result})
    checks = {"old_version_rejects_units": rows[0]["status"] == "script_rejected",
              "updated_version_accepts": rows[1]["acceptance"] is True,
              "polish_loads_only_catalog": rows[2]["loaded_files"] == ["catalog"],
              "preview_rejected": rows[3]["status"] == "script_rejected"}
    (output / "result.json").write_text(json.dumps({"checks": checks, "runs": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = "# 技能包版本实验\n\n| 条件 | 技能版本 | 状态 | 验收 | 加载字节 |\n|---|---|---|---|---:|\n"
    for row in rows:
        version = row["selected"]["version"] if row["selected"] else "—"
        report += f"| {row['case']} | {version} | {row['status']} | {row['acceptance']} | {row['loaded_bytes']} |\n"
    report += "\n加载字节为 UTF-8 长度，不是 token。此实验使用显式 task 路由，没有测量模型选择技能的能力。\n"
    (output / "report.md").write_text(report, encoding="utf-8")
    print(f"checks={len(checks)} passed={sum(checks.values())}")
    print(f"artifacts={output.as_posix()}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="runs/experiments")
    experiments(parser.parse_args().output)
