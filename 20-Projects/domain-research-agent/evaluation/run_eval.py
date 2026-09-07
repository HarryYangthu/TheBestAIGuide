"""Four local scenarios, repeated with a new work directory on every trial."""
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import json
from domain_research import ResearchService, InjectedCrash
from rag_pipeline import load_jsonl
from eval_harness import EvalTask, run_suite, summarize, write_report

CORPUS = Path(__file__).resolve().parents[1] / "fixtures/corpus.jsonl"


def system(request, fixture, emit):
    with TemporaryDirectory() as directory:
        service = ResearchService(directory, load_jsonl(CORPUS), tenant="demo")
        try:
            if request.get("simulate_crash"):
                try:
                    service.run("eval", request["query"], crash_at="after_report")
                except InjectedCrash:
                    emit("injected_crash", stage="after_report")
                service.close()
                service = ResearchService(directory, load_jsonl(CORPUS), tenant="demo")
            result = service.run("eval", request["query"])
            fixture["report_written"] = (Path(directory) / "eval.report.json").is_file()
            fixture["memory_written"] = service.memory.get("demo", "eval", now=0) is not None
            fixture["citation_count"] = len(result["citations"])
            emit("evidence_verified", count=len(result["citations"]), abstained=result["abstained"])
            return result
        finally:
            service.close()


TASKS = [
    EvalTask("supported", {"query":"ERR-12003"},
             {"output":{"abstained":False}, "state":{"report_written":True,"memory_written":True,"citation_count":1}},
             tags=("evidence",)),
    EvalTask("unknown", {"query":"ERR-88888"},
             {"output":{"abstained":True}, "state":{"report_written":True,"memory_written":False,"citation_count":0}},
             tags=("abstention",)),
    EvalTask("private", {"query":"ERR-99999"},
             {"output":{"abstained":True}, "state":{"citation_count":0,"memory_written":False},
              "forbidden_strings":["PRIVATE_FIXTURE_ONLY"]},
             tags=("authorization",), critical=True),
    EvalTask("resume", {"query":"ERR-12003", "simulate_crash":True},
             {"output":{"abstained":False}, "state":{"report_written":True,"memory_written":True,"citation_count":1}},
             tags=("recovery",), critical=True),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(Path(__file__).parent / "report"))
    args = parser.parse_args()
    results = run_suite(TASKS, system, trials=2)
    write_report(results, args.output)
    print(json.dumps(summarize(results), ensure_ascii=False, indent=2))
    if not all(r.success for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
