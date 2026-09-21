"""Run local context-engineering mechanisms and write a single comparison report."""
import argparse
import copy
import platform

from builder import build_context, select_documents, trim_action_groups
from context import ROOT, dumps, initial_messages, measure, read_fixture, save_json
from context_strategies import (cache_identity, evidence_metrics, offload, read_back,
                                refresh_policy, scoped_summary)


def inputs():
    return (read_fixture("engineering/task.json"), read_fixture("engineering/index.json"),
            read_fixture("history.json"))


def action_group(label, body):
    return [{"role": "assistant", "content": None, "tool_calls": [{"id": label, "type": "function",
             "function": {"name": "read_evidence", "arguments": dumps({"evidence_id": label, "start": 1})}}]},
            {"role": "tool", "tool_call_id": label, "content": body}]


def run(output):
    task, index, history = inputs()
    output.mkdir(parents=True, exist_ok=True)
    variants = {}
    # Both index entries point to the same policy evidence; do not double-count it.
    aliases = {"policy-copy": "policy-v3"}
    def metrics(ids):
        return evidence_metrics({"policy-v3", "dry-run-log"}, {aliases.get(x, x) for x in ids})
    for name, options in [("current", {}), ("without_deduplication", {"deduplicate": False}),
                          ("without_log_compaction", {"compact_log": False})]:
        envelope = build_context(task, index, history, "alpha", **options)
        save_json(output / name / "envelope.json", envelope)
        save_json(output / name / "request.json", envelope["request"])
        variants[name] = {"input_tokens": envelope["budget"]["serialized_request_tokens"],
                          "within_budget": True,
                          **metrics(envelope["selected_item_ids"])}
    current = build_context(task, index, history, "alpha")
    allowed = [d for d in index if d["tenant"] == "alpha"]
    # Full authorized baseline keeps data boundaries, but does not scope-filter or compact.
    full_request = copy.deepcopy(current["request"])
    full_request["messages"] = initial_messages(task)
    full_request["messages"] += [{"role": "user", "content": dumps({"data_only": True, **d,
        "body": (ROOT / "fixtures" / d["path"]).read_text(encoding="utf-8")})} for d in allowed]
    full_request["messages"].append({"role": "user", "content": dumps(history)})
    full_tokens = measure(full_request)
    variants["full_authorized"] = {"input_tokens": full_tokens, "within_budget": full_tokens <= 3100,
        **metrics({d["id"] for d in allowed})}
    minimal = copy.deepcopy(current["request"])
    minimal["messages"] = initial_messages(task)
    variants["minimal"] = {"input_tokens": measure(minimal), "within_budget": measure(minimal) <= 3100,
                          **metrics(set())}
    save_json(output / "full_authorized" / "request.json", full_request)
    save_json(output / "minimal" / "request.json", minimal)

    conflict_index = index + [dict(index[0], id="policy-conflict", path="engineering/conflicting-policy.txt")]
    try:
        build_context(task, conflict_index, history, "alpha")
    except ValueError as error:
        conflict = str(error).startswith("unresolved_conflict")
    else:
        conflict = False
    try:
        build_context(task, index, history, "alpha", window=901)
    except ValueError as error:
        overflow = str(error) == "mandatory_overflow"
    else:
        overflow = False
    events = read_fixture("engineering/events.json")
    summary = scoped_summary(events, task["task_id"])
    prefix = []
    for event in events:
        if measure(prefix + [event]) > 180:
            break
        prefix.append(event)
    naive = scoped_summary(prefix, task["task_id"])
    expected = {"allow_report": False, "verification_passed": False, "next_step": "核对检查执行权限"}
    def preserved(value):
        return sum(type(value["facts"].get(k, {}).get("value")) is type(v)
                   and value["facts"].get(k, {}).get("value") == v for k, v in expected.items())
    save_json(output / "scoped-summary.json", summary)
    groups = [action_group("old-read", "启动成功。" * 200), action_group("dry-run-log", "verification_check=FAILED")]
    trimmed = trim_action_groups(initial_messages(task), groups, 260)
    save_json(output / "trimmed-messages.json", trimmed)
    documents, _, _ = select_documents(task, index, "alpha")
    log = next(d for d in documents if d["id"] == "dry-run-log")
    reference = offload(output / "objects", log, "alpha")
    tail = read_back(output / "objects", reference, "alpha", 83, 2)
    save_json(output / "reference.json", reference)
    save_json(output / "read-back.json", tail)
    prefix_text = "审核任务资料；只读，不执行发布。"
    key = cache_identity("configured-model", "alpha", "v3", "tools-v1", prefix_text)
    cache_changed = key != cache_identity("configured-model", "alpha", "v4", "tools-v1", prefix_text)
    refresh = refresh_policy(task, index, "alpha")
    unknown = refresh_policy({**task, "policy_version": "v4"}, index, "alpha")
    result = {"task_id": task["task_id"], "python": platform.python_version(),
        "evidence_unit": "canonical evidence id", "evidence_aliases": aliases,
        "variants": variants, "checks": {
            "foreign_body_not_read": "other-tenant" not in current["body_read_ids"],
            "foreign_body_not_in_request": "PRIVATE_FIXTURE_BETA_ONLY" not in dumps(current["request"]),
            "wrong_scope_excluded": "scratch-note" not in current["selected_item_ids"],
            "duplicate_excluded": "policy-copy" not in current["selected_item_ids"],
            "expired_excluded": "expired-note" not in current["selected_item_ids"],
            "conflict_rejected": conflict, "overflow_rejected": overflow,
            "failure_not_rewritten": summary["facts"]["verification_passed"]["value"] is False,
            "failure_source_preserved": summary["facts"]["verification_passed"]["source_id"] == "s3",
            "action_group_preserved": trimmed["removed_groups"] == 1 and trimmed["messages"][-1]["tool_call_id"] == "dry-run-log",
            "read_back_preserves_failure": "verification_check=FAILED" in tail["lines"][0]["text"],
            "policy_change_invalidates_key": cache_changed,
            "refresh_missing_is_unknown": unknown["status"] == "UNKNOWN",
            "untrusted_note_remains_data": '"trust":"untrusted"' in current["request"]["messages"][-1]["content"],
        }, "compression": {"prefix_preserved": preserved(naive), "structured_preserved": preserved(summary),
                             "required": len(expected), "raw_tokens": measure(events), "summary_tokens": measure(summary)},
        "refresh": {k: v for k, v in refresh.items() if k != "body"},
        "real_model_trials": 0, "runtime_release_actions": 0}
    assert all(result["checks"].values()), result["checks"]
    save_json(output / "result.json", result)
    report = "# 上下文工程对照实验\n\n固定任务：stats workspace 报告审核；全部为本地机制实验。\n\n"
    report += "| 策略 | 请求编码 token | 预算内 | 证据召回 | 证据精确率 |\n|---|---:|---|---:|---:|\n"
    for name, row in variants.items():
        report += f"| {name} | {row['input_tokens']} | {row['within_budget']} | {row['recall']} | {row['precision']} |\n"
    report += "\n## 机制检查\n\n| 检查 | 结果 |\n|---|---|\n"
    report += "\n".join(f"| {key} | {value} |" for key, value in result["checks"].items())
    report += f"\n\n结构化事实保留：{preserved(naive)}/3 → {preserved(summary)}/3。\n"
    report += "\n真实模型调用：0；位置效应与模型抵抗注入的结果需运行 live_evaluate.py。\n"
    (output / "report.md").write_text(report, encoding="utf-8")
    print("variants=" + str(len(variants)))
    print(f"checks={sum(result['checks'].values())}/{len(result['checks'])}")
    print(f"scoped_facts={preserved(summary)}/{len(expected)}")
    print("model_calls=0")
    print("artifacts=" + str(output.relative_to(ROOT)))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="runs/engineering")
    args = parser.parse_args()
    run(ROOT / args.out)
