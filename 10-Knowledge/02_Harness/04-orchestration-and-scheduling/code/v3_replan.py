import argparse
import asyncio
from report_workflow import ReportWorker, load_inputs, make_plan, save_run
from scheduler import Scheduler


async def run_replan(output, add_empty_check=False):
    before_inputs = load_inputs()
    worker = ReportWorker(before_inputs)
    scheduler = Scheduler(make_plan(), worker)
    await scheduler.run()
    before = scheduler.snapshot()
    after_inputs = load_inputs("cases-v2.json")
    worker.inputs = after_inputs
    invalidated = scheduler.replan(make_plan("2", empty_check=add_empty_check), changed_inputs={"cases"})
    await scheduler.run()
    result = save_run(output, scheduler, {"before": before_inputs, "after": after_inputs},
                      {"before": before, "invalidated": invalidated})
    return result


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--add-empty-check", action="store_true")
    parser.add_argument("--output", default="runs/v3")
    args = parser.parse_args()
    result = await run_replan(args.output, args.add_empty_check)
    before = result["before"]["results"]["publish"]["summary"]["passed_checks"]
    after = result["results"]["publish"]["summary"]["passed_checks"]
    print(f"before_passed={before} after_passed={after}")
    print("invalidated=" + ",".join(result["invalidated"]))
    retained = next(event["retained"] for event in reversed(result["events"]) if event["kind"] == "replan")
    print(f"executions={result['executions']} retained={','.join(retained)}")
    print(f"artifacts={args.output}")


if __name__ == "__main__":
    asyncio.run(main())
