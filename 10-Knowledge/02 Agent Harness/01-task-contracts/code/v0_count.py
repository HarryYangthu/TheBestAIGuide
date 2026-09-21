"""The first runnable step: select completed checks and add their seconds."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / "examples/checks.json").read_text(encoding="utf-8"))
completed = [row for row in rows if row["status"] == "done"]
result = {"count": len(completed), "total_seconds": sum(row["seconds"] for row in completed)}
path = ROOT / "runs/preview.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(f"count={result['count']} total_seconds={result['total_seconds']}")
print("saved=runs/preview.json")
