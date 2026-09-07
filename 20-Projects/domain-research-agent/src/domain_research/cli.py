from pathlib import Path
import argparse
import json
from rag_pipeline import load_jsonl
from .service import ResearchService


def main():
    parser = argparse.ArgumentParser(description="Run the offline evidence fixture")
    parser.add_argument("--query", default="ERR-12003")
    parser.add_argument("--run-id", default="demo-001")
    parser.add_argument("--output", default=".runs/research")
    parser.add_argument("--corpus", default=str(Path(__file__).resolve().parents[2] / "fixtures/corpus.jsonl"))
    args = parser.parse_args()
    service = ResearchService(args.output, load_jsonl(args.corpus), tenant="demo")
    try:
        print(json.dumps(service.run(args.run_id, args.query), ensure_ascii=False, indent=2))
    finally:
        service.close()


if __name__ == "__main__":
    main()
