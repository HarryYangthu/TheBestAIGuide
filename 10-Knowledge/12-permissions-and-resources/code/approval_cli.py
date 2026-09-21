import argparse
import asyncio
import json
import sys
from dataclasses import asdict
from pathlib import Path
from control import Request, Runtime, fingerprint, principal


async def run(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    runtime, actor = Runtime(output), principal()
    request = Request("publish-approved", "publish_record", "a1")
    runtime.authorize(actor, request)
    payload = runtime.project(request)
    print(json.dumps({"subject": actor.subject, "tenant": actor.tenant, "action": asdict(request),
                      "payload": payload, "fingerprint": fingerprint(actor, request, payload),
                      "effect": "write these exact values to a1.json"}, ensure_ascii=False, indent=2))
    answer = input("Type APPROVE to write this file; anything else rejects: ")
    token = None
    if answer == "APPROVE":
        token = runtime.approvals.grant(actor, request, payload, source="human_terminal" if sys.stdin.isatty() else "stdin_fixture")
    result = await runtime.execute(actor, request, deadline=asyncio.get_running_loop().time() + 5, token=token)
    (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "events.json").write_text(json.dumps(runtime.events, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"status={result['status']} artifacts={output.as_posix()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="runs/approval")
    asyncio.run(run(parser.parse_args().output))
