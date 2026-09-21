"""Offload/read-back, version refresh and cache identity for the same release task."""
import os
import tempfile
from datetime import datetime
from pathlib import Path

from builder import resolve_source, sha256
from context import dumps


def offload(directory, document, tenant):
    """One immutable body per hash; only the authenticated caller chooses tenant."""
    directory.mkdir(parents=True, exist_ok=True)
    digest = sha256(document["body"])
    path = directory / (digest + ".txt")
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory, delete=False) as f:
        f.write(document["body"])
        temporary = Path(f.name)
    os.replace(temporary, path)
    return {"file": path.name, "sha256": digest, "tenant": tenant,
            "source_id": document["id"], "version": document["version"]}


def read_back(directory, reference, tenant, start=1, limit=4):
    # Reference metadata belongs to the trusted state store, not a model argument.
    if reference["tenant"] != tenant:
        raise PermissionError("reference_tenant_mismatch")
    if start < 1 or not 1 <= limit <= 20:
        raise ValueError("invalid_line_range")
    path = (directory / reference["file"]).resolve()
    if not path.is_relative_to(directory.resolve()):
        raise PermissionError("invalid_reference_path")
    body = path.read_text(encoding="utf-8")
    if sha256(body) != reference["sha256"]:
        raise ValueError("source_changed")
    lines = body.splitlines()
    end = min(start - 1 + limit, len(lines))
    return {"source_id": reference["source_id"], "version": reference["version"],
            "lines": [{"line": i + 1, "text": lines[i]} for i in range(start - 1, end)],
            "next_start": end + 1 if end < len(lines) else None}


def cache_identity(model, tenant, policy_version, tools_version, prefix):
    """A local identity example, not a provider prompt-cache control API."""
    return sha256(dumps({"model": model, "tenant": tenant, "policy_version": policy_version,
                         "tools_version": tools_version, "prefix": prefix}))


def refresh_policy(task, index, tenant):
    """Re-read only an authorized source with the explicitly requested version."""
    candidates = [d for d in index if d["tenant"] == tenant and d["kind"] == "policy"
                  and d["service"] == task["service"] and d["environment"] == task["environment"]
                  and d["version"] == task["policy_version"] and d["status"] == "active"
                  and (not d.get("valid_until") or datetime.fromisoformat(d["valid_until"]) > datetime.fromisoformat(task["as_of"]))]
    if not candidates:
        return {"status": "UNKNOWN", "reason": "requested_version_unavailable"}
    bodies = []
    for item in candidates:
        try:
            text = resolve_source(item["path"]).read_text(encoding="utf-8")
        except (OSError, ValueError):
            return {"status": "UNKNOWN", "reason": "source_unavailable"}
        bodies.append((item, text))
    if len({sha256(text) for _, text in bodies}) != 1:
        return {"status": "UNKNOWN", "reason": "conflicting_sources"}
    item, text = bodies[0]
    return {"status": "CURRENT", "version": item["version"], "source_id": item["id"],
            "body": text, "source_sha256": sha256(text), "checked_as_of": task["as_of"]}


def scoped_summary(events, task_id):
    """Input order is the event order within this task; hypotheses stay separate."""
    facts = {}
    for event in events:
        if event["task_id"] != task_id or event["kind"] not in {"constraint", "observation", "pending"}:
            continue
        facts[event["key"]] = {"value": event["value"], "source_id": event["id"], "kind": event["kind"]}
    return {"task_id": task_id, "facts": facts, "method": "scoped-structured-extract-v1", "lossy": True}


def evidence_metrics(required, selected):
    required, selected = set(required), set(selected)
    overlap = len(required & selected)
    return {"recall": overlap / len(required) if required else None,
            "precision": overlap / len(selected) if selected else None,
            "required": len(required), "selected": len(selected)}
