"""本地 UTF-8 Markdown/JSONL 接入；刻意不伪装成通用 PDF/OCR 解析器。"""
from dataclasses import dataclass
from pathlib import Path
import json
import re


def identifiers(text: str) -> tuple[str, ...]:
    """保留完整编码；ALM-12003 与 ALM-12030 是两个不同标识。"""
    return tuple(dict.fromkeys(re.findall(r"\b[A-Z]{2,}-\d{3,}\b", text.upper())))


@dataclass(frozen=True)
class Document:
    doc_id: str
    text: str
    tenant: str = "public"
    product: str = ""
    version: str = "1"
    identifiers: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.doc_id or not self.tenant or not self.version or not self.text.strip():
            raise ValueError("document id, tenant, version and text must be non-empty")
        declared = tuple(x.upper() for x in self.identifiers)
        object.__setattr__(self, "identifiers", declared or identifiers(self.text))


def load_jsonl(path: str | Path) -> list[Document]:
    rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    return [Document(**row) for row in rows]


def load_markdown(path: str | Path, **metadata) -> Document:
    path = Path(path)
    if path.suffix.lower() != ".md":
        raise ValueError("only .md is supported; convert other formats with provenance first")
    return Document(doc_id=metadata.pop("doc_id", path.stem), text=path.read_text(encoding="utf-8"), **metadata)
