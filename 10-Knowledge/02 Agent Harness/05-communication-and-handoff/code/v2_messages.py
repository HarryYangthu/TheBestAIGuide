import argparse
import asyncio
from protocol import Case, LocalBus, exchange, save_run


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="runs/v2")
    args = parser.parse_args()
    case = Case()
    bus = LocalBus(["coordinator", "notes-reader"])
    request = case.delegate("coordinator", "snapshot-ready.json")
    _, decisions = await exchange(case, request, bus)
    result = save_run(args.output, case, bus)
    print("decisions=" + ",".join(decisions))
    print(f"complete={result['merged']['complete']} owner={case.owner} epoch={case.epoch}")
    print(f"artifacts={args.output}")


if __name__ == "__main__":
    asyncio.run(main())
