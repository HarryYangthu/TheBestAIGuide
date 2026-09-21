"""Run one-variable changes against the same input; no model or network involved."""
import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from contracts import ROOT, execute, write_json

CASES = [
    ("valid", "none"), ("invalid_json", "invalid_json"),
    ("seconds_as_text", "input_schema"), ("duplicate_id", "invalid_input"),
    ("row_limit", "constraint_violation"), ("no_done", "empty_selection"),
    ("missing_mean", "output_schema"), ("wrong_total", "acceptance_failed"),
    ("wrong_task", "acceptance_failed"), ("wrong_digest", "acceptance_failed"),
    ("minimum_done", "acceptance_failed"), ("path_escape", "constraint_violation"),
]


def run_experiments(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    baseline_task = json.loads((ROOT / "examples/task.json").read_text(encoding="utf-8"))
    baseline_rows = json.loads((ROOT / "examples/checks.json").read_text(encoding="utf-8"))
    table = []
    for name, expected in CASES:
        case = output / name
        task, rows = copy.deepcopy(baseline_task), copy.deepcopy(baseline_rows)
        if name == "seconds_as_text": rows[0]["seconds"] = "2.5"
        if name == "duplicate_id": rows[1]["id"] = rows[0]["id"]
        if name == "row_limit": task["constraints"]["max_rows"] = 4
        if name == "no_done":
            for row in rows: row["status"] = "in_progress"
        if name == "minimum_done": task["acceptance"]["min_done"] = 4
        if name == "path_escape": task["input_path"] = "../checks.json"
        write_json(case / "input/task.json", task)
        write_json(case / "input/checks.json", rows)
        if name == "invalid_json": (case / "input/checks.json").write_text("[", encoding="utf-8")
        mutations = {
            "missing_mean": lambda x: x.pop("mean_seconds"),
            "wrong_total": lambda x: x.update(total_seconds=99),
            "wrong_task": lambda x: x.update(task_id="another-task"),
            "wrong_digest": lambda x: x.update(source_sha256="0" * 64),
        }
        record = execute(case / "input/task.json", case / "run", mutations.get(name))
        observed = record["error"]["code"] if record["error"] else "none"
        table.append(dict(case=name, expected=expected, observed=observed,
                          matched=expected == observed, accepted=record["status"] == "accepted"))
    write_json(output / "comparison.json", table)
    lines = ["# 任务协议实验", "", "数据由 code/experiments.py 实际执行生成。", "",
             "| 场景 | 预期错误 | 实际错误 | 任务通过 | 检查符合预期 |", "|---|---|---|---|---|"]
    for row in table:
        lines.append(f"| {row['case']} | {row['expected']} | {row['observed']} | {row['accepted']} | {row['matched']} |")
    (output / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return table


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    path = args.output or ROOT / "runs" / ("experiments-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    rows = run_experiments(path)
    print(f"cases={len(rows)} matched={sum(row['matched'] for row in rows)} accepted={sum(row['accepted'] for row in rows)}")
    print(f"artifacts={path}")
    raise SystemExit(0 if all(row["matched"] for row in rows) else 1)
