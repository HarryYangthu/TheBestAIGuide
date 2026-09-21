"""Deterministic counterexamples; never calls a model."""
import argparse
import copy
import importlib.metadata

from context import (ROOT, crop_contains, crop_tool_result, dumps, extract_history,
                     initial_messages, isolate_worker, load_on_demand, measure, pack,
                     read_fixture, save_json, validate_summary)


def run(output, window):
    task = read_fixture("task.json")
    history = read_fixture("history.json")
    index = read_fixture("index.json")
    parent = initial_messages(task)
    alias = parent
    alias.append({"role": "user", "content": "其他任务：scratch timeout_ms=9000"})
    aliased_changed_parent = len(parent) == 3
    isolated = isolate_worker(parent, task)
    shallow = parent.copy()
    shallow[0]["content"] = "覆盖父级系统消息"
    shallow_changed_parent = parent[0]["content"] == "覆盖父级系统消息"
    isolated[0]["content"] = "独立 reviewer 系统消息"
    isolated_unchanged_parent = parent[0]["content"] != isolated[0]["content"]

    documents = load_on_demand(task, index)
    policy = next(item for item in documents if item["id"] == "policy-v3")
    log = next(item for item in documents if item["id"] == "dry-run-log")
    clipped = crop_tool_result(log)
    required_text = "verification_check=FAILED"
    naive = log["body"][:180]
    good = extract_history(history)
    bad = read_fixture("bad-summary.json")
    good_check = validate_summary(good, history)
    bad_check = validate_summary(bad, history)
    budgeted = pack(initial_messages(task), [policy, good],
                    [clipped], window=window, output_reserve=600, framing_margin=300)
    # A failed dry run is a required release gate. If an optional block was dropped,
    # the consumer must stop, rather than infer success from missing evidence.
    has_check = any(required_text in msg["content"] for msg in budgeted["messages"])
    acceptance = {"required_facts_preserved": good_check["accepted"],
                  "verification_evidence_present": has_check,
                  "report_decision": "BLOCKED" if has_check else "NEEDS_EVIDENCE"}
    result = {
        "isolation": {"alias_changed_parent": aliased_changed_parent,
                      "shallow_changed_parent": shallow_changed_parent,
                      "isolated_unchanged_parent": isolated_unchanged_parent,
                      "unrelated_scratch_leaked": any("scratch" in x["content"] for x in isolated)},
        "loading": {"indexed": len(index), "body_reads": len(documents),
                    "selected": [d["id"] for d in documents]},
        "crop": {"naive_kept_failure": required_text in naive,
                 "structured_kept_failure": crop_contains(clipped, required_text),
                 "raw_tokens": measure(log), "cropped_tokens": measure(clipped)},
        "compression": {"bad": bad_check, "good": good_check,
                        "history_tokens": measure(history), "summary_tokens": measure(good)},
        "budget": {k: v for k, v in budgeted.items() if k != "messages"},
        "acceptance": acceptance,
        "versions": {name: importlib.metadata.version(name) for name in ("tiktoken", "openai")},
    }
    save_json(output / "input-history.json", history)
    save_json(output / "loaded-documents.json", documents)
    save_json(output / "cropped-log.json", clipped)
    save_json(output / "summary.json", good)
    save_json(output / "messages.json", budgeted["messages"])
    save_json(output / "result.json", result)
    rows = [
        ("独立上下文", "浅拷贝改变父消息", str(shallow_changed_parent)),
        ("按需加载", "索引数 / 正文读取数", f"{len(index)} / {len(documents)}"),
        ("结果裁剪", "头部截断 / 结构裁剪保留失败", f"{required_text in naive} / {crop_contains(clipped, required_text)}"),
        ("历史压缩", "有损摘要 / 校验摘要事实数", f"{bad_check['preserved']} / {good_check['preserved']}"),
        ("预算", "输入编码 token / 本地上限", f"{budgeted['serialized_input_tokens']} / {budgeted['local_input_limit']}"),
    ]
    report = "# stats 发布上下文\n\n| 实验 | 观察 | 实际值 |\n|---|---|---|\n"
    report += "\n".join(f"| {a} | {b} | {c} |" for a, b, c in rows)
    report += f"\n\n报告检查：**{acceptance['report_decision']}**。查看 `cropped-log.json` 的原始行号定位失败。\n"
    (output / "report.md").write_text(report, encoding="utf-8")
    print(f"selected={len(documents)}/{len(index)}")
    print(f"summary_facts={good_check['preserved']}/{good_check['required']}")
    print(f"input_tokens={budgeted['serialized_input_tokens']} limit={budgeted['local_input_limit']}")
    print("report_decision=" + acceptance["report_decision"])
    print("artifacts=" + str(output.relative_to(ROOT)))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--window", type=int, default=2400)
    parser.add_argument("--out", default="runs/default")
    args = parser.parse_args()
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    run(out, args.window)
