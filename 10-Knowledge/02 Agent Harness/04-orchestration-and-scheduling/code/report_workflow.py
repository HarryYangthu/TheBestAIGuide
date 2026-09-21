"""Read the task note, run local checks, and assemble a report through a DAG."""
import asyncio
import json
from copy import deepcopy
from pathlib import Path
from scheduler import Node
from stats import mean
from simulation import run_simulation, save_simulation

ROOT = Path(__file__).resolve().parent.parent


def load_inputs(cases="cases-v1.json"):
    root = ROOT / "fixtures"
    return {"notes": (root / "notes.txt").read_text(encoding="utf-8"),
            "cases": json.loads((root / cases).read_text(encoding="utf-8")),
            "policy": json.loads((root / "policy.json").read_text(encoding="utf-8"))}


def make_plan(case_version="1", empty_check=False):
    nodes = [Node("notes", (), "read"), Node("cases", (), "read", case_version),
             Node("policy", (), "read")]
    if empty_check:
        nodes.append(Node("empty_check", ("policy",), "calculate"))
    deps = ("notes", "cases", "empty_check") if empty_check else ("notes", "cases")
    return nodes + [Node("summary", deps, "calculate"),
                    Node("review", ("summary", "policy"), "review"),
                    Node("publish", ("review",), "publish")]


class ReportWorker:
    def __init__(self, inputs, delays=None):
        self.inputs = deepcopy(inputs)
        self.delays = delays or {"notes": .02, "cases": .03, "policy": .01}

    async def __call__(self, node, dependencies):
        await asyncio.sleep(self.delays.get(node.task_id, .001))
        if node.task_id == "notes":
            return {"text": self.inputs["notes"]}
        if node.task_id == "cases":
            data = self.inputs["cases"]
            for case in data["cases"]:
                if "expected" not in case:
                    raise ValueError("missing expected result")
            return deepcopy(data)
        if node.task_id == "policy":
            return deepcopy(self.inputs["policy"])
        if node.task_id == "empty_check":
            try:
                mean([])
            except ValueError:
                return {"passed": True}
            return {"passed": False}
        if node.task_id == "summary":
            cases = dependencies["cases"]["cases"]
            checks = [{**case, "actual": mean(case["values"])} for case in cases]
            passed = sum(c["actual"] == c["expected"] for c in checks)
            extra = dependencies.get("empty_check")
            if extra is not None:
                passed += int(extra["passed"])
            return {"notes": dependencies["notes"]["text"], "checks": checks,
                    "passed_checks": passed, "total_checks": len(checks) + int(extra is not None),
                    "case_version": dependencies["cases"]["version"],
                    "simulation": await run_simulation()}
        if node.task_id == "review":
            summary, policy = dependencies["summary"], dependencies["policy"]
            if not summary["simulation"]["metrics"]["passed"]:
                raise ValueError("simulation acceptance failed")
            if summary["passed_checks"] != summary["total_checks"]:
                raise ValueError("check failed")
            if summary["passed_checks"] < policy["minimum_passed"]:
                raise ValueError("insufficient checks")
            if policy["required_note"] not in summary["notes"]:
                raise ValueError("required note missing")
            return {"accepted": True, "summary": deepcopy(summary)}
        if node.task_id == "publish":
            return deepcopy(dependencies["review"])
        raise ValueError(f"unknown worker: {node.task_id}")


def save_run(output, scheduler, inputs, extra=None):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    result = scheduler.snapshot()
    result["accepted"] = result["results"].get("publish", {}).get("accepted", False)
    result.update(extra or {})
    for name, value in (("input.json", inputs), ("result.json", result)):
        (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "events.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in result["events"]), encoding="utf-8")
    lines = ["# 仿真与代码检查报告", "", f"accepted={result['accepted']}", "",
             "| 节点 | 状态 |", "|---|---|"]
    lines.extend(f"| {key} | {state} |" for key, state in result["states"].items())
    if result["accepted"]:
        data = result["results"]["publish"]["summary"]
        save_simulation(output, data["simulation"])
        metrics = data["simulation"]["metrics"]
        lines += ["", f"输入 MSE：{metrics['input_mse']:.6f}；输出 MSE：{metrics['output_mse']:.6f}。",
                  "[仿真报告](simulation/report.md)", "", "## 任务说明", "", data["notes"], "## 检查", "",
                  f"通过 {data['passed_checks']}/{data['total_checks']}；用例版本 {data['case_version']}。"]
    if result["errors"]:
        lines += ["", "## 错误", "", json.dumps(result["errors"], ensure_ascii=False)]
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result
