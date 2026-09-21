"""Generate a policy from dev failures, evaluate, adopt, and support verified rollback."""
import argparse
import csv
import difflib
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from policy_engine import aggregate, validate_policy

ROOT = Path(__file__).resolve().parents[1]
ENGINE = Path(__file__).with_name("policy_engine.py")
BASELINE = {"normalize_status": False, "invalid_value": "reject", "include_negative": True}
TRIALS = 2


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def suite(split):
    return read_json(ROOT / "fixtures" / f"{split}.json")


def create_version(run, policy, evidence):
    validate_policy(policy)
    canonical = json.dumps(policy, sort_keys=True).encode()
    version = hashlib.sha256(canonical + sha(ENGINE).encode()).hexdigest()[:16]
    target = Path(run) / "versions" / version
    target.mkdir(parents=True, exist_ok=False)
    write_json(target / "policy.json", policy)
    (target / "policy_engine.py").write_bytes(ENGINE.read_bytes())
    write_json(target / "manifest.json", {"version": version, "policy_sha256": sha(target / "policy.json"),
               "engine_sha256": sha(ENGINE), "evidence": evidence, "created_at": datetime.now(timezone.utc).isoformat()})
    return version


def load_version(run, version):
    target = Path(run) / "versions" / version
    manifest = read_json(target / "manifest.json")
    if manifest["policy_sha256"] != sha(target / "policy.json"):
        raise ValueError("version policy hash mismatch")
    if manifest["engine_sha256"] != sha(ENGINE) or manifest["engine_sha256"] != sha(target / "policy_engine.py"):
        raise ValueError("version engine hash mismatch")
    policy = read_json(target / "policy.json")
    validate_policy(policy)
    canonical = json.dumps(policy, sort_keys=True).encode()
    if hashlib.sha256(canonical + sha(ENGINE).encode()).hexdigest()[:16] != version:
        raise ValueError("version content identity mismatch")
    return policy


