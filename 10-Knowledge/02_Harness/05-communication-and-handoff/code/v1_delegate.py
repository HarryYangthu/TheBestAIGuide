"""The smallest delegation is a function call with a verifiable return value."""
import json
from pathlib import Path


def check_notes(task, snapshot):
    root = Path(__file__).resolve().parent.parent / "fixtures"
    path = (root / snapshot["path"]).resolve()
    if not path.is_relative_to(root.resolve()) or snapshot["path"] != task["path"]:
        raise ValueError("notes path denied")
    text = path.read_text(encoding="utf-8")
    found = sum(fact in text for fact in task["required_facts"])
    required = len(task["required_facts"])
    return {"path": task["path"], "required": required,
            "found": found, "missing": required - found,
            "evidence": {"version": snapshot["version"], "pointer": task["path"], "text": text}}


def main():
    task = json.loads(Path("fixtures/task.json").read_text(encoding="utf-8"))
    snapshot = json.loads(Path("fixtures/snapshot-ready.json").read_text(encoding="utf-8"))
    result = check_notes(task, snapshot)
    output = Path("runs/v1")
    output.mkdir(parents=True, exist_ok=True)
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"path={result['path']} required={result['required']} found={result['found']} missing={result['missing']}")
    print("owner=coordinator")
    print("artifacts=runs/v1")


if __name__ == "__main__":
    main()
