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
    shutil.copyfile(ROOT / "examples/samples.json", workspace / "samples.json")
    shutil.copyfile(ROOT / "examples/steps.json", workspace / "steps.json")
    registry = build_registry(workspace)
    cases = [
        ("search", "search_docs", {"query": "报告", "limit": 1}, None),
        ("bad_limit", "search_docs", {"query": "报告", "limit": 200}, "invalid_arguments"),
        ("bool_limit", "search_docs", {"query": "报告", "limit": True}, "invalid_arguments"),
        ("escape", "read_file", {"path": "../outside.txt"}, "path_denied"),
        ("missing", "read_file", {"path": "missing.txt"}, "not_found"),
        ("python", "run_python", {"script": "compute.py", "input_path": "samples.json"}, None),
        ("budget2", "simulate_loop", {"input_path": "steps.json", "max_steps": 2}, None),
        ("budget3", "simulate_loop", {"input_path": "steps.json", "max_steps": 3}, None),
    ]
    rows = []
    for case, name, arguments, expected in cases:
        result = registry.call({"id": case, "name": name, "arguments": arguments})
        actual = None if result["ok"] else result["error"]["code"]
        rows.append({"case": case, "expected_error": expected, "passed": actual == expected, "result": result})
    (output / "result.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = "# 工具实验\n\n| case | ok | error | passed |\n|---|---|---|---|\n"
    for row in rows:
        result = row["result"]
        report += f"| {row['case']} | {result['ok']} | {'' if result['ok'] else result['error']['code']} | {row['passed']} |\n"
    docker = "可用" if shutil.which("docker") else "不可用"
    report += f"\n本入口未执行容器；当前 Docker CLI {docker}。运行 code/run_container.py 可另外生成结果。\n"
    (output / "report.md").write_text(report, encoding="utf-8")
    print(f"cases={len(rows)} passed={sum(row['passed'] for row in rows)}")
    print(f"artifacts={output.as_posix()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="runs/experiments")
    run(parser.parse_args().output)
