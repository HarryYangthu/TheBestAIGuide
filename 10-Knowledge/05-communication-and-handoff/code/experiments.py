import argparse
import asyncio
from copy import deepcopy
import json
from pathlib import Path
from protocol import Case, LocalBus, exchange, inventory_worker, save_run
from v3_handoff import run_handoff


async def run_messages(output):
    case = Case()
    bus = LocalBus(["coordinator", "inventory-worker"])
    checks = []
    def check(name, actual, expected):
        checks.append({"case": name, "actual": actual, "expected": expected,
                       "passed": actual == expected})

    first = case.delegate("coordinator", "inventory-unavailable.json")
    failed, decisions = await exchange(case, first, bus)
    check("failure_reported", decisions[-1], "accepted_failure")
    check("incomplete_after_failure", case.merge(["read-stock"])["complete"], False)
    second = case.delegate("coordinator", "inventory-ready.json")
    result, decisions = await exchange(case, second, bus)
    check("retry_result", decisions[-1], "accepted_result")

    async def deliver(message):
        await bus.send(message)
        return case.receive(await bus.receive("coordinator"))

    check("duplicate_result", await deliver(result), "duplicate")
    conflict = deepcopy(result)
    conflict["payload"]["shortage"] = 0
    check("same_id_changed", await deliver(conflict), "conflicting_message")
    late = case.response(first, "failure", failed["payload"])
    check("late_attempt", await deliver(late), "stale_attempt")
    check("late_started", await deliver(case.response(second, "started", {})), "late_progress")
    wrong = case.response(second, "result", result["payload"])
    wrong["correlation_id"] = "another-request"
    check("wrong_correlation", await deliver(wrong), "wrong_correlation")
    old_input = case.response(second, "result", result["payload"])
    old_input["input_version"] = "stock-1"
    check("old_input", await deliver(old_input), "stale_input")
    check("new_id_same_result", await deliver(case.response(second, "result", result["payload"])), "duplicate_outcome")
    changed_result = deepcopy(result["payload"])
    changed_result["shortage"] = 0
    check("new_id_conflicting_result", await deliver(case.response(second, "result", changed_result)), "conflicting_outcome")
    await bus.send(second)
    await inventory_worker(case, await bus.receive("inventory-worker"), bus)
    duplicate_reply = case.receive(await bus.receive("coordinator"))
    check("duplicate_request_reply", duplicate_reply, "duplicate")
    check("worker_execution_count", bus.worker_executions, 2)
    check("merged_shortage", case.merge(["read-stock"])["results"]["read-stock"]["shortage"], 1)
    save_run(output, case, bus, {"checks": checks})
    return checks


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="runs/experiments")
    args = parser.parse_args()
    output = Path(args.output)
    checks = await run_messages(output / "delivery")
    handoff = await run_handoff(output / "handoff")
    for name, actual, expected in [
        ("offer_keeps_owner", handoff["before_accept"]["owner"], "coordinator"),
        ("handoff_owner", handoff["owner"], "fulfillment-specialist"),
        ("handoff_epoch", handoff["epoch"], 2),
        ("old_owner_rejected", handoff["old_action"], "rejected_stale_owner"),
        ("new_owner_acts", handoff["new_action"], "draft_created"),
    ]:
        checks.append({"case": name, "actual": actual, "expected": expected, "passed": actual == expected})
    (output / "comparison.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# 通信与交接实验", "", "| 场景 | 实际决定 | 通过 |", "|---|---|---|"]
    lines.extend(f"| {row['case']} | {row['actual']} | {row['passed']} |" for row in checks)
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    delivery = json.loads((output / "delivery" / "result.json").read_text(encoding="utf-8"))
    accepted_results = delivery["merged"]["results"]
    print(f"checks={len(checks)} passed={sum(row['passed'] for row in checks)}")
    print(f"worker_executions={delivery['worker_executions']} accepted_results={len(accepted_results)} shortage={accepted_results['read-stock']['shortage']}")
    print(f"owner={handoff['owner']} epoch={handoff['epoch']}")
    print(f"artifacts={args.output}")
    if not all(row["passed"] for row in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
