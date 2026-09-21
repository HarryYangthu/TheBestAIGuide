import argparse
import asyncio
from protocol import Case, LocalBus, exchange, save_run


async def run_handoff(output):
    case = Case()
    bus = LocalBus(["coordinator", "notes-reader", "report-writer"])
    request = case.delegate("coordinator", "snapshot-ready.json")
    await exchange(case, request, bus)
    offer = case.offer_handoff("coordinator", "report-writer")
    before_accept = {"owner": case.owner, "epoch": case.epoch}
    case.accept_handoff("report-writer", offer["handoff_id"], offer["epoch"])
    old_action = case.act("coordinator", 1, "write_report")
    new_action = case.act("report-writer", 2, "write_report")
    return save_run(output, case, bus, {"handoff": offer, "before_accept": before_accept,
                                      "old_action": old_action, "new_action": new_action})


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="runs/v3")
    args = parser.parse_args()
    result = await run_handoff(args.output)
    print(f"before_accept={result['before_accept']['owner']} epoch={result['before_accept']['epoch']}")
    print(f"after_accept={result['owner']} epoch={result['epoch']}")
    print(f"old_action={result['old_action']} new_action={result['new_action']}")
    print(f"artifacts={args.output}")


if __name__ == "__main__":
    asyncio.run(main())
