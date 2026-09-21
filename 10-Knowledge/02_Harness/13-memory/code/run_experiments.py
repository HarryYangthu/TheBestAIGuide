"""Run distinct interpreter processes so persistence is observable."""
import json
import subprocess
import sys
from datetime import datetime, timezone

from memory import ROOT, save_json


def run():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = ROOT / "runs" / stamp
    db = run_dir / "memory.sqlite3"
    stages = [
        ("learn", "learn", []),
        ("reuse", "review", []),
        ("no-trigger", "review", ["--task", "task-no-trigger.json"]),
        ("conflict", "conflict", []),
        ("disputed", "review", []),
        ("update", "update", []),
        ("new-policy", "review", ["--task", "task-third.json"]),
        ("expiry", "expire", ["--as-of", "2026-10-02"]),
        ("expired", "review", ["--task", "task-expired.json"]),
        ("forget", "forget", ["--id", "pref-language"]),
    ]
    logs = []
    for name, action, extra in stages:
        cmd = [sys.executable, str(ROOT / "code/session.py"), action,
               "--db", str(db), "--out", str(run_dir / name), *extra]
        completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logs.append({"stage": name, "argv": cmd, "stdout": completed.stdout, "returncode": completed.returncode})
    save_json(run_dir / "processes.json", logs)
    report = "# 跨次任务复用实验\n\n| 阶段 | 独立进程输出 |\n|---|---|\n"
    report += "\n".join(f"| {r['stage']} | {r['stdout'].strip().replace(chr(10), '; ')} |" for r in logs)
    (run_dir / "comparison.md").write_text(report + "\n", encoding="utf-8")
    reuse = json.loads((run_dir / "reuse/result.json").read_text())
    disputed = json.loads((run_dir / "disputed/result.json").read_text())
    updated = json.loads((run_dir / "new-policy/result.json").read_text())
    final_rows = json.loads((run_dir / "forget/store-snapshot.json").read_text())
    acceptance = {
        "second_process_reused_fact": any(r["id"] == "fact-timeout-v3" for r in reuse["selected"]),
        "current_instruction_won": reuse["effective_preferences"]["language"] == "en",
        "conflicting_fact_withheld": not any(r["key"] == "timeout_ms" for r in disputed["selected"]),
        "updated_fact_used": any(r["key"] == "timeout_ms" and r["value"] == 2000 for r in updated["selected"]),
        "forgotten_payload_absent": not any(r["id"] == "pref-language" for r in final_rows),
    }
    save_json(run_dir / "result.json", acceptance)
    print("processes=" + str(len(logs)))
    print("acceptance=" + str(all(acceptance.values())))
    print("artifacts=" + str(run_dir.relative_to(ROOT)))
    return run_dir, acceptance


if __name__ == "__main__":
    run()