def set_active(run, version, action, reason):
    run = Path(run)
    load_version(run, version)  # Validate before changing the pointer.
    path = run / "active.json"
    before = read_json(path)["version"] if path.exists() else None
    tmp = run / "active.tmp"
    write_json(tmp, {"version": version})
    os.replace(tmp, path)
    event = {"action": action, "from_version": before, "to_version": version,
             "reason": reason, "at": datetime.now(timezone.utc).isoformat()}
    with (run / "history.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def evaluate_case(case, policy, version, trial, target):
    target = Path(target)
    target.mkdir(parents=True, exist_ok=False)
    source = ROOT / "fixtures" / case["input"]
    write_json(target / "case.json", case)
    started = time.perf_counter()
    error = None
    error_type = None
    input_sha256 = None
    tool_calls = 0
    actual = None
    try:
        (target / "input.csv").write_bytes(source.read_bytes())
        input_sha256 = sha(target / "input.csv")
        tool_calls = 1
        value = aggregate(target / "input.csv", policy)
        write_json(target / "summary.json", value)
        # Acceptance consumes the actual artifact, not the function return.
        actual = read_json(target / "summary.json")
        accepted = set(actual) == set(case["expected"]) and all(type(actual[k]) is type(v) and actual[k] == v for k, v in case["expected"].items())
    except (ValueError, OSError, KeyError) as exc:
        accepted, error, error_type = False, str(exc), type(exc).__name__
    result = {"task_id": case["id"], "version": version, "trial": trial, "accepted": accepted,
              "actual": actual, "expected": case["expected"], "error": error, "error_type": error_type,
              "input_sha256": input_sha256, "checker_version": "order-contract-v1",
              "elapsed_ms": (time.perf_counter() - started) * 1000, "tool_calls": tool_calls,
              "model_cost_usd": None, "cost_source": "not_instrumented"}
    write_json(target / "result.json", result)
    return result


def evaluate(run, split, version):
    policy = load_version(run, version)
    rows = []
    for case in suite(split):
        for trial in range(TRIALS):
            rows.append(evaluate_case(case, policy, version, trial, Path(run) / "evaluations" / split / version / f"{case['id']}-{trial}"))
    return rows


def collect_failures(run, rows):
    """Collect only development evidence. Held-out suite is never read here."""
    cases = {c["id"]: c for c in suite("dev")}
    failures = []
    for row in rows:
        if row["accepted"] or row["trial"] != 0:
            continue
        case = cases[row["task_id"]]
        source = Path(run) / "evaluations/dev" / row["version"] / f"{case['id']}-0/input.csv"
        reason = "unclassified"
        evidence = []
        if row["error"] and row["error"].startswith("invalid_value:"):
            reason = "invalid_value"
            evidence = [row["error"]]
        elif row["error"]:
            evidence = [{"error_type": row["error_type"], "message": row["error"]}]
        else:
            with source.open(encoding="utf-8", newline="") as handle:
                evidence = [{"sample_id": r["sample_id"], "status": r["status"]} for r in csv.DictReader(handle)
                            if r["status"] != "valid" and r["status"].strip().casefold() == "valid"]
            if evidence:
                reason = "unrecognized_status"
        failures.append({"task_id": case["id"], "reason": reason, "evidence": evidence,
                         "input_sha256": row["input_sha256"], "result_file": f"evaluations/dev/{row['version']}/{case['id']}-0/result.json"})
    return failures


def propose(policy, failures):
    """Bounded rule-driven mutation. Does not claim open-ended learning."""
    candidate, changes = dict(policy), []
    reasons = {f["reason"] for f in failures}
    if "unrecognized_status" in reasons and not policy["normalize_status"]:
        candidate["normalize_status"] = True
        changes.append({"field": "normalize_status", "from": False, "to": True, "evidence_reason": "unrecognized_status"})
    if "invalid_value" in reasons and policy["invalid_value"] == "reject":
        candidate["invalid_value"] = "skip_and_record"
        changes.append({"field": "invalid_value", "from": "reject", "to": "skip_and_record", "evidence_reason": "invalid_value"})
    return candidate, changes


def gate(rows_by_split):
    checks, pairs = {}, {}
    for split, versions in rows_by_split.items():
        left, right = versions["baseline"], versions["candidate"]
        expected_keys = {(c["id"], trial) for c in suite(split) for trial in range(TRIALS)}
        def indexed(rows):
            result = {(r["task_id"], r["trial"]): r for r in rows}
            if len(result) != len(rows) or set(result) != expected_keys:
                raise ValueError("incomplete or duplicate evaluation pairs")
            return result
        baseline, candidate = indexed(left), indexed(right)
        deltas = []
        for key in sorted(expected_keys):
            b, c = baseline[key], candidate[key]
            if not b["input_sha256"] or not c["input_sha256"]:
                raise ValueError("missing input hash; comparison is invalid")
            if b["input_sha256"] != c["input_sha256"] or b["checker_version"] != c["checker_version"]:
                raise ValueError("evaluation conditions changed")
            deltas.append({"task_id": key[0], "trial": key[1], "delta": int(c["accepted"]) - int(b["accepted"])})
        pairs[split] = deltas
        checks[f"{split}_no_regressions"] = all(p["delta"] >= 0 for p in deltas)
        checks[f"{split}_resource_budget"] = all(r["tool_calls"] <= 1 for r in right)
    checks["dev_has_improvement"] = any(p["delta"] > 0 for p in pairs["dev"])
    checks["holdout_all_pass"] = all(r["accepted"] for r in rows_by_split["holdout"]["candidate"])
    return {"passed": all(checks.values()), "checks": checks, "pairs": pairs, "budget": {"max_tool_calls_per_run": 1},
            "cost_comparison": "unavailable: model_cost_usd not instrumented"}


def run_cycle(out, negative_filter=False):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / "suite-lock.json", {"dev_sha256": sha(ROOT / "fixtures/dev.json"), "holdout_sha256": sha(ROOT / "fixtures/holdout.json"),
               "trial_count": TRIALS, "engine_sha256": sha(ENGINE), "controller_sha256": sha(__file__),
               "inputs": {p.name: sha(p) for p in (ROOT / "fixtures").glob("*.csv")}})
    baseline = create_version(out, BASELINE, {"role": "baseline"})
    set_active(out, baseline, "initialize", "fixed baseline")
    dev_baseline = evaluate(out, "dev", baseline)
    failures = collect_failures(out, dev_baseline)
    write_json(out / "failures.json", failures)
    candidate_policy, changes = propose(BASELINE, failures)
    if negative_filter:
        candidate_policy["include_negative"] = False
        changes.append({"field": "include_negative", "from": True, "to": False, "evidence_reason": "explicit regression experiment"})
    if not changes:
        write_json(out / "decision.json", {"adopted": False, "reason": "no_supported_change"})
        return {"baseline": baseline, "candidate": None, "adopted": False}
    candidate = create_version(out, candidate_policy, {"failures_sha256": sha(out / "failures.json"), "changes": changes})
    before = (json.dumps(BASELINE, indent=2) + "\n").splitlines(keepends=True)
    after = (json.dumps(candidate_policy, indent=2) + "\n").splitlines(keepends=True)
    (out / "candidate.diff").write_text("".join(difflib.unified_diff(before, after, fromfile="baseline/policy.json", tofile="candidate/policy.json")), encoding="utf-8")
    # Candidate is frozen before the holdout suite is read for evaluation.
    dev_candidate = evaluate(out, "dev", candidate)
    holdout_baseline = evaluate(out, "holdout", baseline)
    holdout_candidate = evaluate(out, "holdout", candidate)
    rows = {"dev": {"baseline": dev_baseline, "candidate": dev_candidate},
            "holdout": {"baseline": holdout_baseline, "candidate": holdout_candidate}}
    decision = gate(rows)
    decision.update({"baseline": baseline, "candidate": candidate, "adopted": decision["passed"]})
    write_json(out / "decision.json", decision)
    if decision["passed"]:
        set_active(out, candidate, "adopt", "all predeclared evaluation gates passed")
    return decision


