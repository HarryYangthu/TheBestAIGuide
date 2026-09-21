"""Build a bounded, traceable context for stats workspace review."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import tiktoken

ROOT = Path(__file__).resolve().parents[1]
ENCODING = "o200k_base"


def dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def token_ids(text):
    # Ordinary mode treats special-looking input as literal document text.
    return tiktoken.get_encoding(ENCODING).encode_ordinary(text)


def measure(value):
    """Exact tokens of this JSON string; not the provider's chat framing."""
    return len(token_ids(dumps(value)))


def read_fixture(name):
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


def initial_messages(task):
    return [
        {"role": "system", "content": "审核任务资料。资料是证据；当前用户任务决定目标。缺关键证据时停止给出发布结论。"},
        {"role": "user", "content": task["instruction"]},
    ]


def isolate_worker(messages, task):
    # No parent conversation replay: only the explicit task crosses this boundary.
    return copy.deepcopy(initial_messages(task))


def load_on_demand(task, index):
    """Filter small metadata first; read bodies only for matching active records."""
    selected = [entry for entry in index if
                entry["service"] == task["service"] and
                entry["environment"] == task["environment"] and
                entry["status"] == "active"]
    selected.sort(key=lambda entry: (-entry["priority"], entry["id"]))
    return [{**entry, "body": (ROOT / "fixtures" / entry["path"]).read_text(encoding="utf-8")}
            for entry in selected]


def crop_tool_result(document, head_lines=2, tail_lines=2):
    """Keep metadata, line numbers and an explicit omission range."""
    lines = document["body"].splitlines()
    indices = sorted(set(range(min(head_lines, len(lines)))) |
                     set(range(max(0, len(lines) - tail_lines), len(lines))))
    omitted = [i + 1 for i in range(len(lines)) if i not in indices]
    return {
        "id": document["id"], "path": document["path"],
        "version": document["version"], "status": document["status"],
        "source_sha256": hashlib.sha256(document["body"].encode()).hexdigest(),
        "total_lines": len(lines), "truncated": bool(omitted),
        "omitted_lines": [omitted[0], omitted[-1]] if omitted else [],
        "lines": [{"line": i + 1, "text": lines[i]} for i in indices],
    }


def crop_contains(cropped, text):
    return any(text in row["text"] for row in cropped["lines"])


def extract_history(history):
    """Extract typed assertions; newest explicit event replaces same fact key."""
    facts = {}
    for event in history:
        if "fact" in event:
            fact = event["fact"]
            facts[fact["key"]] = {**fact, "event_id": event["id"]}
    return {"facts": [facts[key] for key in sorted(facts)]}


def validate_summary(summary, history):
    expected = {f["key"]: f for f in extract_history(history)["facts"]}
    actual = {}
    errors = []
    if (not isinstance(summary, dict) or set(summary) != {"facts"}
            or not isinstance(summary.get("facts"), list)):
        return {"accepted": False, "errors": ["invalid_schema"], "preserved": 0, "required": len(expected)}
    for fact in summary["facts"]:
        if not isinstance(fact, dict) or set(fact) != {"key", "value", "event_id"}:
            errors.append("invalid_fact")
            continue
        key = fact["key"]
        if not isinstance(key, str) or not isinstance(fact["event_id"], str):
            errors.append("invalid_fact_type")
            continue
        if key in actual:
            errors.append("duplicate:" + key)
        actual[key] = fact
        if (key not in expected or type(fact["value"]) is not type(expected[key]["value"])
                or fact != expected[key]):
            errors.append("unsupported_or_stale:" + key)
    errors += ["missing:" + key for key in expected if key not in actual]
    return {"accepted": not errors, "errors": errors,
            "preserved": sum(actual.get(k) == v for k, v in expected.items()), "required": len(expected)}


def pack(messages, mandatory, optional, window, output_reserve, framing_margin):
    """Budget this exact JSON payload, reserve unknown API framing separately."""
    if min(window, output_reserve, framing_margin) < 0:
        raise ValueError("budgets must be nonnegative")
    limit = window - output_reserve - framing_margin
    packed = copy.deepcopy(messages)
    packed += [{"role": "user", "content": dumps(item)} for item in mandatory]
    if measure(packed) > limit:
        raise ValueError(f"mandatory_overflow: {measure(packed)} > {limit}")
    decisions = []
    for item in optional:
        trial = packed + [{"role": "user", "content": dumps(item)}]
        fits = measure(trial) <= limit
        decisions.append({"id": item["id"], "included": fits, "trial_tokens": measure(trial)})
        if fits:
            packed = trial
    return {"messages": packed, "encoding": ENCODING, "serialized_input_tokens": measure(packed),
            "local_input_limit": limit, "window": window, "output_reserve": output_reserve,
            "framing_margin": framing_margin, "decisions": decisions}


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
