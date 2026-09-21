"""Replay explicit protocol fixtures, never present them as real model responses."""
import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from adapter import ROOT, AdapterError, StreamAccumulator, UsageLedger, normalize_message, parse_structured
from live import SCHEMA, summary_acceptance


def replay(chunks):
    collector = StreamAccumulator()
    for chunk in chunks:
        collector.feed(chunk)
    return collector.finish()


def experiment(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    path = ROOT / "examples/stream-tools.jsonl"
    chunks = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    (output / "stream-tools.jsonl").write_bytes(path.read_bytes())
    scenarios = [("interleaved_tools", chunks, "none"),
                 ("missing_finish", chunks[:-2], "incomplete_response"),
                 ("missing_usage", chunks[:-1], "none")]
    truncated = copy.deepcopy(chunks)
    truncated[-2]["choices"][0]["finish_reason"] = "length"
    scenarios.append(("length_limit", truncated, "output_truncated"))
    broken = copy.deepcopy(chunks)
    broken[3]["choices"][0]["delta"]["tool_calls"][0]["function"]["arguments"] = ""
    scenarios.append(("broken_arguments", broken, "invalid_arguments"))
    table = []
    normalized = None
    for name, events, expected in scenarios:
        observed, response = "none", None
        try: response = replay(events)
        except AdapterError as exc: observed = exc.code
        if name == "interleaved_tools": normalized = response
        table.append(dict(case=name, expected=expected, observed=observed, matched=expected == observed,
                          usage_known=response is not None and response["usage"]["total_tokens"] is not None))
    ledger = UsageLedger()
    ledger.add(normalized["usage"])
    ledger.add(None)
    ledger.add({"prompt_tokens": 4})
    # Complete schema, wrong facts: model formatting and task acceptance are separate.
    value = {"commands": ["python missing.py"], "artifacts": ["invented.json"]}
    response = normalize_message({"content": json.dumps(value)}, "stop")
    checked = parse_structured(response, SCHEMA)
    accepted = summary_acceptance(checked, (ROOT / "examples/notes.txt").read_text(encoding="utf-8"))
    result = dict(mode="explicit_protocol_replay", scenarios=table, normalized=normalized,
                  usage=ledger.summary(), structured_schema_passed=True, structured_acceptance=accepted)
    (output / "comparison.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# 模型接入协议实验", "", "由显式协议样本实际回放生成；未调用模型。", "",
             "| 场景 | 预期 | 实际 | 观察到 total_tokens | 符合预期 |", "|---|---|---|---|---|"]
    for row in table:
        lines.append(f"| {row['case']} | {row['expected']} | {row['observed']} | {row['usage_known']} | {row['matched']} |")
    lines += ["", "三个请求的已知 token 合计与覆盖情况：", "", "| 字段 | 已知合计 | 有值请求 | 缺失请求 |", "|---|---:|---:|---:|"]
    for key, value in result["usage"]["fields"].items():
        lines.append(f"| {key} | {value['known_sum']} | {value['reported_requests']} | {value['missing_requests']} |")
    lines += ["", f"结构化字段通过 Schema，但事实验收：{accepted['passed']}。", ""]
    (output / "comparison.md").write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    path = args.output or ROOT / "runs" / ("replay-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    result = experiment(path)
    rows = result["scenarios"]
    print(f"mode=explicit_protocol_replay cases={len(rows)} matched={sum(row['matched'] for row in rows)}")
    print("tool_calls=" + str(len(result["normalized"]["tool_calls"])))
    print(f"requests={result['usage']['request_count']} fully_metered={result['usage']['fully_metered_requests']}")
    print(f"artifacts={path}")
    raise SystemExit(0 if all(row["matched"] for row in rows) else 1)