def rollback(run, reason):
    decision = read_json(Path(run) / "decision.json")
    if not decision.get("adopted"):
        raise ValueError("no adopted candidate to roll back")
    current = read_json(Path(run) / "active.json")["version"]
    if current != decision["candidate"]:
        raise ValueError("active version is not the candidate from this decision")
    set_active(run, decision["baseline"], "rollback", reason)
    return decision["baseline"]


def run_active(run, task_id, out):
    version = read_json(Path(run) / "active.json")["version"]
    policy = load_version(run, version)
    case = next(c for c in suite("dev") + suite("holdout") if c["id"] == task_id)
    return evaluate_case(case, policy, version, 0, out)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--out", type=Path, required=True)
    run_parser.add_argument("--negative-filter", action="store_true")
    active_parser = sub.add_parser("active")
    active_parser.add_argument("--run", type=Path, required=True)
    active_parser.add_argument("--task", default="whitespace")
    active_parser.add_argument("--out", type=Path, required=True)
    back_parser = sub.add_parser("rollback")
    back_parser.add_argument("--run", type=Path, required=True)
    back_parser.add_argument("--reason", required=True)
    args = parser.parse_args()
    if args.command == "run":
        result = run_cycle(args.out, args.negative_filter)
        print(f"adopted={result['adopted']}")
    elif args.command == "active":
        result = run_active(args.run, args.task, args.out)
        print(f"version={result['version']} accepted={result['accepted']}")
    else:
        print(f"rolled_back_to={rollback(args.run, args.reason)}")


if __name__ == "__main__":
    main()
