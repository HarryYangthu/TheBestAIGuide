"""Local teaching integration. Trusted caller binds tenant/product/version.

The default policy is deterministic, not an LLM. One writer per work directory;
the persisted result is an extract, not an open-ended generated conclusion.
"""
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
import json
import re

from agent_loop import Action, Tool, run_agent
from rag_pipeline import Document, Index, answer, verify_citation
from recoverable_runtime import EventStore
from state_memory import CheckpointStore, MemoryStore


class InjectedCrash(RuntimeError):
    pass


class EvidencePolicy:
    def decide(self, state):
        if not state.observations:
            return Action("tool", "lookup", {"query": state.task})
        return Action("finish", answer="检索结束；发布内容由引用校验器决定。")


def stable_json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


class ResearchService:
    def __init__(self, directory, documents: list[Document], *, tenant: str,
                 product: str = "GuideDemo", version: str = "1"):
        if not tenant or not product or not version:
            raise ValueError("trusted scope must be explicit")
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.tenant, self.product, self.version = tenant, product, version
        self.index = Index()
        for document in documents:
            self.index.upsert(document)
        # Binding input corpus prevents reusing a completed run after sources change.
        canonical_docs = sorted([asdict(d) for d in documents],
                                key=lambda d: (d["tenant"], d["doc_id"]))
        self.corpus_digest = sha256(stable_json(canonical_docs).encode()).hexdigest()
        self.checkpoints = CheckpointStore(str(self.directory / "checkpoints.sqlite"))
        self.memory = MemoryStore(str(self.directory / "memory.sqlite"))
        self.events = EventStore(str(self.directory / "events.sqlite"))

    def close(self):
        self.checkpoints.close()
        self.memory.close()
        self.events.close()

    def _request(self, query):
        return {"query": query, "tenant": self.tenant, "product": self.product,
                "version": self.version, "corpus_digest": self.corpus_digest}

    def run(self, run_id: str, query: str, *, model=None, crash_at=None, now=0.0):
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", run_id):
            raise ValueError("run_id must be a short safe identifier")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query cannot be empty")
        if crash_at not in {None, "after_prepare", "after_report"}:
            raise ValueError("unknown crash point")
        request = self._request(query)
        saved_version, saved = self.checkpoints.load(run_id)
        if saved and saved["request"] != request:
            raise ValueError("run_id is already bound to a different request or source version")
        if saved.get("stage") == "completed":
            # Rebuild a deleted report from the committed snapshot, without retrieval.
            self._write_report(run_id, saved["result"])
            return saved["result"]

        if not saved:
            evidence = None

            def lookup(arguments):
                nonlocal evidence
                if set(arguments) != {"query"} or not isinstance(arguments["query"], str):
                    raise ValueError("lookup accepts only query; scope is bound by the server")
                if arguments["query"] != query:
                    raise ValueError("this teaching task requires the original query without rewriting")
                evidence = answer(self.index, arguments["query"], tenant=self.tenant,
                                  product=self.product, version=self.version)
                return asdict(evidence)

            state = run_agent(model or EvidencePolicy(), {"lookup": Tool(lookup)}, query,
                              max_steps=4, trace_path=str(self.directory / f"{run_id}.trace.jsonl"))
            if state.status != "completed" or evidence is None:
                raise ValueError("agent failed or finished without invoking the evidence tool")
            if not all(verify_citation(self.index, c, tenant=self.tenant) for c in evidence.citations):
                raise ValueError("citation verification failed")
            result = {"run_id": run_id, "tenant": self.tenant, "query": query,
                      "text": evidence.text, "citations": [asdict(c) for c in evidence.citations],
                      "abstained": evidence.abstained, "steps": state.steps,
                      "decision_policy": "deterministic-v1" if model is None else f"provided:{type(model).__name__}",
                      "answer_mode": "extractive-v1"}
            saved = {"request": request, "stage": "prepared", "result": result}
            saved_version = self.checkpoints.save(run_id, saved, expected_version=0)
            self.events.append(run_id, "report", "prepared", {"abstained": result["abstained"]})

        if crash_at == "after_prepare":
            raise InjectedCrash(crash_at)
        result = saved["result"]
        self._write_report(run_id, result)
        if crash_at == "after_report":
            raise InjectedCrash(crash_at)

        # Save evidence pointers only; a previous answer must not become a new fact.
        if not result["abstained"]:
            value = {"query": query, "citations": result["citations"]}
            old = self.memory.get(self.tenant, run_id, now=now)
            if old is None:
                self.memory.put(self.tenant, run_id, value, source=f"report:{run_id}", now=now)
            elif old.value != value:
                raise ValueError("memory key has conflicting content")
        saved["stage"] = "completed"
        self.checkpoints.save(run_id, saved, expected_version=saved_version)
        self.events.append(run_id, "report", "completed", {"citation_count": len(result["citations"])})
        return result

    def _write_report(self, run_id, result):
        path = self.directory / f"{run_id}.report.json"
        content = stable_json(result) + "\n"
        if path.exists():
            if path.read_text(encoding="utf-8") != content:
                raise ValueError("existing report conflicts with prepared result")
            return
        # Same-directory replace is atomic on supported local filesystems. No fsync:
        # this demonstrates process crashes, not guaranteed machine-power-loss safety.
        temporary = path.with_suffix(".tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(path)
