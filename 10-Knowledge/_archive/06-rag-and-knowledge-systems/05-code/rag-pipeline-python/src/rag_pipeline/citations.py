"""抽取式回答用于验证检索/引用链路，不替代开放式事实蕴含判断。"""
from dataclasses import dataclass
from .retrieval import Index


@dataclass(frozen=True)
class Citation:
    chunk_id: str
    doc_id: str
    version: str
    quote: str
    start: int
    end: int


@dataclass(frozen=True)
class Answer:
    text: str
    citations: tuple[Citation, ...]
    abstained: bool


def answer(index: Index, query: str, *, tenant: str, product: str | None = None,
           version: str | None = None, k: int = 3) -> Answer:
    hits = index.search(query, tenant=tenant, product=product, version=version, k=k)
    if not hits:
        return Answer("当前授权范围内没有找到匹配证据，无法回答。", (), True)
    cites = tuple(Citation(h.chunk.chunk_id, h.chunk.doc_id, h.chunk.version,
                          h.chunk.text, h.chunk.start, h.chunk.end) for h in hits)
    text = "\n\n".join(f"[{i}] {c.quote}" for i,c in enumerate(cites,1))
    return Answer(text, cites, False)


def verify_citation(index: Index, citation: Citation, *, tenant: str) -> bool:
    c = index.get_chunk(citation.chunk_id, tenant=tenant)
    return bool(c and c.doc_id == citation.doc_id and c.version == citation.version
                and c.text == citation.quote and c.start == citation.start and c.end == citation.end)
