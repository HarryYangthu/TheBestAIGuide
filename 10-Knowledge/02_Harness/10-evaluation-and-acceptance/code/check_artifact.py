import argparse
import json
from pathlib import Path
from evaluation import accept, cases

parser = argparse.ArgumentParser()
parser.add_argument("--case", required=True)
parser.add_argument("--artifact", type=Path, required=True)
args = parser.parse_args()
case = next(c for c in cases() if c["id"] == args.case)
print(json.dumps(accept(args.artifact, case["expected"]), ensure_ascii=False, indent=2))
