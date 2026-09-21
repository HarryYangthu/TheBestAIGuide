import argparse
import json
import shutil
from pathlib import Path
from runtime import ROOT, build_registry


def run(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    workspace = output / "workspace"
    workspace.mkdir()
    shutil.copyfile(ROOT / "examples/demand.csv", workspace / "demand.csv")
    registry = build_registry(workspace)
    trace = []

    def call(name, **arguments):
        request = {"id": f"call-{len(trace) + 1}", "name": name, "arguments": arguments}
        result = registry.call(request)
        trace.append({"request": request, "result": result})
        if not result["ok"]:
            raise RuntimeError(result["error"])
        return result["data"]

    evidence = call("search_docs", query="库存", limit=5)
    source = call("read_file", path="demand.csv")
    computation = call("run_python", script="compute.py", input_path="demand.csv")
    summary = json.loads(computation["stdout"])
    alternatives = {str(q): call("simulate_inventory", input_path="demand.csv", initial=4, daily_delivery=q) for q in (2, 4)}
    feasible = [int(q) for q, v in alternatives.items() if v["lost"] == 0]
    selected = min(feasible, key=lambda q: alternatives[str(q)]["ending"]) if feasible else None
    report = "# 七天补货实验\n\n"
    report += f"输入：demand.csv，共 {summary['days']} 天，总需求 {summary['total']}。\n\n"
    report += "| 每日到货 | 缺货总量 | 期末库存 |\n|---:|---:|---:|\n"
    for q, value in alternatives.items():
        report += f"| {q} | {value['lost']} | {value['ending']} |\n"
    citations = "、".join(f"{item['path']}:{item['line']}" for item in evidence["matches"] if item["path"] == "policy.md")
    report += f"\n选择：每日到货 {selected} 件。规则出处：{citations}。\n"
    call("write_file", path="report.md", text=report)
    result = {"summary": summary, "alternatives": alternatives, "selected": selected,
              "acceptance": summary["days"] == 7 and summary["total"] == 29 and selected == 4
              and alternatives["2"]["lost"] == 11 and alternatives["4"]["ending"] == 3
              and (workspace / "report.md").read_text(encoding="utf-8") == report,
              "calls": len(trace)}
    (output / "trace.jsonl").write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in trace), encoding="utf-8")
    (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "schemas.json").write_text(json.dumps(registry.list_tools(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"selected={selected} calls={len(trace)} acceptance={result['acceptance']}")
    print(f"artifacts={output.as_posix()}")
    if not result["acceptance"]:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="runs/task")
    run(parser.parse_args().output)
