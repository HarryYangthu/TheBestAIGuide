"""Explicit task routing and progressive loading, without an LLM or installation."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from validate_output import check

ROOT = Path(__file__).resolve().parents[1]


def header(path):
    # Parse only the small frontmatter subset used by these supplied packages.
    # A host supporting arbitrary YAML should use a complete YAML parser.
    values = {}
    with path.open(encoding="utf-8") as stream:
        if stream.readline().strip() != "---":
            raise ValueError("missing frontmatter")
        for line in stream:
            if line.strip() == "---":
                break
            if ":" in line:
                key, value = line.strip().split(":", 1)
                if key in {"name", "description", "version"}:
                    values[key] = value.strip().strip('"')
    if set(values) != {"name", "description", "version"}:
        raise ValueError("incomplete skill metadata")
    if values["name"] != path.parent.name:
        raise ValueError("skill name must equal directory name")
    return values


def run(output, task="compare", packages=None, old_path=None, new_path=None):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    packages = Path(packages or ROOT / "examples/skills")
    old_path = Path(old_path or ROOT / "examples/inputs/v1.json")
    new_path = Path(new_path or ROOT / "examples/inputs/v2.json")
    trace = []

    def loaded(kind, path, text):
        trace.append({"event": "loaded", "kind": kind, "path": path,
                      "context_bytes": len(text.encode("utf-8")), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()})

    catalog = [header(path) for path in sorted(packages.glob("*/SKILL.md"))]
    loaded("catalog", "catalog", json.dumps(catalog, ensure_ascii=False))
    selected = next((item for item in catalog if item["name"] == "release-comparison"), None) if task == "compare" else None
    result = {"task": task, "selected": selected, "status": "skipped", "acceptance": None}
    if selected:
        package = packages / selected["name"]
        method = (package / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[2].strip()
        loaded("method", "SKILL.md", method)
        old = json.loads(old_path.read_text(encoding="utf-8"))
        new = json.loads(new_path.read_text(encoding="utf-8"))
        loaded("input", "old.json", json.dumps(old, ensure_ascii=False))
        loaded("input", "new.json", json.dumps(new, ensure_ascii=False))
        (output / "old.json").write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (output / "new.json").write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        units_needed = any(old["fields"].get(axis, {}).get("unit") != new["fields"].get(axis, {}).get("unit") for axis in ("timeout", "retry_limit", "batch_size"))
        template = package / "assets/report.md"
        script = package / "scripts/compare.py"
        command = [sys.executable, str(script), "--old", str(old_path), "--new", str(new_path), "--old-version", "1.0", "--new-version", "2.0", "--template", str(template), "--output", str(output / "comparison")]
        reference = package / "references/units.json"
        if units_needed and reference.exists():
            loaded("reference", "references/units.json", reference.read_text(encoding="utf-8"))
            command.extend(["--units", str(reference)])
        loaded("template", "assets/report.md", template.read_text(encoding="utf-8"))
        execution = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=5)
        trace.append({"event": "executed", "path": "scripts/compare.py", "sha256": hashlib.sha256(script.read_bytes()).hexdigest(), "returncode": execution.returncode, "stdout": execution.stdout, "stderr": execution.stderr})
        if execution.returncode == 0:
            acceptance = check(output / "comparison", old, new)
            (output / "comparison").mkdir(parents=True, exist_ok=True)
            (output / "comparison/acceptance.json").write_text(json.dumps(acceptance, indent=2) + "\n", encoding="utf-8")
            result.update(status="completed" if acceptance["passed"] else "acceptance_failed", acceptance=acceptance["passed"])
        else:
            result.update(status="script_rejected", acceptance=False)
    result["loaded_bytes"] = sum(event.get("context_bytes", 0) for event in trace)
    result["loaded_files"] = [event["path"] for event in trace if event["event"] == "loaded"]
    (output / "trace.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="runs/host")
    parser.add_argument("--task", choices=["compare", "polish"], default="compare")
    parser.add_argument("--packages")
    parser.add_argument("--old")
    parser.add_argument("--new")
    args = parser.parse_args()
    result = run(args.output, args.task, args.packages, args.old, args.new)
    print(f"status={result['status']} acceptance={result['acceptance']}")
    print(f"artifacts={args.output}")
    if result["status"] not in {"completed", "skipped"}:
        raise SystemExit(2)
