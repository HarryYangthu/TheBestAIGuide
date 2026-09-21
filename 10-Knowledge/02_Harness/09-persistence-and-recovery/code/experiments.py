"""Launch actual processes, preserve before/after observations and generate a report."""
import argparse
import json
from pathlib import Path
import platform
import sqlite3
import subprocess
import sys
import time

from runtime import Recipient, canonical, init, inspect, request_cancel

WORKER = Path(__file__).with_name("runtime.py")


def child(root, *options, expected=0):
    process = subprocess.run([sys.executable, str(WORKER), "run", "--root", str(root), *options],
                             capture_output=True, text=True, timeout=10)
    if process.returncode != expected:
        raise AssertionError(f"returncode={process.returncode}, expected={expected}: {process.stderr}")
    return process.returncode


def hard_timeout(root):
    process = subprocess.Popen([sys.executable, str(WORKER), "run", "--root", str(root),
                                "--hang-before-effect"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 5
        while not (root / "ready").exists():
            if process.poll() is not None or time.monotonic() > deadline:
                raise RuntimeError("worker did not reach the controlled wait")
            time.sleep(0.005)
        try:
            process.communicate(timeout=0.05)
            raise AssertionError("worker unexpectedly returned")
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)  # Reap the child before starting recovery.
        return {"killed": process.returncode != 0, "returncode": process.returncode}
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)


def run_all(out):
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    for name, crash, exit_code in [("normal", None, 0), ("after_item", "after_item", 71),
                                   ("after_prepare", "after_prepare", 70), ("after_effect", "after_effect", 72),
                                   ("after_receipt", "after_receipt", 73)]:
        root = out / name
        init(root)
        child(root, *(["--crash", crash] if crash else []), expected=exit_code)
        before = inspect(root)
        child(root)
        after = inspect(root)
        rows.append({"scenario": name, "exit_code": exit_code, "before": before, "after": after})
    for name, failure in [("retry_success", 2), ("retry_exhausted", 5)]:
        root = out / name
        init(root, max_attempts=3)
        child(root, "--fail-until", str(failure))
        before = inspect(root)
        child(root, "--fail-until", str(failure))  # No reset of attempt counters on restart.
        rows.append({"scenario": name, "before": before, "after": inspect(root)})
    root = out / "timeout"
    init(root)
    termination = hard_timeout(root)
    before = inspect(root)
    child(root)
    rows.append({"scenario": "timeout", "termination": termination, "before": before, "after": inspect(root)})
    root = out / "expired"
    init(root, ttl=-1)
    child(root)
    rows.append({"scenario": "expired", "before": inspect(root), "after": inspect(root)})
    for name, crash, exit_code in [("cancel_before", None, 0), ("cancel_after_item", "after_item", 71),
                                   ("cancel_after_effect", "after_effect", 72)]:
        root = out / name
        init(root)
        if crash:
            child(root, "--crash", crash, expected=exit_code)
        before = inspect(root)
        request_cancel(root)
        child(root)
        rows.append({"scenario": name, "before": before, "after": inspect(root)})
    # Same payload under a new operation identity creates a real second publication.
    recipient = Recipient(out / "key-scope.sqlite")
    payload = [{"item_index": 0, "item_id": "A", "mean": 3.0}]
    key = canonical(["tenant-a/reports/v1", "run-1", "publish", 1])
    first = recipient.publish(key, payload)
    same = recipient.publish(key, payload)
    mismatch_rejected = False
    try:
        recipient.publish(key, [{"item_index": 0, "item_id": "A", "mean": 4.0}])
    except ValueError:
        mismatch_rejected = True
    recipient.publish(canonical(["tenant-a/reports/v1", "run-2", "publish", 1]), payload)
    key_scope = {"same_key_same_receipt": first == same, "changed_payload_rejected": mismatch_rejected,
                 "effects_after_new_run_id": recipient.db.execute("SELECT count(*) FROM publications").fetchone()[0]}
    recipient.close()
    result = {"python": platform.python_version(), "sqlite": sqlite3.sqlite_version, "scenarios": rows, "key_scope": key_scope}
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    lines = ["# 故障恢复实验", "", f"Python {result['python']} / SQLite {result['sqlite']}", "",
             "| 场景 | 中断后下一项 | 中断后操作 | 恢复后状态 | 尝试数 | 发布数 | 提交样本数 | 验收 |",
             "|---|---:|---|---|---:|---:|---:|---|"]
    for row in rows:
        b, a = row["before"], row["after"]
        lines.append(f"| {row['scenario']} | {b['next_index']} | {b['operation_status']} | {a['status']} | {a['attempts']} | {a['effect_count']} | {a['item_commits']} | {a['acceptance']} |")
    lines += ["", "幂等键实验：", "", "```json", json.dumps(key_scope, indent=2, sort_keys=True), "```", ""]
    (out / "report.md").write_text("\n".join(lines))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = run_all(args.out)
    print(f"scenarios={len(result['scenarios'])} key_scope_checks=3")
    print(f"artifacts={args.out.as_posix()}")
