"""段落优先切块。偏移指向原始字符串；长段落定长回退会标记 split。"""
from dataclasses import dataclass
import hashlib
import re
from .ingest import Document, identifiers


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    text: str
    tenant: str
    product: str
    version: str
    identifiers: tuple[str, ...]
    start: int
    end: int
    split: bool


def chunk_document(doc: Document, max_chars: int = 600) -> list[Chunk]:
    if max_chars < 1:
        raise ValueError("max_chars must be positive")
    chunks = []
    for para in re.finditer(r"\S(?:.*?\S)?(?=\n\s*\n|\Z)", doc.text, flags=re.S):
        for start in range(para.start(), para.end(), max_chars):
            end = min(start + max_chars, para.end())
            content = doc.text[start:end]
            digest = hashlib.sha256(content.encode()).hexdigest()[:12]
            cid = f"{doc.doc_id}@{doc.version}:{start}-{end}:{digest}"
            mentioned = set(identifiers(content))
            # 多编号文档不能把全部编号广播给每段。单一编号文档允许正文无编码段继承。
            # 显式元数据可以排除“不是 ALM-12003”这种提及，自动提取不理解否定。
            codes = tuple(x for x in doc.identifiers if x in mentioned)
            if not mentioned and len(doc.identifiers) == 1:
                codes = doc.identifiers
            chunks.append(Chunk(cid, doc.doc_id, content, doc.tenant, doc.product,
                                doc.version, codes, start, end,
                                para.end() - para.start() > max_chars))
    return chunks
