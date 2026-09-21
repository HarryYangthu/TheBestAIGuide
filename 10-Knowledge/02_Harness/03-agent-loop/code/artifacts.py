"""将每次运行保存到独立目录，保留输入、响应、消息和产物。"""
from datetime import datetime, timezone
import difflib
import json
from pathlib import Path
import shutil
import uuid

ROOT = Path(__file__).resolve().parents[1]


def new_run(stage, output_root=None):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    directory = Path(output_root or ROOT / "runs") / f"{stage}-{stamp}-{uuid.uuid4().hex[:6]}"
    workspace = directory / "workspace"
    workspace.mkdir(parents=True)
    shutil.copyfile(ROOT / "notes.txt", workspace / "notes.txt")
    shutil.copyfile(ROOT / "examples" / "stats.py", workspace / "stats.py")
    return directory, workspace


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def final_text(messages):
    for message in reversed(messages):
        if message["role"] != "assistant":
            continue
        for call in message.get("tool_calls", []):
            if call["name"] == "finish":
                return call["arguments"].get("summary", "")
        if message.get("content"):
            return message["content"]
    return ""


def save_run(directory, result, records, before_source):
    directory = Path(directory)
    messages = result.get("messages", [])
    write_json(directory / "result.json", result)
    write_json(directory / "messages.json", messages)
    for key, filename in (("request", "requests.jsonl"), ("response", "responses.jsonl")):
        rows = [{"attempt": index + 1, key: record.get(key), "error": record.get("error")}
                for index, record in enumerate(records)]
        (directory / filename).write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    (directory / "trace.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in result.get("trace", [])), encoding="utf-8")
    summary = final_text(messages)
    (directory / "answer.md").write_text(summary + "\n", encoding="utf-8")
    after = (directory / "workspace" / "stats.py").read_text(encoding="utf-8")
    diff = "".join(difflib.unified_diff(before_source.splitlines(True), after.splitlines(True), fromfile="before/stats.py", tofile="after/stats.py"))
    (directory / "changes.diff").write_text(diff, encoding="utf-8")
    acceptance = result.get("acceptance")
    lines = ["# 本次运行记录", "", f"- 阶段：{result.get('stage', '')}",
             f"- 执行方式：{result.get('execution_mode', 'live_api')}",
             f"- 模型：{result.get('model', '')}",
             f"- 状态：{result.get('status')} / {result.get('reason')}",
             f"- 模型请求尝试：{result.get('model_calls', 0)}", "", "## 输出", "", summary or "本次未生成正文。", ""]
    if acceptance is not None:
        lines += ["## 当前文件检查", "", f"整体通过：{acceptance['passed']}", "", "| 检查项 | 通过 | 详情 |", "|---|---|---|"]
        for item in acceptance["checks"]:
            detail = str(item["detail"]).replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {item['name']} | {item['passed']} | {detail} |")
        lines += ["", f"文件 SHA-256：`{acceptance['source_sha256']}`", "", "## 代码变化", "", "```diff", diff.rstrip() or "（无变化）", "```", ""]
    lines += ["## 对照文件", "", "- requests.jsonl：每次发给 API 的请求。", "- responses.jsonl：API 原始响应或请求错误类型。", "- messages.json：循环保存的完整消息。", "- trace.jsonl：执行事件。", "- workspace/：本次使用与修改的文件。", ""]
    (directory / "report.md").write_text("\n".join(lines), encoding="utf-8")


def print_summary(directory, result):
    print(f"status={result['status']} reason={result['reason']} model_calls={result['model_calls']}")
    if result.get("acceptance") is not None:
        print(f"acceptance={result['acceptance']['passed']}")
    print(f"artifacts={directory}")
