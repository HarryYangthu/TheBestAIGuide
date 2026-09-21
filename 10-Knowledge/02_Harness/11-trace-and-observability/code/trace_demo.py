"""Instrument real local concurrent work and an explicit protocol-fixture replay."""
import argparse
import csv
import hashlib
import json
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = {"engine": "trace-v1", "tool": "aggregate-v1", "policy": "reject-invalid-v1", "prompt": "fixture-plan-v1"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Recorder:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.trace_id = uuid.uuid4().hex
        self.zero = time.perf_counter_ns()
        self.lock = threading.Lock()
        self.next_id = 0

    @contextmanager
    def span(self, name, kind, task_id, parent=None, parent_task_id=None, **attrs):
        with self.lock:
            self.next_id += 1
            span_id = f"s{self.next_id:04d}"
        record = {
            "trace_id": self.trace_id, "span_id": span_id,
            "parent_span_id": parent["span_id"] if parent else None,
            "task_id": task_id, "parent_task_id": parent_task_id,
            "name": name, "kind": kind, "status": "ok", "error": None,
            "start_utc": datetime.now(timezone.utc).isoformat(),
            "start_ms": (time.perf_counter_ns() - self.zero) / 1e6,
            "versions": VERSIONS.copy(), "attributes": attrs,
        }
        try:
            yield record
        except Exception as exc:
            if not hasattr(exc, "origin_span_id"):
                exc.origin_span_id = span_id
            record["status"] = "error"
            record["error"] = {"type": type(exc).__name__, "message": str(exc),
                               "origin_span_id": exc.origin_span_id, "is_origin": exc.origin_span_id == span_id}
            raise
        finally:
            record["end_ms"] = (time.perf_counter_ns() - self.zero) / 1e6
            record["duration_ms"] = record["end_ms"] - record["start_ms"]
            with self.lock:
                with self.path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def validate(records):
    by_id = {r["span_id"]: r for r in records}
    if len(by_id) != len(records):
        raise ValueError("duplicate span id")
    if len({r["trace_id"] for r in records}) != 1:
        raise ValueError("multiple trace ids")
    roots = [r for r in records if r["parent_span_id"] is None]
    if len(roots) != 1:
        raise ValueError("need exactly one root")
    for row in records:
        if row["end_ms"] < row["start_ms"]:
            raise ValueError("negative duration")
        if abs(row["duration_ms"] - (row["end_ms"] - row["start_ms"])) > 1e-6:
            raise ValueError("duration differs from interval")
        if row["parent_span_id"]:
            parent = by_id.get(row["parent_span_id"])
            if parent is None:
                raise ValueError("orphan span")
            if not (parent["start_ms"] <= row["start_ms"] <= row["end_ms"] <= parent["end_ms"]):
                raise ValueError("child outside parent interval")
            if row["task_id"] != parent["task_id"] and row["parent_task_id"] != parent["task_id"]:
                raise ValueError("broken parent task link")
    # Follow every chain: a fabricated cycle must not pass just because intervals coincide.
    for row in records:
        seen, current = set(), row
        while current is not None:
            if current["span_id"] in seen:
                raise ValueError("span cycle")
            seen.add(current["span_id"])
            current = by_id.get(current["parent_span_id"])
    return by_id


def union_ms(intervals):
    if not intervals:
        return 0.0
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(end, merged[-1][1])
        else:
            merged.append([start, end])
    return sum(end - start for start, end in merged)


def replay_plan(rec, parent):
    # This is explicitly a fixture read, not a request to a model service.
    with rec.span("model.plan.fixture_replay", "model", "batch", parent,
                  execution_mode="fixture_replay", usage_source="fixtures/provider-response.json",
                  usage_provenance="handwritten_protocol_example", model="fixture-model-v1") as span:
        source = ROOT / "fixtures/provider-response.json"
        response = read_json(source)
        rates = read_json(ROOT / "fixtures/example-rates.json")
        usage = response["usage"]
        span["attributes"].update({"response_sha256": sha(source), "usage": usage,
            "cost_usd": None, "cost_source": "no_live_invoice",
            "illustrative_cost_usd": (usage["input_tokens"] * rates["input_per_million"] + usage["output_tokens"] * rates["output_per_million"]) / 1_000_000,
            "rate_source": "fixtures/example-rates.json", "rate_scope": "arbitrary_example_not_vendor_price"})
        return response["plan"]


def work(rec, parent, item, out, barrier, delay_ms):
    child_task = item["task_id"]
    with rec.span("handoff." + child_task, "handoff", "batch", parent,
                  from_task_id="batch", to_task_id=child_task, input_file=item["input"]) as handoff:
        write_json(out / f"handoff-{child_task}.json", {"trace_id": rec.trace_id,
                   "parent_span_id": handoff["span_id"], "from_task_id": "batch", "to_task_id": child_task, "input": item["input"]})
        with rec.span("task." + child_task, "task", child_task, handoff, "batch",
                      caused_by_span_id=handoff["span_id"]) as task:
            # Deliberate, documented latency injection makes overlap visible on fast disks.
            with rec.span("tool.read_csv", "tool", child_task, task, "batch", injected_delay_ms=delay_ms) as read_span:
                barrier.wait(timeout=5)
                time.sleep(delay_ms / 1000)
                source = ROOT / "fixtures" / item["input"]
                raw = source.read_bytes()
                (out / item["input"]).write_bytes(raw)
                rows = list(csv.DictReader(raw.decode().splitlines()))
                read_span["attributes"].update({"input_sha256": hashlib.sha256(raw).hexdigest(), "row_count": len(rows)})
            with rec.span("tool.aggregate", "tool", child_task, task, "batch", input_file=item["input"]) as aggregate_span:
                total, count = 0, 0
                for number, row in enumerate(rows, 2):
                    if row["status"].strip().casefold() != "paid":
                        continue
                    try:
                        value = Decimal(row["amount"])
                        if not value.is_finite() or value * 100 != (value * 100).to_integral_value():
                            raise InvalidOperation
                        total += int(value * 100)
                        count += 1
                    except (InvalidOperation, ValueError):
                        aggregate_span["attributes"].update({"failed_row": number, "order_id": row["order_id"]})
                        raise ValueError(f"invalid_amount: file={item['input']} row={number} order={row['order_id']}") from None
                artifact = out / f"summary-{child_task}.json"
                write_json(artifact, {"total_cents": total, "paid_rows": count})
                aggregate_span["attributes"].update({"output_file": artifact.name, "output_sha256": sha(artifact)})
            with rec.span("acceptance.summary", "acceptance", child_task, task, "batch", output_file=artifact.name) as check_span:
                expected = read_json(ROOT / "fixtures/expected.json")[child_task]
                accepted = read_json(artifact) == expected
                check_span["attributes"]["accepted"] = accepted
                if not accepted:
                    raise ValueError("artifact_mismatch")
                return {"task_id": child_task, "accepted": accepted, "artifact": artifact.name}


def build_report(out):
    records = [json.loads(line) for line in (out / "trace.jsonl").read_text().splitlines()]
    by_id = validate(records)
    root = next(r for r in records if r["parent_span_id"] is None)
    children = [r for r in records if r["kind"] == "task" and r["parent_task_id"] == "batch"]
    models = [r for r in records if r["kind"] == "model"]
    direct = sorted([r for r in records if r["error"] and r["error"]["is_origin"]], key=lambda r: r["end_ms"])
    known = [m["attributes"].get("cost_usd") for m in models if m["attributes"].get("cost_usd") is not None]
    result = {"trace_id": root["trace_id"], "span_count": len(records), "root_wall_ms": root["duration_ms"],
              "child_duration_sum_ms": sum(r["duration_ms"] for r in children),
              "child_interval_union_ms": union_ms([(r["start_ms"], r["end_ms"]) for r in children]),
              "first_direct_error": direct[0] if direct else None,
              "model_span_count": len(models), "known_cost_spans": len(known),
              "total_model_cost_usd": sum(known) if len(known) == len(models) else None,
              "illustrative_cost_usd": sum(m["attributes"].get("illustrative_cost_usd", 0) for m in models),
              "success_tasks": sum(r["status"] == "ok" for r in children), "failed_tasks": sum(r["status"] == "error" for r in children)}
    result["child_overlap_ms"] = result["child_duration_sum_ms"] - result["child_interval_union_ms"]
    write_json(out / "metrics.json", result)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ordered = sorted(records, key=lambda r: r["start_ms"])
    fig, ax = plt.subplots(figsize=(10, 5))
    for index, row in enumerate(ordered):
        ax.barh(index, max(row["duration_ms"], .15), left=row["start_ms"], color="#dc2626" if row["status"] == "error" else "#2563eb")
    ax.set_yticks(range(len(ordered)), [r["span_id"] + " " + r["name"] for r in ordered])
    ax.invert_yaxis()
    ax.set(xlabel="Milliseconds since recorder start (same process)", title="Measured local spans; read delay deliberately injected")
    fig.tight_layout()
    fig.savefig(out / "timeline.png", dpi=160)
    plt.close(fig)
    lines = ["# 实际本地并行轨迹", "", f"成功子任务 {result['success_tasks']}；失败子任务 {result['failed_tasks']}；span {len(records)}。", "",
             "| 时长指标 | 毫秒 |", "|---|---:|", f"| 根任务墙钟 | {result['root_wall_ms']:.3f} |", f"| 两个子任务时长相加 | {result['child_duration_sum_ms']:.3f} |", f"| 子任务区间并集 | {result['child_interval_union_ms']:.3f} |", f"| 重叠区间量 | {result['child_overlap_ms']:.3f} |", "",
             "模型边界为明确选择的 fixture_replay；输入输出 token 来自手写协议样本。示例费用公式值不表示发生了真实调用或账单。实际模型成本为 null。", "", "![timeline](timeline.png)", "",
             "## 关联和错误", "", "| span | parent | task | kind | status | error origin |", "|---|---|---|---|---|---|"]
    for r in ordered:
        lines.append(f"| {r['span_id']} {r['name']} | {r['parent_span_id']} | {r['task_id']} | {r['kind']} | {r['status']} | {(r['error'] or {}).get('origin_span_id', '')} |")
    if direct:
        row = direct[0]
        chain = [row["span_id"]]
        while by_id[chain[-1]]["parent_span_id"]:
            chain.append(by_id[chain[-1]]["parent_span_id"])
        lines += ["", f"最早记录到的直接异常：{row['error']['message']}。", "", "向父级追溯：" + " → ".join(chain) + "。"]
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    parser.add_argument("--delay-ms", type=float, default=60)
    args = parser.parse_args()
    if args.delay_ms < 0:
        parser.error("delay must be nonnegative")
    args.out.mkdir(parents=True, exist_ok=False)
    write_json(args.out / "manifest.json", {"versions": VERSIONS, "code_sha256": sha(__file__), "delay_ms": args.delay_ms,
               "model_mode": "fixture_replay", "fixtures": {p.name: sha(p) for p in (ROOT / "fixtures").iterdir() if p.is_file()}})
    rec = Recorder(args.out / "trace.jsonl")
    outcomes = []
    with rec.span("task.batch", "task", "batch") as root:
        plan = replay_plan(rec, root)
        barrier = threading.Barrier(len(plan))
        with ThreadPoolExecutor(max_workers=len(plan)) as pool:
            futures = [(item, pool.submit(work, rec, root, item, args.out, barrier, args.delay_ms)) for item in plan]
            for item, future in futures:
                try:
                    outcomes.append(future.result())
                except Exception as exc:
                    outcomes.append({"task_id": item["task_id"], "accepted": False, "error": str(exc), "origin_span_id": getattr(exc, "origin_span_id", None)})
        root["status"] = "error" if any(not o["accepted"] for o in outcomes) else "ok"
        root["attributes"]["child_results"] = outcomes
        write_json(args.out / "results.json", outcomes)
    metrics = build_report(args.out)
    print("model_mode=fixture_replay")
    print(f"success_tasks={metrics['success_tasks']} failed_tasks={metrics['failed_tasks']}")
    print(f"root_wall_ms={metrics['root_wall_ms']:.3f} child_sum_ms={metrics['child_duration_sum_ms']:.3f}")
    print(f"artifacts={args.out}")


if __name__ == "__main__":
    main()
