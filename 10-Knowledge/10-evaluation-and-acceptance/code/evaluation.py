"""Artifact acceptance and paired offline evaluation; no model/network calls."""
import argparse
import csv
import hashlib
import json
import time
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_VERSION = "summary-contract-v1"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cases():
    return read_json(ROOT / "fixtures/cases.json")


def aggregate(source, normalize=False):
    total, count = 0, 0
    with Path(source).open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            status = row["status"].strip().casefold() if normalize else row["status"]
            if status != "paid":
                continue
            try:
                amount = Decimal(row["amount"])
                if not amount.is_finite() or amount * 100 != (amount * 100).to_integral_value():
                    raise InvalidOperation
                cents = int(amount * 100)
            except (InvalidOperation, ValueError):
                raise ValueError(f"invalid_amount: order={row['order_id']}") from None
            total += cents
            count += 1
    return {"total_cents": total, "paid_rows": count, "rejected_rows": []}


def accept(artifact, expected):
    """Read the actual artifact. Return checks, never trust a runner's success flag."""
    path = Path(artifact)
    result = {"checker_version": CHECKER_VERSION, "accepted": False, "checks": {}, "artifact_sha256": None}
    if not path.exists():
        result["checks"]["file_exists"] = False
        return result
    result["artifact_sha256"] = digest(path)
    try:
        actual = read_json(path)
    except (ValueError, UnicodeError):
        result["checks"]["valid_json"] = False
        return result
    result["checks"]["object"] = isinstance(actual, dict)
    if not isinstance(actual, dict):
        return result
    result["checks"]["exact_fields"] = set(actual) == set(expected)
    for key, wanted in expected.items():
        result["checks"][key] = type(actual.get(key)) is type(wanted) and actual.get(key) == wanted
    result["accepted"] = all(result["checks"].values())
    return result


def run_one(case, variant, trial, target):
    target = Path(target)
    target.mkdir(parents=True, exist_ok=False)
    source = ROOT / "fixtures" / case["input"]
    (target / "input.csv").write_bytes(source.read_bytes())
    write_json(target / "case.json", case)
    started = time.perf_counter()
    error = None
    try:
        value = aggregate(target / "input.csv", normalize=variant == "candidate")
        write_json(target / "summary.json", value)
        exit_reason = "completed"
    except (ValueError, KeyError) as exc:
        exit_reason, error = "exception", {"type": type(exc).__name__, "message": str(exc)}
    elapsed_ms = (time.perf_counter() - started) * 1000
    check = accept(target / "summary.json", case["expected"])
    write_json(target / "acceptance.json", check)
    result = {
        "task_id": case["id"], "trial": trial, "variant": variant,
        "input_sha256": digest(target / "input.csv"), "checker_version": CHECKER_VERSION,
        "exit_reason": exit_reason, "accepted": check["accepted"], "error": error,
        "elapsed_ms": elapsed_ms, "tool_calls": 1,
        "model_cost_usd": None, "cost_source": "not_instrumented",
        "artifact_dir": str(target),
    }
    write_json(target / "result.json", result)
    return result


def summarize(rows, task_ids, trials):
    expected_keys = {(task, trial, variant) for task in task_ids for trial in range(trials) for variant in ("baseline", "candidate")}
    actual_keys = [(r["task_id"], r["trial"], r["variant"]) for r in rows]
    if len(actual_keys) != len(set(actual_keys)) or set(actual_keys) != expected_keys:
        raise ValueError("missing, extra or duplicate task/trial/variant rows")
    lookup = {(r["task_id"], r["trial"], r["variant"]): r for r in rows}
    paired, variants = [], {}
    for task in task_ids:
        for trial in range(trials):
            left, right = (lookup[(task, trial, v)] for v in ("baseline", "candidate"))
            if left["input_sha256"] != right["input_sha256"] or left["checker_version"] != right["checker_version"]:
                raise ValueError("pair uses a different input or checker")
            paired.append({"task_id": task, "trial": trial, "delta": int(right["accepted"]) - int(left["accepted"]),
                           "baseline": left["accepted"], "candidate": right["accepted"]})
    for variant in ("baseline", "candidate"):
        subset = [r for r in rows if r["variant"] == variant]
        known = [r["model_cost_usd"] for r in subset if r["model_cost_usd"] is not None]
        successes = sum(r["accepted"] for r in subset)
        variants[variant] = {"successes": successes, "denominator": len(subset), "success_rate": successes / len(subset),
                             "mean_elapsed_ms": sum(r["elapsed_ms"] for r in subset) / len(subset),
                             "tool_calls": sum(r["tool_calls"] for r in subset), "cost_known_rows": len(known),
                             "cost_coverage": len(known) / len(subset),
                             "known_cost_subtotal_usd": sum(known) if known else None,
                             "total_cost_usd": sum(known) if len(known) == len(subset) else None}
    counts = Counter(p["delta"] for p in paired)
    return {"task_count": len(task_ids), "trials": trials, "variants": variants, "paired": paired,
            "wins": counts[1], "ties": counts[0], "regressions": counts[-1],
            "delta_success_rate": variants["candidate"]["success_rate"] - variants["baseline"]["success_rate"],
            "release_gate": {"required_success_rate": 1.0, "passed": counts[-1] == 0 and variants["candidate"]["success_rate"] == 1.0}}


