"""从工程目录执行 PYTHONPATH=src python -m rag_pipeline.cli。"""
from pathlib import Path
import argparse
import json
from . import Index, answer, load_jsonl, retrieval_metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path, default=Path("fixtures"))
    parser.add_argument("--output", type=Path, default=Path("run-report.json"))
    args = parser.parse_args()
    idx = Index()
    for doc in load_jsonl(args.fixtures/"corpus.jsonl"):
        idx.upsert(doc)
    rows = []
    for line in (args.fixtures/"queries.jsonl").read_text(encoding="utf-8").splitlines():
        q = json.loads(line)
        filters = {k:q[k] for k in ("tenant","product","version")}
        hits = idx.search(q["query"], **filters, k=3, unit="document")
        out = answer(idx,q["query"],**filters)
        ranking = list(dict.fromkeys(h.chunk.doc_id for h in hits))
        rows.append({"query_id":q["id"],"slice":q["slice"],"ranking":ranking,
                     "abstained":out.abstained,**retrieval_metrics(ranking,q["relevance"],3)})
    report = {"data":"hand-authored synthetic teaching fixtures v1", "mode":"BM25 + exact RRF",
              "embedding_executed":False,"reranker_executed":False,"rows":rows}
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
