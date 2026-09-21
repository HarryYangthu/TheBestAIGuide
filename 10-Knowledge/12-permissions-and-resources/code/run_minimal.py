import json
from pathlib import Path
from control import ROOT, Denied, Request, Runtime, principal

runtime = Runtime(ROOT / "runs/minimal")
results = []
for resource in ("a1", "b1"):
    try:
        runtime.authorize(principal(), Request(resource, "read_record", resource))
        status = "allowed"
    except Denied as exc:
        status = exc.code
    results.append({"resource": resource, "status": status})
    print(f"{resource}={status}")
(runtime.output / "result.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print("artifacts=runs/minimal")
