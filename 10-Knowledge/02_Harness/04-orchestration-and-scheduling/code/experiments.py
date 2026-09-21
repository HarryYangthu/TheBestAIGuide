"""Run the same report task through controlled scheduling conditions."""
import argparse
import asyncio
import json
from pathlib import Path
from report_workflow import ReportWorker, load_inputs, make_plan, save_run
from scheduler import Scheduler
from v3_replan import run_replan


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="runs/experiments")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, concurrency, cases in [
        ("serial", 1, "cases-v1.json"), ("parallel", 2, "cases-v1.json"),
        ("missing_case", 2, "cases-missing.json"),
    ]:
        inputs = load_inputs(cases)
        scheduler = Scheduler(make_plan(), ReportWorker(inputs), concurrency=concurrency)
        await scheduler.run()
        result = save_run(output / name, scheduler, inputs)
        rows.append({"case": name, "accepted": result["accepted"],
                     "passed_checks": result["results"].get("publish", {}).get("summary", {}).get("passed_checks"),
                     "executions": result["executions"], "peak_active": result["peak_active"]})
    for name, empty_check in [("cases_changed", False), ("plan_changed", True)]:
        result = await run_replan(output / name, empty_check)
        rows.append({"case": name, "accepted": result["accepted"],
                     "passed_checks": result["results"]["publish"]["summary"]["passed_checks"],
                     "executions": result["executions"], "peak_active": result["peak_active"]})
    cancellation = Scheduler(make_plan(), ReportWorker(load_inputs(),
                             delays={"policy": 10, "cases": 10, "notes": 10}))
    parent = asyncio.create_task(cancellation.run())
    while not any(event["kind"] == "start" for event in cancellation.events):
        await asyncio.sleep(0)
    # Let execute_child enter its try/finally before requesting cancellation.
    await asyncio.sleep(0)
    parent.cancel()
    try:
        await parent
    except asyncio.CancelledError:
        pass
    save_run(output / "cancelled", cancellation, load_inputs())
    rows.append({"case": "cancelled", "accepted": False, "passed_checks": None,
                 "executions": cancellation.executions, "peak_active": cancellation.peak_active})
    (output / "comparison.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    lines = ["# 调度实验", "", "| 场景 | 验收 | 通过检查数 | 执行次数 | 最大活动数 |",
             "|---|---|---:|---:|---:|"]
    lines.extend(f"| {row['case']} | {row['accepted']} | {row['passed_checks']} | {row['executions']} | {row['peak_active']} |" for row in rows)
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for row in rows:
        print(f"{row['case']}: accepted={row['accepted']} passed_checks={row['passed_checks']} executions={row['executions']} peak_active={row['peak_active']}")
    print(f"artifacts={args.output}")


if __name__ == "__main__":
    asyncio.run(main())
