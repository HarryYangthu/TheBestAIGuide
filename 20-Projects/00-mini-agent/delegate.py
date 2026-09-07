#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from mini_agent.subagents import delegate

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optional: two isolated read-only Agent contexts")
    parser.add_argument("--mode", choices=("demo", "live"), required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = delegate(Path(__file__).resolve().parent / "fixtures/docs", args.output, args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
