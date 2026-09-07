"""Lesson 07: run the curriculum and inspect outputs, including expected failures."""
import json
from pathlib import Path
from .providers import DemoModel
from .runtime import run
from .tools import ToolBox
from .context import pack
from .memory import set_format, resolve_format
from .parallel import benchmark
from .evaluate import evaluate

ROOT = Path(__file__).resolve().parents[1]


def curriculum(output):
    output = Path(output)
    if output.exists():
        raise ValueError("choose a new curriculum output directory")
    output.mkdir(parents=True)
    docs = ROOT / "fixtures/docs"
    stages = []
    for stage in range(1, 8):
        result = run(output / f"stage-{stage:02d}", docs, DemoModel(stage), stage)
        stages.append({"stage": stage, "passed": result["passed"], "mode": result["mode"]})
    evidence = {}
    # Actual context packing, preserving the last assistant/tool pair.
    messages = [{"role": "system", "content": "保留系统规则"}, {"role": "user", "content": "保留当前任务"}]
    for i in range(5):
        messages += [{"role": "assistant", "tool_calls": [{"id": str(i), "type": "function", "function": {"name": "read_file", "arguments": "{}"}}]},
                     {"role": "tool", "tool_call_id": str(i), "content": "资料" * 400}]
    packed, stats = pack(messages, 1500)
    evidence["context"] = {**stats, "passed": stats["removed_groups"] > 0 and packed[-1] == messages[-1] and packed[:2] == messages[:2]}
    memory = output / "memory.json"
    set_format(memory, "bullets")
    remembered = resolve_format(memory)
    overridden = resolve_format(memory, "table")
    # These produce actual reports whose format is affected by remembered/current preferences.
    mem_run = run(output / "memory-recall", docs, DemoModel(4), 4, report_format=remembered[0], format_source=remembered[1])
    override_run = run(output / "memory-override", docs, DemoModel(4), 4, report_format=overridden[0], format_source=overridden[1])
    set_format(memory, "delete")
    deleted = resolve_format(memory)
    evidence["memory"] = {"recalled": remembered, "current_override": overridden, "after_delete": deleted,
                          "passed": remembered == ("bullets", "memory") and overridden == ("table", "current_request")
                          and deleted == ("table", "default") and mem_run["passed"] and override_run["passed"]}
    metrics = benchmark(ToolBox(docs, output, 6).read_file, ["v1.md", "v2.md"])
    evidence["parallel"] = {**metrics, "passed": metrics["same_results"]}
    short = run(output / "expected-budget-failure", docs, DemoModel(7), 7, max_steps=1)
    evidence["budget"] = {"status": short["status"], "passed": short["status"] == "budget_exhausted" and not short["passed"]}
    # Mutate a completed report; a mere file-exists checker would wrongly pass this.
    wrong = output / "expected-citation-failure"
    run(wrong, docs, DemoModel(7), 7)
    report = json.loads((wrong / "report.json").read_text(encoding="utf-8"))
    report["changes"][0]["source"]["path"] = "preview.md"
    (wrong / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    rejected = evaluate(wrong, docs)
    evidence["citation_rejection"] = {"failed_checks": [x["check"] for x in rejected["checks"] if not x["passed"]],
                                     "passed": not rejected["passed"]}
    summary = {"mode": "demo", "stages": stages, "experiments": evidence,
               "passed": all(x["passed"] for x in stages) and all(x["passed"] for x in evidence.values()),
               "live_model_validated": False,
               "meaning": "PASS 代表教学机制与固定任务验收通过；真实模型能力需另行 live 运行。"}
    (output / "completion.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# 项目完成报告", "", f"模式：demo；整体：{'PASS' if summary['passed'] else 'FAIL'}。", "",
             "| 项目 | 结果 |", "| --- | --- |"]
    lines += [f"| 阶段 {x['stage']:02d} | {'PASS' if x['passed'] else 'FAIL'} |" for x in stages]
    lines += [f"| {name} | {'PASS' if x['passed'] else 'FAIL'} |" for name, x in evidence.items()]
    lines += ["", summary["meaning"], "", "两个 expected-* 目录应为 FAIL；正确识别这些失败，才算相应实验通过。"]
    (output / "completion.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary
