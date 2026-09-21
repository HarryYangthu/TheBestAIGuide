import argparse
import asyncio
from report_workflow import ReportWorker, load_inputs, make_plan, save_run
from scheduler import Scheduler


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--missing-case", action="store_true")
    parser.add_argument("--output", default="runs/v2")
    args = parser.parse_args()
    inputs = load_inputs("cases-missing.json" if args.missing_case else "cases-v1.json")
    scheduler = Scheduler(make_plan(), ReportWorker(inputs), concurrency=args.concurrency)
    await scheduler.run()
    result = save_run(args.output, scheduler, inputs)
    total = result["results"].get("publish", {}).get("summary", {}).get("passed_checks")
    print(f"accepted={result['accepted']} passed_checks={total}")
    print(f"executions={result['executions']} peak_active={result['peak_active']}")
    print(f"artifacts={args.output}")


if __name__ == "__main__":
    asyncio.run(main())
