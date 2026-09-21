"""Parameterized deterministic comparison; invoked through ordinary process tools."""
import argparse
from decimal import Decimal
import json
from pathlib import Path

AXES = ("timeout", "retry_limit", "batch_size")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compare(old, new, old_version, new_version, units=None):
    if old["product"] != new["product"]:
        raise ValueError("product_mismatch")
    for document, version in ((old, old_version), (new, new_version)):
        if document["status"] != "stable" or document["version"] != version:
            raise ValueError("release_mismatch")
        for axis in AXES:
            field = document["fields"][axis]
            if type(field["value"]) not in (int, float) or field["value"] < 0:
                raise ValueError("invalid_value")
            expected = f"{axis} = {field['value']} {field['unit']}"
            if field["quote"] != expected or expected not in document["body"].splitlines():
                raise ValueError("evidence_mismatch")
    rows = []
    for axis in AXES:
        left, right = old["fields"][axis], new["fields"][axis]
        if left["unit"] == right["unit"]:
            a, b, unit = Decimal(str(left["value"])), Decimal(str(right["value"])), left["unit"]
        else:
            if units is None or left["unit"] not in units or right["unit"] not in units:
                raise ValueError("unit_conversion_required")
            u, v = units[left["unit"]], units[right["unit"]]
            if u["canonical"] != v["canonical"]:
                raise ValueError("incompatible_dimensions")
            a = Decimal(str(left["value"])) * Decimal(str(u["scale"]))
            b = Decimal(str(right["value"])) * Decimal(str(v["scale"]))
            unit = u["canonical"]
        rows.append({"axis": axis, "old": float(a), "new": float(b), "unit": unit,
                     "changed": a != b,
                     "old_evidence": {"source": old["source_id"], "version": old["version"], **left},
                     "new_evidence": {"source": new["source_id"], "version": new["version"], **right}})
    return {"product": old["product"], "old_version": old_version, "new_version": new_version, "rows": rows}


def render(result, template):
    rows = []
    for row in result["rows"]:
        old, new = row["old_evidence"], row["new_evidence"]
        rows.append(f"| {row['axis']} | {row['old']:g} | {row['new']:g} | {row['unit']} | {row['changed']} | {old['source']}@{old['version']}: `{old['quote']}` | {new['source']}@{new['version']}: `{new['quote']}` |")
    return template.format(product=result["product"], old_version=result["old_version"], new_version=result["new_version"], rows="\n".join(rows))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", required=True)
    parser.add_argument("--new", required=True)
    parser.add_argument("--old-version", required=True)
    parser.add_argument("--new-version", required=True)
    parser.add_argument("--units")
    parser.add_argument("--template", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    try:
        result = compare(load(args.old), load(args.new), args.old_version, args.new_version, load(args.units) if args.units else None)
    except (ValueError, KeyError, TypeError) as exc:
        (output / "error.json").write_text(json.dumps({"status": "rejected", "error": str(exc)}, indent=2) + "\n", encoding="utf-8")
        print(f"status=rejected reason={exc}")
        raise SystemExit(2)
    (output / "comparison.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "report.md").write_text(render(result, Path(args.template).read_text(encoding="utf-8")), encoding="utf-8")
    print(f"status=generated rows={len(result['rows'])}")


if __name__ == "__main__":
    main()
