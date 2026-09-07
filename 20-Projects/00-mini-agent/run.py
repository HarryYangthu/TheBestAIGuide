#!/usr/bin/env python3
"""Run from any directory, without installing packages."""
import argparse
import json
from pathlib import Path
from mini_agent.providers import DemoModel, LiveModel
from mini_agent.runtime import run, TASK
from mini_agent.memory import resolve_format, set_format
from mini_agent.evaluate import evaluate

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    execute = commands.add_parser("run")
    execute.add_argument("--stage", type=int, choices=range(1, 8), default=1)
    execute.add_argument("--mode", choices=("demo", "live"), required=True)
    execute.add_argument("--output", type=Path, required=True)
    execute.add_argument("--docs", type=Path, default=ROOT / "fixtures/docs")
    execute.add_argument("--max-steps", type=int, default=16)
    execute.add_argument("--context-chars", type=int, default=9000)
    execute.add_argument("--memory", type=Path, default=Path(".runs/mini-memory.json"))
    execute.add_argument("--format", choices=("table", "bullets"))
    execute.add_argument("--task", default=TASK)
    memory = commands.add_parser("memory")
    memory.add_argument("value", choices=("table", "bullets", "delete"))
    memory.add_argument("--file", type=Path, required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--output", type=Path, required=True)
    verify.add_argument("--docs", type=Path, default=ROOT / "fixtures/docs")
    args = parser.parse_args()
    if args.command == "memory":
        set_format(args.file, args.value)
        print(json.dumps({"saved": str(args.file), "value": args.value}))
        return 0
    if args.command == "verify":
        result = evaluate(args.output, args.docs)
    else:
        provider = DemoModel(args.stage) if args.mode == "demo" else LiveModel()
        fmt, origin = (resolve_format(args.memory, args.format) if args.stage >= 4 else (args.format or "table", "current_or_default"))
        result = run(args.output, args.docs, provider, args.stage, args.max_steps, args.context_chars,
                     fmt, origin, args.task)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
