#!/usr/bin/env python3
import argparse
import json
from mini_agent.harness import curriculum

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run all seven offline lessons and acceptance experiments")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = curriculum(args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
