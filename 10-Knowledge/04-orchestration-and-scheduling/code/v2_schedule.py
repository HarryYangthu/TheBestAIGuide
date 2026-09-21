import argparse
import asyncio
from order_workflow import OrderWorker, load_inputs, make_plan, save_run
from scheduler import Scheduler


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--missing-price", action="store_true")
    parser.add_argument("--output", default="runs/v2")
    args = parser.parse_args()
    inputs = load_inputs("prices-missing.json" if args.missing_price else "prices-v1.json")
    scheduler = Scheduler(make_plan(), OrderWorker(inputs), concurrency=args.concurrency)
    await scheduler.run()
    result = save_run(args.output, scheduler, inputs)
    total = result["results"].get("publish", {}).get("quote", {}).get("total_cents")
    print(f"accepted={result['accepted']} total_cents={total}")
    print(f"executions={result['executions']} peak_active={result['peak_active']}")
    print(f"artifacts={args.output}")


if __name__ == "__main__":
    asyncio.run(main())
