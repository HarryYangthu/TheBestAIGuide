import argparse
from pathlib import Path
from evaluation import cases, run_one

parser = argparse.ArgumentParser()
parser.add_argument("--case", default="whitespace")
parser.add_argument("--variant", choices=["baseline", "candidate"], default="baseline")
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()
case = next(c for c in cases() if c["id"] == args.case)
result = run_one(case, args.variant, 0, args.out)
print(f"exit_reason={result['exit_reason']} accepted={result['accepted']}")
print(f"artifacts={args.out}")
