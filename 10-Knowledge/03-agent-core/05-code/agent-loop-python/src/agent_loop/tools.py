"""Small read-only fixture. Real systems need resource authorization in handlers."""
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Tool:
    handler: Callable[[dict[str, Any]], Any]
    allowed: bool = True


DOCUMENTS = [
    {"id": "doc-1", "text": "上下文预算必须为模型输出和工具结果预留空间。"},
    {"id": "doc-2", "text": "上下文压缩应保留当前目标、约束、证据来源和未完成任务。"},
    {"id": "doc-3", "text": "工具超时后需要核查副作用，不能把超时当作没有执行。"},
]


def search(arguments: dict[str, Any]) -> dict[str, Any]:
    if set(arguments) != {"query"} or not isinstance(arguments["query"], str):
        raise ValueError("query must be the only field and must be a string")
    query = arguments["query"].strip()
    if not query:
        raise ValueError("query cannot be empty")
    # Chinese substring matching is deliberate: this is not a vector retriever.
    return {"documents": [dict(d) for d in DOCUMENTS if query in d["text"]]}


def default_tools() -> dict[str, Tool]:
    return {"search": Tool(search)}
