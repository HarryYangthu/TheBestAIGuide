import argparse
from datetime import datetime, timezone
from pathlib import Path
from contracts import ROOT, execute


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, default=ROOT / "examples/task.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or ROOT / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    if output.exists():
        parser.error("输出目录已存在，请使用新目录")
    record = execute(args.task, output)
    print(f"status={record['status']} code={record['error']['code'] if record['error'] else 'none'}")
    print(f"run_id={record['run_id']}")
    print(f"artifacts={output}")
    return 0 if record["status"] == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())
