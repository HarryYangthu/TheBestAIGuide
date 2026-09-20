"""运行离线实验：python code/run_scenarios.py all --summary。"""
import argparse
import json
from scenarios import CASE_NAMES, run_case


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", nargs="?", default="all", choices=("all",) + CASE_NAMES)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--max-steps", type=int)
    args = parser.parse_args()
    names = CASE_NAMES if args.case == "all" else [args.case]
    results = [run_case(name, max_steps=args.max_steps) for name in names]
    if args.summary:
        results = [{"case": result["case"], "fixture_mode": result["fixture_mode"],
                    "status": result["status"], "reason": result["reason"],
                    "model_calls": result["model_calls"], "acceptance_passed": result["acceptance"]["passed"]}
                   for result in results]
    print(json.dumps(results if args.case == "all" else results[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
