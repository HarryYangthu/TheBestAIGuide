"""可读的内存索引：每次仅对授权、版本匹配的候选计算统计与排名。"""
from collections import Counter
from dataclasses import dataclass
from typing import Callable
import math
import re
from .ingest import Document, identifiers
from .chunking import Chunk, chunk_document
from .ranking import rrf


def tokenize(text: str) -> list[str]:
    # 教学词法：英文词/完整编码 + 中文单字。不是语义分词器。
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*|[\u4e00-\u9fff]", text.lower())


def bm25(query: str, texts: list[str], k1: float = 1.2, b: float = 0.75) -> list[float]:
    if k1 <= 0 or not 0 <= b <= 1:
        raise ValueError("invalid BM25 parameters")
    if not texts:
        return []
    counts = [Counter(tokenize(t)) for t in texts]
    lengths = [sum(c.values()) for c in counts]
    avgdl = sum(lengths) / len(texts)
    if avgdl == 0:
        return [0.0] * len(texts)
    scores = [0.0] * len(texts)
    for term in set(tokenize(query)):
        df = sum(term in c for c in counts)
        idf = math.log(1 + (len(texts) - df + 0.5) / (df + 0.5))
        for i, c in enumerate(counts):
            tf = c[term]
            scores[i] += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * lengths[i] / avgdl))
    return scores


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float
    channels: tuple[str, ...]


class Index:
    def __init__(self, max_chars: int = 600,
                 embedder: Callable[[list[str]], list[list[float]]] | None = None,
                 reranker: Callable[[str, list[str]], list[float]] | None = None):
        self.max_chars = max_chars
        self.embedder = embedder
        self.reranker = reranker
        self._documents: dict[tuple[str, str], Document] = {}
        self._chunks: dict[tuple[str, str], list[Chunk]] = {}
        self.generation = 0

    def upsert(self, document: Document) -> None:
        """完整替换同 tenant/doc_id；先成功切块，再切换可见内容。"""
        key = (document.tenant, document.doc_id)
        chunks = chunk_document(document, self.max_chars)
        self._documents[key] = document
        self._chunks[key] = chunks
        self.generation += 1

    def delete(self, doc_id: str, *, tenant: str = "public") -> bool:
        key = (tenant, doc_id)
        existed = key in self._documents
        self._documents.pop(key, None)
        self._chunks.pop(key, None)
        if existed:
            self.generation += 1
        return existed

    def get_chunk(self, chunk_id: str, *, tenant: str) -> Chunk | None:
        return next((c for (t, _), cs in self._chunks.items() if t == tenant
                     for c in cs if c.chunk_id == chunk_id), None)

    def search(self, query: str, *, tenant: str, product: str | None = None,
               version: str | None = None, k: int = 5, mode: str = "hybrid",
               unit: str = "chunk") -> list[Hit]:
        if not tenant or k < 1 or mode not in {"bm25", "exact", "hybrid", "dense"} or unit not in {"chunk", "document"}:
            raise ValueError("tenant, positive k and supported mode/unit are required")
        required = set(identifiers(query))
        candidates = [c for (t, _), cs in self._chunks.items() if t == tenant for c in cs
                      if (product is None or c.product == product)
                      and (version is None or c.version == version)
                      and (not required or required <= set(c.identifiers))]
        if not candidates or not tokenize(query):
            return []
        lists = {}
        if mode in {"bm25", "hybrid"}:
            scores = bm25(query, [c.text for c in candidates])
            lists["bm25"] = [c.chunk_id for c, s in sorted(zip(candidates, scores),
                               key=lambda cs: (-cs[1], cs[0].chunk_id)) if s > 0]
        if mode in {"exact", "hybrid"} and required:
            lists["exact"] = sorted(c.chunk_id for c in candidates)
        if mode == "dense" and self.embedder is None:
            raise ValueError("dense mode needs a real configured embedder")
        if self.embedder is not None and mode in {"hybrid", "dense"}:
            vectors = self.embedder([query] + [c.text for c in candidates])
            if len(vectors) != len(candidates) + 1 or not vectors[0]:
                raise ValueError("embedder returned wrong batch shape")
            dim = len(vectors[0])
            if any(len(v) != dim or any(not math.isfinite(x) for x in v) for v in vectors):
                raise ValueError("embedding dimensions or values invalid")
            def cosine(v):
                norm = math.sqrt(sum(x*x for x in vectors[0]) * sum(x*x for x in v))
                return sum(a*b for a,b in zip(vectors[0],v)) / norm if norm else 0.0
            scores = [cosine(v) for v in vectors[1:]]
            lists["dense"] = [c.chunk_id for c,s in sorted(zip(candidates,scores),
                              key=lambda cs: (-cs[1],cs[0].chunk_id)) if s > 0]
        fused = rrf(list(lists.values()))
        by_id = {c.chunk_id: c for c in candidates}
        ordered = sorted(fused, key=lambda cid: (-fused[cid], cid))
        if self.reranker is not None and ordered:
            scores = self.reranker(query, [by_id[cid].text for cid in ordered])
            if len(scores) != len(ordered) or any(not math.isfinite(s) for s in scores):
                raise ValueError("reranker returned wrong shape or non-finite scores")
            ordered = [cid for cid,s in sorted(zip(ordered,scores), key=lambda x:(-x[1],x[0]))]
        if unit == "document":
            seen = set()
            unique = []
            for cid in ordered:
                doc_id = by_id[cid].doc_id
                if doc_id not in seen:
                    seen.add(doc_id)
                    unique.append(cid)
            ordered = unique
        return [Hit(by_id[cid], fused[cid], tuple(channel for channel,ids in lists.items()
                    if cid in ids)) for cid in ordered[:k]]
