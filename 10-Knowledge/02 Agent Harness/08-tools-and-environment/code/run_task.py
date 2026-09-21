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
    for name in ("samples.json", "steps.json"):
        shutil.copyfile(ROOT / "examples" / name, workspace / name)
    shutil.copyfile(ROOT / "notes.txt", workspace / "notes.txt")
    registry, trace = build_registry(workspace), []

    def call(name, **arguments):
        request = {"id": f"call-{len(trace) + 1}", "name": name, "arguments": arguments}
        result = registry.call(request)
        trace.append({"request": request, "result": result})
        if not result["ok"]:
            raise RuntimeError(result["error"])
        return result["data"]

    evidence = call("search_docs", query="报告", limit=5)
    notes = call("read_file", path="notes.txt")["text"]
    summary = json.loads(call("run_python", script="compute.py", input_path="samples.json")["stdout"])
    alternatives = {str(n): call("simulate_loop", input_path="steps.json", max_steps=n) for n in (2, 3)}
    report = f"# 笔记与统计报告\n\n{notes}\n样本数：{summary['count']}；均值：{summary['mean']}。\n\n"
    report += "| 步骤预算 | 已执行 | 剩余 | 完成 |\n|---:|---:|---:|---|\n"
    for n, value in alternatives.items():
        report += f"| {n} | {value['executed']} | {value['remaining']} | {value['completed']} |\n"
    report += "\n规则：" + "、".join(f"{m['path']}:{m['line']}" for m in evidence['matches']) + "。\n"
    call("write_file", path="report.md", text=report)
    result = {"summary": summary, "alternatives": alternatives, "calls": len(trace),
              "acceptance": summary == {"count": 2, "mean": 3.0}
              and alternatives['2']['remaining'] == 1 and alternatives['3']['completed']
              and (workspace / "report.md").read_text(encoding="utf-8") == report}
    (output / "trace.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in trace), encoding="utf-8")
    for name, data in (("result.json", result), ("schemas.json", registry.list_tools())):
        (output / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"mean={summary['mean']} calls={len(trace)} acceptance={result['acceptance']}")
    print(f"artifacts={output.as_posix()}")
    if not result["acceptance"]:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="runs/task")
    run(parser.parse_args().output)
