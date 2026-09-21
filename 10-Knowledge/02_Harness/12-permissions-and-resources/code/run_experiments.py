import argparse
import asyncio
import json
from pathlib import Path
from control import Budget, Denied, Request, Runtime, principal


async def run(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    actor = principal()
    results, all_events = {}, {}

    runtime = Runtime(output / "permissions")
    deadline = asyncio.get_running_loop().time() + 5
    results["allowed"] = await runtime.execute(actor, Request("allowed", "read_record", "a1"), deadline=deadline)
    results["cross_tenant"] = await runtime.execute(actor, Request("cross", "read_record", "b1"), deadline=deadline)
    results["tool_denied"] = await runtime.execute(actor, Request("delete", "delete_record", "a1"), deadline=deadline)
    publish = Request("publish", "publish_record", "a1")
    results["approval_required"] = await runtime.execute(actor, publish, deadline=deadline)
    token = runtime.approvals.grant(actor, publish, runtime.project(publish), source="experiment_fixture")
    altered = Request("publish", "publish_record", "a1", steps=2)
    results["approval_mismatch"] = await runtime.execute(actor, altered, deadline=deadline, token=token)
    results["approved"] = await runtime.execute(actor, publish, deadline=deadline, token=token)
    results["approval_replay"] = await runtime.execute(actor, publish, deadline=deadline, token=token)
    all_events["permissions"] = runtime.events

    ledger = Budget(units=10, cost_micros=30, calls=5)
    await ledger.reserve("A", 8, 24)
    before = ledger.snapshot()
    try:
        await ledger.reserve("B", 6, 18)
    except Denied as exc:
        rejected = exc.code
    await ledger.settle("A", 3, 9)
    await ledger.reserve("B", 6, 18)
    await ledger.settle("B", 4, 12)
    results["reservation"] = {"before_settlement": before, "B_first_attempt": rejected, "after_settlement": ledger.snapshot()}
    all_events["reservation"] = ledger.events

    unknown = Budget(units=10, cost_micros=30)
    await unknown.reserve("remote", 8, 24)
    await unknown.mark_unknown("remote")
    results["unknown_usage"] = unknown.snapshot()
    all_events["unknown_usage"] = unknown.events

    runtime = Runtime(output / "concurrency", concurrency=2, budget=Budget(units=30, cost_micros=90))
    end = asyncio.get_running_loop().time() + 5
    work = [Request(f"worker-{i}", "read_record", "a1", steps=2, delay_ms=10) for i in range(4)]
    completed = await asyncio.gather(*(runtime.execute(actor, request, deadline=end) for request in work))
    results["concurrency"] = {"peak": runtime.peak, "completed": len([r for r in completed if r["status"] == "completed"]), **runtime.budget.snapshot()}
    all_events["concurrency"] = runtime.events

    runtime = Runtime(output / "deadline", concurrency=1)
    first = asyncio.create_task(runtime.execute(actor, Request("holder", "read_record", "a1", delay_ms=80), deadline=asyncio.get_running_loop().time() + 2))
    while runtime.active == 0:
        await asyncio.sleep(0)
    waiting = await runtime.execute(actor, Request("queued", "read_record", "a1"), deadline=asyncio.get_running_loop().time() + 0.01)
    await first
    results["queue_deadline"] = {"status": waiting["status"], "queued_started": any(e.get("event") == "started" and e.get("request") == "queued" for e in runtime.events), **runtime.budget.snapshot()}
    all_events["queue_deadline"] = runtime.events

    runtime = Runtime(output / "cancellation", concurrency=1)
    task = asyncio.create_task(runtime.execute(actor, Request("cancel", "read_record", "a1", steps=10, delay_ms=10), deadline=asyncio.get_running_loop().time() + 5))
    while runtime.active == 0:
        await asyncio.sleep(0)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    results["cancellation"] = {"status": "cancelled", "active": runtime.active, **runtime.budget.snapshot()}
    all_events["cancellation"] = runtime.events

    checks = {
        "allowed_projection": results["allowed"]["status"] == "completed" and set(results["allowed"]["data"]) == {"title", "checks_passed"},
        "data_scope": results["cross_tenant"]["status"] == "resource_denied",
        "tool_scope": results["tool_denied"]["status"] == "tool_denied",
        "approval_gate": results["approval_required"]["status"] == "approval_required",
        "approval_binding": results["approval_mismatch"]["status"] == "approval_mismatch",
        "approval_accept": results["approved"]["status"] == "completed" and (output / "permissions/a1.json").exists(),
        "approval_once": results["approval_replay"]["status"] == "approval_used",
        "budget_reserve": rejected == "budget_exhausted" and results["reservation"]["after_settlement"]["spent_units"] == 7,
        "unknown_held": results["unknown_usage"]["reserved_units"] == 8,
        "concurrency": results["concurrency"]["peak"] == 2 and results["concurrency"]["completed"] == 4,
        "deadline": waiting["status"] == "deadline_exceeded" and not results["queue_deadline"]["queued_started"],
        "cancel_release": results["cancellation"]["active"] == 0 and results["cancellation"]["reserved_units"] == 0,
    }
    (output / "result.json").write_text(json.dumps({"checks": checks, "scenarios": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "events.json").write_text(json.dumps(all_events, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = "# 权限与资源实验\n\n| 检查 | 通过 |\n|---|---|\n"
    report += "".join(f"| {key} | {value} |\n" for key, value in checks.items())
    report += "\n批准事件的来源为 experiment_fixture，是自动实验签发；没有把它记作真人批准。人工入口为 approval_cli.py。\n"
    (output / "report.md").write_text(report, encoding="utf-8")
    print(f"checks={len(checks)} passed={sum(checks.values())}")
    print(f"artifacts={output.as_posix()}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="runs/experiments")
    asyncio.run(run(parser.parse_args().output))
