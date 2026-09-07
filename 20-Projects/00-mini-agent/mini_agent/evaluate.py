"""Host-side fixture checks. The model has no tool exposing expected.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def evaluate(output, docs, expected=None):
    output, docs = Path(output), Path(docs)
    expected = expected or ROOT / "fixtures/expected.json"
    checks = []
    def check(name, passed):
        checks.append({"check": name, "passed": bool(passed)})
    try:
        state = json.loads((output / "run.json").read_text(encoding="utf-8"))
        report = json.loads((output / "report.json").read_text(encoding="utf-8"))
        rows = report["changes"]
        truth = json.loads(Path(expected).read_text(encoding="utf-8"))
        check("agent_finished", state["status"] == "completed")
        check("markdown_exists", (output / "report.md").is_file())
        check("exact_required_changes", sorted(row["id"] for row in rows) == sorted(truth))
        for key, target in truth.items():
            matches = [row for row in rows if row["id"] == key]
            row = matches[0] if len(matches) == 1 else {}
            check(key + ":values", row.get("before") == target["before"] and row.get("after") == target["after"])
            for field, path in (("old_source", "v1.md"), ("source", "v2.md")):
                citation = row.get(field, {})
                line = target["line"]
                correct = (docs / path).read_text(encoding="utf-8").splitlines()[line - 1]
                check(key + ":" + field, citation.get("path") == path and citation.get("line") == line
                      and citation.get("quote") == correct)
        check("format_matches_request", report.get("format") == state["format"])
        mode = state["mode"]
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        check("artifacts_readable_and_well_formed", False)
        mode = "unknown"
    result = {"passed": all(item["passed"] for item in checks), "mode": mode, "checks": checks,
              "scope": "固定教学任务的值、版本、逐字引用及结束状态；不代表通用研究能力。"}
    (output / "acceptance.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# 验收报告", "", f"模式：{mode}；结果：{'PASS' if result['passed'] else 'FAIL'}。", "",
             "| 检查 | 结果 |", "| --- | --- |"]
    lines += [f"| {item['check']} | {'PASS' if item['passed'] else 'FAIL'} |" for item in checks]
    lines += ["", result["scope"]]
    (output / "acceptance.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result