def build_report(out, task_ids, trials):
    # Re-read saved result files; report is not populated from an intended outcome.
    rows = [read_json(p) for p in sorted((out / "runs").glob("*/result.json"))]
    result = summarize(rows, task_ids, trials)
    write_json(out / "comparison.json", result)
    with (out / "results.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = ["task_id", "trial", "variant", "accepted", "exit_reason", "elapsed_ms", "tool_calls", "model_cost_usd"]
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 3.5))
    names = ["baseline", "candidate"]
    ax.bar(names, [result["variants"][v]["success_rate"] for v in names], color=["#6b7280", "#2563eb"])
    ax.set(ylim=(0, 1.1), ylabel="Accepted / all attempted runs", title=f"Same {len(task_ids)} tasks, {trials} repetitions")
    for i, variant in enumerate(names):
        r = result["variants"][variant]
        ax.text(i, r["success_rate"] + .025, f"{r['successes']}/{r['denominator']}", ha="center")
    fig.tight_layout()
    fig.savefig(out / "success-rate.png", dpi=160)
    plt.close(fig)
    lines = ["# 实际产物的配对评测", "", "| 版本 | 成功 / 全部尝试 | 成功率 | 成本已知行 | 总模型成本 |", "|---|---:|---:|---:|---|"]
    for name, value in result["variants"].items():
        lines.append(f"| {name} | {value['successes']}/{value['denominator']} | {value['success_rate']:.1%} | {value['cost_known_rows']} | unknown |")
    lines += ["", f"配对胜 / 平 / 退步：{result['wins']} / {result['ties']} / {result['regressions']}。", "",
              f"成功率差：{result['delta_success_rate']:+.1%}；发布门禁：{'pass' if result['release_gate']['passed'] else 'hold'}（要求全部任务达标且无回归）。",
              "", "每一行失败都保留在分母中。三次重复使用相同的确定性程序，不构成 18 个独立任务。成本未采集，不将其填成 0。", "", "![success-rate](success-rate.png)", "",
              "## 失败明细", "", "| 版本 | 任务 | trial | 原因 |", "|---|---|---:|---|"]
    for row in rows:
        if not row["accepted"]:
            reason = row["error"]["message"] if row["error"] else "artifact mismatch"
            lines.append(f"| {row['variant']} | {row['task_id']} | {row['trial']} | {reason} |")
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    parser.add_argument("--trials", type=int, default=3)
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("--trials must be positive")
    args.out.mkdir(parents=True, exist_ok=False)
    suite = cases()
    write_json(args.out / "suite.json", suite)
    write_json(args.out / "manifest.json", {"suite_sha256": digest(ROOT / "fixtures/cases.json"), "engine_sha256": digest(__file__), "checker_version": CHECKER_VERSION, "trials": args.trials})
    for trial in range(args.trials):
        # Alternate order to avoid always running one version first.
        for case in suite:
            for variant in (("baseline", "candidate") if trial % 2 == 0 else ("candidate", "baseline")):
                run_one(case, variant, trial, args.out / "runs" / f"{case['id']}-{trial}-{variant}")
    result = build_report(args.out, [c["id"] for c in suite], args.trials)
    for variant, value in result["variants"].items():
        print(f"{variant}: accepted={value['successes']}/{value['denominator']}")
    print(f"paired wins/ties/regressions={result['wins']}/{result['ties']}/{result['regressions']}")
    print(f"release_gate={'pass' if result['release_gate']['passed'] else 'hold'}")
    print(f"artifacts={args.out}")


if __name__ == "__main__":
    main()
