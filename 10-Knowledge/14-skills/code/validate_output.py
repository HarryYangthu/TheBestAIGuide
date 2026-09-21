"""Independent artifact acceptance; never treats process exit 0 as sufficient."""
import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


def _check(output, old, new):
    output = Path(output)
    result = json.loads((output / "comparison.json").read_text(encoding="utf-8"))
    report = (output / "report.md").read_text(encoding="utf-8")
    title = f"# {old['product']}：{old['version']} → {new['version']}"
    checks = {"report_title": bool(report.splitlines()) and report.splitlines()[0] == title,
              "versions": result["old_version"] == old["version"] and result["new_version"] == new["version"],
              "product": result["product"] == old["product"] == new["product"],
              "stable": old["status"] == new["status"] == "stable",
              "axes": [r["axis"] for r in result["rows"]] == ["timeout", "retry_limit", "batch_size"]}
    conversion = {"s": ("s", Decimal(1)), "ms": ("s", Decimal("0.001")), "attempts": ("attempts", Decimal(1)), "items": ("items", Decimal(1))}
    for row in result["rows"]:
        axis = row["axis"]
        for side, source in (("old", old), ("new", new)):
            evidence = row[f"{side}_evidence"]
            original = source["fields"][axis]
            supported = evidence == {"source": source["source_id"], "version": source["version"], **original}
            supported = supported and original["quote"] in source["body"].splitlines()
            supported = supported and original["quote"] == f"{axis} = {original['value']} {original['unit']}"
            units_equal = old["fields"][axis]["unit"] == new["fields"][axis]["unit"]
            if units_equal:
                expected_unit, factor = original["unit"], Decimal(1)
            else:
                expected_unit, factor = conversion[original["unit"]]
            numeric = Decimal(str(row[side])) == Decimal(str(original["value"])) * factor
            checks[f"{axis}_{side}"] = supported and numeric and row["unit"] == expected_unit
            checks[f"{axis}_{side}_report"] = f"{evidence['source']}@{evidence['version']}: `{evidence['quote']}`" in report
        checks[f"{axis}_changed"] = row["changed"] == (row["old"] != row["new"])
        checks[f"{axis}_report_values"] = f"| {axis} | {row['old']:g} | {row['new']:g} | {row['unit']} | {row['changed']} |" in report
    return {"passed": all(checks.values()), "checks": checks}


def check(output, old, new):
    try:
        return _check(output, old, new)
    except (OSError, ValueError, KeyError, TypeError, IndexError, InvalidOperation) as exc:
        return {"passed": False, "checks": {"artifact_structure": False},
                "errors": [{"code": "invalid_artifact", "type": type(exc).__name__}]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--old", required=True)
    parser.add_argument("--new", required=True)
    args = parser.parse_args()
    load = lambda path: json.loads(Path(path).read_text(encoding="utf-8"))
    result = check(args.output, load(args.old), load(args.new))
    (Path(args.output) / "acceptance.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"acceptance={result['passed']} checks={len(result['checks'])}")
    raise SystemExit(0 if result["passed"] else 1)
