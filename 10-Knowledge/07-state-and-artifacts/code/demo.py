"""Run from the chapter directory. Each output directory must be new."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import platform
import shutil
import sqlite3
import subprocess
import sys
from threading import Barrier, Event

from artifacts import Artifacts, canonical
from state import Store, VersionConflict, complete, initial

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures"
REPAIRED = "def mean(values):\n    if not values:\n        raise ValueError('empty input')\n    return sum(values) / len(values)\n"


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def report(out, result):
    write_json(out / "result.json", result)
    lines = ["# 状态与产物实验", "", "| 字段 | 实际结果 |", "|---|---|"]
    lines += [f"| {key} | `{json.dumps(value, ensure_ascii=False, sort_keys=True)}` |"
              for key, value in result.items()]
    (out / "report.md").write_text("\n".join(lines) + "\n")


def minimal(out):
    shutil.copyfile(FIX / "stats.py", out / "stats.py")
    state = initial()
    state.update(status="running", next_step="check", refs={"code_path": "stats.py"})
    write_json(out / "state.json", state)
    result = {"status": state["status"], "acceptance": state["acceptance"], "code_exists": (out / "stats.py").exists()}
    report(out, result)
    return result


def run_check(out, artifacts, code, cases):
    workspace = out / "workspace"
    workspace.mkdir(exist_ok=True)
    (workspace / "stats.py").write_bytes(artifacts.read(code))
    (workspace / "cases.json").write_bytes(artifacts.read(cases))
    child = subprocess.run([sys.executable, str(ROOT / "code/check_code.py"),
                            str(workspace / "stats.py"), str(workspace / "cases.json")],
                           capture_output=True, text=True, check=True, timeout=5,
                           env={**__import__("os").environ, "PYTHONDONTWRITEBYTECODE": "1"})
    return json.loads(child.stdout)


def versions(out):
    objects = Artifacts(out / "objects")
    store = Store(out / "state.sqlite")
    try:
        state = initial()
        version = store.save(state, 0)
        cases = objects.put("cases", (FIX / "cases.json").read_bytes())
        plan1 = objects.put("plan", (FIX / "plan-v1.json").read_bytes())
        code1 = objects.put("code", (FIX / "stats.py").read_bytes(), ".py", {"plan": plan1})
        state.update(status="running", next_step="check", refs={"plan": plan1, "code": code1, "cases": cases})
        version = store.save(state, version)
        before = run_check(out, objects, code1, cases)
        evidence1 = objects.put("evidence", canonical(before), dependencies={"code": code1, "cases": cases})
        state["refs"]["evidence"] = evidence1
        state["acceptance"] = "failed"
        version = store.save(state, version)
        plan2 = objects.put("plan", (FIX / "plan-v2.json").read_bytes())
        code2 = objects.put("code", REPAIRED, ".py", {"plan": plan2})
        state["refs"].update(plan=plan2, code=code2)
        state["acceptance"] = "stale"
        stale = objects.stale(evidence1, state["refs"])
        version = store.save(state, version)
        after = run_check(out, objects, code2, cases)
        evidence2 = objects.put("evidence", canonical(after), dependencies={"code": code2, "cases": cases})
        state["refs"]["evidence"] = evidence2
        experiment = {"before_passed": sum(c["passed"] for c in before["cases"]),
                      "after_passed": sum(c["passed"] for c in after["cases"]),
                      "passed": after["passed"]}
        state["refs"]["experiment"] = objects.put("experiment", canonical(experiment),
                                                   dependencies={"evidence": evidence2})
        state = complete(state, objects)
        version = store.save(state, version)
        write_json(out / "state.json", dict(version=version, **state))
        write_json(out / "comparison.json", {"before": before, "after": after,
                                              "old_evidence": evidence1, "stale_dependencies": stale})
        result = {"before_passed": experiment["before_passed"], "after_passed": experiment["after_passed"],
                  "stale_dependencies": stale, "state_version": version, "status": state["status"]}
        report(out, result)
        return result
    finally:
        store.close()


def conflict(out):
    database = out / "state.sqlite"
    store = Store(database)
    store.save(initial(), 0)
    store.close()
    barrier, a_done = Barrier(2), Event()

    def worker(name):
        connection = Store(database)
        try:
            version, state = connection.load()
            barrier.wait(timeout=10)  # Both readers really see version 1.
            state["status"] = "running"
            if name == "A":
                state["next_step"] = "verify"
                connection.save(state, version)
                a_done.set()
                return "saved"
            if not a_done.wait(timeout=10):
                raise TimeoutError("writer A did not commit")
            state["budget"] -= 1
            try:
                connection.save(state, version)
                raise AssertionError("stale write was accepted")
            except VersionConflict as error:
                message = str(error)
            fresh_version, fresh = connection.load()
            # Reapply the intended delta to freshly read state; not the old snapshot.
            fresh["budget"] -= 1
            connection.save(fresh, fresh_version)
            return message
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(worker, "A")
        b = pool.submit(worker, "B")
        a.result(timeout=15)
        rejection = b.result(timeout=15)
    store = Store(database)
    version, state = store.load()
    store.close()
    # Counterexample: the same stale snapshots overwrite the whole JSON file.
    old_a, old_b = initial(), initial()
    old_a.update(status="running", next_step="verify")
    write_json(out / "unversioned.json", old_a)
    old_b.update(status="running", budget=3)
    write_json(out / "unversioned.json", old_b)
    write_json(out / "state.json", dict(version=version, **state))
    result = {"conflict": rejection, "unversioned_next_step": old_b["next_step"],
              "cas_next_step": state["next_step"], "budget": state["budget"], "state_version": version}
    report(out, result)
    return result


def experiments(out):
    result = {"python": platform.python_version(), "sqlite": sqlite3.sqlite_version, "scenarios": {}}
    for name, function in [("minimal", minimal), ("versions", versions), ("conflict", conflict)]:
        directory = out / name
        directory.mkdir()
        result["scenarios"][name] = function(directory)
    report(out, result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", choices=["minimal", "versions", "conflict", "experiments"])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    result = globals()[args.scenario](args.out)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    print(f"artifacts={args.out.as_posix()}")
