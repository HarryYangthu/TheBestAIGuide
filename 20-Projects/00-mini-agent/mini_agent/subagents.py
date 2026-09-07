"""Optional lesson 06: two separate model contexts, read-only tools, bounded loops."""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from .providers import LiveModel
from .tools import ToolBox, schemas


class DemoReader:
    mode = "demo"
    def __init__(self, path):
        self.path, self.called = path, False
    def respond(self, messages, tools):
        if not self.called:
            self.called = True
            return {"role": "assistant", "tool_calls": [{"id": "read-1", "type": "function", "function":
                    {"name": "read_file", "arguments": json.dumps({"path": self.path})}}]}, {}
        return {"role": "assistant", "content": messages[-1]["content"]}, {}


def reader(path, docs, output, mode):
    provider = DemoReader(path) if mode == "demo" else LiveModel()
    tools = [x for x in schemas(1) if x["function"]["name"] == "read_file"]
    box = ToolBox(docs, output, 1)
    messages = [{"role": "system", "content": "你只负责读取指定文件，提取认证、超时、重试原文。不得修改文件。"},
                {"role": "user", "content": f"读取 {path}，返回原文与行号。"}]
    status = "budget_exhausted"
    for _ in range(4):
        message, _usage = provider.respond(messages, tools)
        messages.append(message)
        calls = message.get("tool_calls") or []
        if not calls:
            status = "completed"
            break
        if len(calls) > 4:
            raise ValueError("too_many_child_tool_calls")
        for call in calls:
            try:
                args = json.loads(call["function"]["arguments"])
                if call["function"]["name"] != "read_file" or args.get("path") != path:
                    raise ValueError("child may only read its assigned document")
                result = {"ok": True, "result": box.read_file(**args)}
            except (ValueError, TypeError, KeyError, OSError) as error:
                result = {"ok": False, "error": type(error).__name__}
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result, ensure_ascii=False)})
    return {"assigned_file": path, "mode": mode, "status": status, "messages": messages}


def delegate(docs, output, mode="demo"):
    output = Path(output)
    if output.exists():
        raise ValueError("choose a new output directory")
    output.mkdir(parents=True)
    paths = ["v1.md", "v2.md"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(reader, path, docs, output, mode) for path in paths]
        children = [future.result() for future in futures]
    receipts = []
    for child in children:
        valid_read = False
        for message in child["messages"]:
            if message["role"] == "tool":
                result = json.loads(message["content"])
                valid_read |= result.get("ok", False) and result.get("result", {}).get("path") == child["assigned_file"]
        receipts.append({"file": child["assigned_file"], "read_observed": valid_read,
                         "finished": child["status"] == "completed"})
    summary = {"mode": mode, "receipts": receipts, "passed": all(x["read_observed"] and x["finished"] for x in receipts),
               "scope": "只验证独立上下文、受限读取与结束；不评估子 Agent 自然语言总结质量，不宣称优于单 Agent。"}
    for child in children:
        (output / (child["assigned_file"] + ".trace.json")).write_text(json.dumps(child, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "delegation.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary
