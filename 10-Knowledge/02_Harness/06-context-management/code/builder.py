"""A request builder with access checks, evidence provenance and explicit budgets."""
from __future__ import annotations

import copy
import hashlib
from datetime import datetime
from pathlib import Path

from context import ROOT, crop_tool_result, dumps, extract_history, initial_messages, measure

FIXTURES = ROOT / "fixtures"
BUILDER_VERSION = "context-builder-v1"
OUTPUT_SCHEMA = {"type": "object", "properties": {
    "decision": {"type": "string", "enum": ["BLOCKED", "NEEDS_EVIDENCE", "APPROVED"]},
    "evidence_ids": {"type": "array", "items": {"type": "string"}}},
    "required": ["decision", "evidence_ids"], "additionalProperties": False}
# This describes the request interface; the builder never executes this tool.
TOOLS = [{"type": "function", "function": {
    "name": "read_evidence", "description": "读取已授权证据的指定行；不能修改文件或发布任务。",
    "parameters": {"type": "object", "properties": {
        "evidence_id": {"type": "string"}, "start": {"type": "integer", "minimum": 1}},
        "required": ["evidence_id", "start"], "additionalProperties": False}}}]


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def resolve_source(path):
    resolved = (FIXTURES / path).resolve()
    if not resolved.is_relative_to(FIXTURES.resolve()) or not resolved.is_file():
        raise ValueError("invalid_source_path")
    return resolved


def select_documents(task, index, tenant, *, deduplicate=True):
    """The index and tenant come from trusted application configuration."""
    selected, dropped, reads = [], [], []
    seen = {}
    for item in sorted(index, key=lambda x: (-x["priority"], x["id"])):
        reason = None
        if item["tenant"] != tenant:
            reason = "permission"
        elif (item["service"], item["environment"]) != (task["service"], task["environment"]):
            reason = "wrong_scope"
        elif item["status"] != "active":
            reason = "superseded"
        elif item["kind"] == "policy" and item["version"] != task["policy_version"]:
            reason = "wrong_version"
        elif item.get("valid_until") and datetime.fromisoformat(item["valid_until"]) <= datetime.fromisoformat(task["as_of"]):
            reason = "expired"
        if reason:
            dropped.append({"id": item["id"], "reason": reason})
            continue
        body = resolve_source(item["path"]).read_text(encoding="utf-8")
        reads.append(item["id"])
        digest = sha256(body)
        identity = (item["kind"], item["version"], digest)
        if deduplicate and identity in seen:
            dropped.append({"id": item["id"], "reason": "duplicate", "same_as": seen[identity]})
            continue
        seen[identity] = item["id"]
        selected.append({**item, "body": body, "source_sha256": digest})
    policies = [d for d in selected if d["kind"] == "policy"]
    if len({d["source_sha256"] for d in policies}) > 1:
        raise ValueError("unresolved_conflict: same policy scope/version has different content")
    return selected, dropped, reads


def build_context(task, index, history, tenant, *, window=4000, output_reserve=600,
                  framing_margin=300, deduplicate=True, compact_log=True):
    if min(window, output_reserve, framing_margin) < 0:
        raise ValueError("invalid_budget")
    docs, dropped, reads = select_documents(task, index, tenant, deduplicate=deduplicate)
    policies = [d for d in docs if d["kind"] == "policy"]
    if not policies:
        raise ValueError("missing_policy")
    summary = extract_history(history)
    transformations = [{"output_id": "history-summary", "source_ids": [e["id"] for e in history],
                        "method": "structured-latest-facts-v1", "lossy": True,
                        "source_sha256": sha256(dumps(history))}]
    messages = initial_messages(task) + [{"role": "user", "content": dumps({
        "current_state": summary, "open_items": task["open_items"],
        "constraints": task["constraints"], "acceptance": task["acceptance"]})}]
    messages += [{"role": "user", "content": dumps({"data_only": True, **p})} for p in policies]
    request = {"messages": messages, "tools": copy.deepcopy(TOOLS),
               "response_format": {"type": "json_schema", "json_schema": {
                   "name": "release_review", "strict": True, "schema": OUTPUT_SCHEMA}}}
    limit = window - output_reserve - framing_margin
    if measure(request) > limit:
        raise ValueError("mandatory_overflow")
    selected = [p["id"] for p in policies]
    for item in docs:
        if item["kind"] == "policy":
            continue
        payload = crop_tool_result(item) if item["kind"] == "log" and compact_log else item
        trial = copy.deepcopy(request)
        trial["messages"].append({"role": "user", "content": dumps({
            "data_only": True, "trust": item["trust"], "evidence": payload})})
        if measure(trial) > limit:
            dropped.append({"id": item["id"], "reason": "budget"})
            continue
        request = trial
        selected.append(item["id"])
        if payload is not item:
            transformations.append({"output_id": item["id"] + ":crop", "source_ids": [item["id"]],
                                    "method": "head-tail-with-lines", "lossy": True,
                                    "source_sha256": item["source_sha256"]})
    required = {"policy-v3", "dry-run-log"}
    missing = sorted(required - set(selected))
    return {"request": request, "builder_version": BUILDER_VERSION,
            "task_id": task["task_id"], "candidate_item_ids": [d["id"] for d in index],
            "selected_item_ids": selected, "dropped": dropped,
            "body_read_ids": reads, "transformations": transformations,
            "budget": {"serialized_request_tokens": measure(request), "local_input_limit": limit,
                       "output_reserve": output_reserve, "framing_margin": framing_margin},
            "warnings": ["missing_evidence:" + x for x in missing],
            "ready_for_review": not missing}


def trim_action_groups(prefix, groups, limit):
    """Each group is one assistant tool-call message and all its tool results."""
    groups = copy.deepcopy(groups)
    seen_ids = set()
    for group in groups:
        if not group or group[0].get("role") != "assistant":
            raise ValueError("incomplete_action_group")
        calls = [c["id"] for c in group[0].get("tool_calls", [])]
        results = [m.get("tool_call_id") for m in group[1:] if m.get("role") == "tool"]
        if (not calls or len(calls) != len(set(calls)) or set(calls) & seen_ids
                or len(results) != len(group) - 1 or sorted(calls) != sorted(results)):
            raise ValueError("incomplete_action_group")
        seen_ids.update(calls)
    removed = 0
    def assemble():
        notice = [{"role": "system", "content": f"已移除 {removed} 组动作；缺证据时回读原文。"}] if removed else []
        return copy.deepcopy(prefix) + notice + [m for group in groups for m in group]
    while measure(assemble()) > limit and len(groups) > 1:
        groups.pop(0)
        removed += 1
    messages = assemble()
    if measure(messages) > limit:
        raise ValueError("latest_complete_group_overflow")
    return {"messages": messages, "removed_groups": removed, "tokens": measure(messages)}
