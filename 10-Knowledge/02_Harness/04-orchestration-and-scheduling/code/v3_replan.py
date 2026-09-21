import argparse
import asyncio
from order_workflow import OrderWorker, load_inputs, make_plan, save_run
from scheduler import Scheduler


async def run_replan(output, add_shipping=False):
    before_inputs = load_inputs()
    worker = OrderWorker(before_inputs)
    scheduler = Scheduler(make_plan(), worker)
    await scheduler.run()
    before = scheduler.snapshot()
    after_inputs = load_inputs("prices-v2.json")
    worker.inputs = after_inputs
    invalidated = scheduler.replan(make_plan("2", shipping=add_shipping), changed_inputs={"prices"})
    await scheduler.run()
    result = save_run(output, scheduler, {"before": before_inputs, "after": after_inputs},
                      {"before": before, "invalidated": invalidated})
    return result


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--add-shipping", action="store_true")
    parser.add_argument("--output", default="runs/v3")
    args = parser.parse_args()
    result = await run_replan(args.output, args.add_shipping)
    before = result["before"]["results"]["publish"]["quote"]["total_cents"]
    after = result["results"]["publish"]["quote"]["total_cents"]
    print(f"before_cents={before} after_cents={after}")
    print("invalidated=" + ",".join(result["invalidated"]))
    retained = next(event["retained"] for event in reversed(result["events"]) if event["kind"] == "replan")
    print(f"executions={result['executions']} retained={','.join(retained)}")
    print(f"artifacts={args.output}")


if __name__ == "__main__":
    asyncio.run(main())
