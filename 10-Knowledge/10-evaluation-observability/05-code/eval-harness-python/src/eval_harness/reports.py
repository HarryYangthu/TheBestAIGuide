from dataclasses import asdict
from pathlib import Path
from collections import defaultdict
import json
from .tasks import TrialResult


def summarize(results: list[TrialResult]) -> dict:
    if not results:
        raise ValueError("cannot summarize an empty suite")
    per_task, slices = defaultdict(list), defaultdict(list)
    for r in results:
        per_task[r.task_id].append(r.success)
        for tag in r.tags:
            slices[tag].append(r.success)
    return {
        "tasks": len(per_task), "trials": len(results),
        "successes": sum(r.success for r in results),
        "trial_success_rate": sum(r.success for r in results)/len(results),
        "macro_task_success_rate": sum(sum(v)/len(v) for v in per_task.values())/len(per_task),
        "system_errors": sum(r.status == "system_error" for r in results),
        "per_task": {key:{"successes":sum(v),"trials":len(v)} for key,v in sorted(per_task.items())},
        "slices": {key:sum(v)/len(v) for key,v in sorted(slices.items())},
        "uncertainty": "Not inferred: repeated deterministic fixtures are not independent population samples."
    }


def compare(baseline: list[TrialResult], candidate: list[TrialResult], max_drop: float = 0.0) -> dict:
    """严格配对教学门禁：关键任务全过，已过任务不退化，总成功率不下降。"""
    if not 0 <= max_drop <= 1:
        raise ValueError("max_drop must be in [0,1]")
    key = lambda r: (r.task_id, r.task_version, r.trial_index)
    a, b = {key(r):r for r in baseline}, {key(r):r for r in candidate}
    if not a or a.keys() != b.keys() or len(a) != len(baseline) or len(b) != len(candidate):
        raise ValueError("baseline and candidate must have matching unique task/version/trial keys")
    if any(a[k].critical != b[k].critical or a[k].tags != b[k].tags for k in a):
        raise ValueError("critical flags and slices must stay fixed across comparison")
    regressed = [k[0] for k in a if a[k].success and not b[k].success]
    improved = [k[0] for k in a if not a[k].success and b[k].success]
    critical_failures = sorted({r.task_id for r in candidate if r.critical and not r.success})
    delta = sum(r.success for r in candidate)/len(candidate)-sum(r.success for r in baseline)/len(baseline)
    return {"passed": not regressed and not critical_failures and delta >= -max_drop,
            "regressed_tasks": sorted(set(regressed)), "improved_tasks": sorted(set(improved)),
            "critical_failures": critical_failures, "success_rate_delta": delta,
            "policy": "strict paired regression; not a statistical non-inferiority test"}


def write_report(results: list[TrialResult], directory: str | Path) -> None:
    path = Path(directory)
    path.mkdir(parents=True,exist_ok=True)
    (path/"summary.json").write_text(json.dumps(summarize(results),indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (path/"trials.jsonl").write_text("".join(json.dumps(asdict(r),ensure_ascii=False)+"\n" for r in results),encoding="utf-8")
