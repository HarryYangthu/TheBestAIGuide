import argparse
from dataclasses import asdict
import json
from . import EvidenceModel, default_tools, run_agent


def main():
    parser = argparse.ArgumentParser(description="Offline document-search Agent Loop")
    parser.add_argument("query", nargs="?", default="上下文")
    parser.add_argument("--trace", default=None, help="new JSONL output file")
    args = parser.parse_args()
    state = run_agent(EvidenceModel(), default_tools(), args.query, trace_path=args.trace)
    print(json.dumps(asdict(state), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
