"""Real API entrypoint. Tests and replay fixtures are separate commands."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from adapter import ROOT, AdapterError, OpenAIAdapter, assistant_message, parse_structured

PARAMETERS = {"type": "object", "properties": {"path": {"type": "string", "enum": ["notes.txt"]}},
              "required": ["path"], "additionalProperties": False}
TOOL = {"type": "function", "function": {"name": "read_file", "description": "读取仿真任务说明 notes.txt",
        "strict": True, "parameters": PARAMETERS}}
SCHEMA = {"type": "object", "properties": {
    "commands": {"type": "array", "items": {"type": "string"}},
    "artifacts": {"type": "array", "items": {"type": "string"}}},
    "required": ["commands", "artifacts"], "additionalProperties": False}


def tool_result(call, notes):
    if call["name"] != "read_file":
        raise AdapterError("unknown_tool", "工具名不在白名单")
    errors = list(Draft202012Validator(PARAMETERS).iter_errors(call["arguments"]))
    if errors:
        raise AdapterError("tool_schema", errors[0].message)
    return {"role": "tool", "tool_call_id": call["id"], "content": notes}


def summary_acceptance(value, notes):
    expected = {"commands": [], "artifacts": []}
    for line in notes.splitlines():
        if line.startswith("执行："):
            expected["commands"].append(line.removeprefix("执行："))
        elif line.startswith("产物："):
            expected["artifacts"].extend(line.removeprefix("产物：").split("、"))
    checks = {key: sorted(value[key]) == sorted(expected[key]) for key in expected}
    return {"passed": all(checks.values()), "checks": checks}


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(mode, output):
    output.mkdir(parents=True, exist_ok=False)
    notes = (ROOT / "examples/notes.txt").read_text(encoding="utf-8")
    (output / "notes.txt").write_text(notes, encoding="utf-8")
    adapter = None
    result = dict(mode=mode, status="failed", error=None, acceptance=None)
    try:
        adapter = OpenAIAdapter.from_env()
        if mode in ("tool", "stream-tools"):
            messages = [{"role": "user", "content": "读取 notes.txt，提取仿真命令和产物路径；本轮只整理执行计划。"}]
            response = adapter.request(messages, stream=mode == "stream-tools", tools=[TOOL],
                tool_choice={"type": "function", "function": {"name": "read_file"}}, parallel_tool_calls=False)
            messages.append(assistant_message(response))
            if not response["tool_calls"]:
                raise AdapterError("expected_tool", "本次任务需要 read_file 请求")
            for call in response["tool_calls"]:
                messages.append(tool_result(call, notes))
            save(output / "messages.json", messages)
            response = adapter.request(messages, tools=[TOOL], tool_choice="none")
        else:
            messages = [{"role": "user", "content": "根据下面任务说明提取 commands 和 artifacts 两个字符串数组。逐字保留执行命令与完整产物路径，不执行命令。\n" + notes}]
            options = {}
            if mode == "structured":
                options["response_format"] = {"type": "json_schema", "json_schema": {"name": "simulation_plan", "strict": True, "schema": SCHEMA}}
            response = adapter.request(messages, stream=mode == "stream", on_text=lambda text: print(text, end="", flush=True), **options)
            if mode == "stream": print()
        (output / "answer.txt").write_text(response["content"] or "", encoding="utf-8")
        if mode == "structured":
            value = parse_structured(response, SCHEMA)
            save(output / "summary.json", value)
            saved = json.loads((output / "summary.json").read_text(encoding="utf-8"))
            result["acceptance"] = summary_acceptance(saved, notes)
            if not result["acceptance"]["passed"]:
                raise AdapterError("acceptance_failed", "命令或产物路径与任务说明不一致")
        result["status"] = "completed"
    except AdapterError as exc:
        result["error"] = exc.record()
    finally:
        if adapter:
            save(output / "requests-and-responses.json", adapter.records)
            result["usage"] = adapter.ledger.summary()
            adapter.client.close()
        save(output / "run.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["text", "tool", "stream", "stream-tools", "structured"], default="text")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or ROOT / "runs" / (args.mode + "-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    if output.exists(): parser.error("输出目录已存在，请使用新目录")
    result = run(args.mode, output)
    print(f"status={result['status']} code={result['error']['code'] if result['error'] else 'none'}")
    print(f"artifacts={output}")
    return result["status"] != "completed"


if __name__ == "__main__": raise SystemExit(main())
