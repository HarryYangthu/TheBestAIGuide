"""上下文预算/压缩教学算法；没有调用模型。完整解释见同目录 Notebook。"""
from dataclasses import dataclass
import json


def byte_tokens(text: str) -> int:
    """教学字节 tokenizer：每个 UTF-8 字节一个 token，不等于供应商计费 token。"""
    return len(text.encode("utf-8"))


@dataclass(frozen=True)
class Item:
    id: str
    text: str
    utility: float
    mandatory: bool = False
    tenant: str = "alpha"


def pack(items: list[Item], window: int, reserved_output: int, tenant: str,
         count=byte_tokens) -> dict:
    if not 0 <= reserved_output < window:
        raise ValueError("invalid output reserve")
    limit = window - reserved_output
    selected, dropped = [], []
    def render(rows):
        # 分隔符同样计入成本；真实模型还要计消息模板、工具 Schema 等开销。
        return "\n\n".join(f"[{i.id}] {i.text}" for i in rows)
    permitted = []
    for item in items:
        if item.tenant != tenant:
            dropped.append({"id":item.id,"reason":"permission"})
        else:
            permitted.append(item)
    for item in permitted:
        if item.mandatory:
            selected.append(item)
    if count(render(selected)) > limit:
        raise ValueError("mandatory information exceeds budget; do not silently truncate")
    optional = sorted((x for x in permitted if not x.mandatory),
                      key=lambda x:(-x.utility/max(count(render([x])),1),x.id))
    for item in optional:
        if count(render(selected+[item])) <= limit:
            selected.append(item)
        else:
            dropped.append({"id":item.id,"reason":"budget"})
    return {"text":render(selected),"selected_ids":[i.id for i in selected],"dropped":dropped,
            "input_tokens":count(render(selected)),"input_limit":limit,
            "counting":"injected counter (default: UTF-8 byte tokenizer)"}


def compact(events: list[dict]) -> dict:
    """针对已结构化事件抽取最新事实；不是从任意自然语言自动理解事实。"""
    facts, sources = {}, {}
    for event in events:
        if event["kind"] in {"constraint","observation","pending"}:
            facts[event["key"]] = event["value"]
            sources[event["key"]] = event["id"]
    return {"facts":facts,"sources":sources,"method":"structured-extract-v1","lossy":True}


def recall(summary: dict, expected: dict) -> float:
    return sum(summary.get("facts",{}).get(k)==v for k,v in expected.items())/len(expected)


def serialized(value) -> str:
    return json.dumps(value,ensure_ascii=False,separators=(",",":"))
