"""Execute chapter-owned fixture code in a child process; not a hostile-code sandbox."""
import argparse
import importlib.util
import json
from pathlib import Path


def check(path, cases):
    spec = importlib.util.spec_from_file_location("candidate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = []
    for case in cases:
        try:
            actual = module.mean(case["values"])
            passed = "error" not in case and actual == case["expected"]
            observed = actual
        except Exception as error:
            observed = type(error).__name__
            passed = observed == case.get("error")
        rows.append({"input": case["values"], "observed": observed, "passed": passed})
    return {"passed": all(r["passed"] for r in rows), "cases": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("code", type=Path)
    parser.add_argument("cases", type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.code, json.loads(args.cases.read_text())), sort_keys=True))
