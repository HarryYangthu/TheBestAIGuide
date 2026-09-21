"""Run the same order through controlled scheduling conditions."""
import argparse
import asyncio
import json
from pathlib import Path
from order_workflow import OrderWorker, load_inputs, make_plan, save_run
from scheduler import Scheduler
from v3_replan import run_replan


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="runs/experiments")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, concurrency, prices in [
        ("serial", 1, "prices-v1.json"), ("parallel", 2, "prices-v1.json"),
        ("missing_price", 2, "prices-missing.json"),
    ]:
        inputs = load_inputs(prices)
        scheduler = Scheduler(make_plan(), OrderWorker(inputs), concurrency=concurrency)
        await scheduler.run()
        result = save_run(output / name, scheduler, inputs)
        rows.append({"case": name, "accepted": result["accepted"],
                     "total_cents": result["results"].get("publish", {}).get("quote", {}).get("total_cents"),
                     "executions": result["executions"], "peak_active": result["peak_active"]})
    for name, shipping in [("price_changed", False), ("plan_changed", True)]:
        result = await run_replan(output / name, shipping)
        rows.append({"case": name, "accepted": result["accepted"],
                     "total_cents": result["results"]["publish"]["quote"]["total_cents"],
                     "executions": result["executions"], "peak_active": result["peak_active"]})
    cancellation = Scheduler(make_plan(), OrderWorker(load_inputs(),
                             delays={"policy": 10, "prices": 10, "stock": 10}))
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
    rows.append({"case": "cancelled", "accepted": False, "total_cents": None,
                 "executions": cancellation.executions, "peak_active": cancellation.peak_active})
    (output / "comparison.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    lines = ["# 调度实验", "", "| 场景 | 验收 | 金额（分） | 执行次数 | 最大活动数 |",
             "|---|---|---:|---:|---:|"]
    lines.extend(f"| {row['case']} | {row['accepted']} | {row['total_cents']} | {row['executions']} | {row['peak_active']} |" for row in rows)
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for row in rows:
        print(f"{row['case']}: accepted={row['accepted']} total_cents={row['total_cents']} executions={row['executions']} peak_active={row['peak_active']}")
    print(f"artifacts={args.output}")


if __name__ == "__main__":
    asyncio.run(main())
