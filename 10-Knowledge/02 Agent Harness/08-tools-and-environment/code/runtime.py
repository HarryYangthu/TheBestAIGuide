"""A small tool registry. Local Python execution is NOT an OS sandbox."""
from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]


class ToolError(Exception):
    def __init__(self, code, message, retryable=False):
        self.code, self.message, self.retryable = code, message, retryable
        super().__init__(message)


def validate(value, schema, field="arguments"):
    """Validate the JSON Schema subset used by this chapter, not all JSON Schema."""
    types = {"object": dict, "string": str, "integer": int, "array": list, "boolean": bool}
    if type(value) is not types[schema["type"]]:
        raise ToolError("invalid_arguments", f"{field}: expected {schema['type']}")
    if schema["type"] == "object":
        properties = schema.get("properties", {})
        missing = set(schema.get("required", [])) - value.keys()
        extra = value.keys() - properties.keys()
        if missing or (extra and not schema.get("additionalProperties", True)):
            raise ToolError("invalid_arguments", f"{field}: missing={sorted(missing)}, extra={sorted(extra)}")
        for key in value:
            if key in properties:
                validate(value[key], properties[key], f"{field}.{key}")
    elif schema["type"] == "integer":
        if not schema.get("minimum", value) <= value <= schema.get("maximum", value):
            raise ToolError("invalid_arguments", f"{field}: outside bounds")
    elif schema["type"] == "string":
        if not schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", len(value)):
            raise ToolError("invalid_arguments", f"{field}: invalid length")
    elif schema["type"] == "array":
        for item in value:
            validate(item, schema["items"], field + "[]")


def obj(**fields):
    return {"type": "object", "properties": fields, "required": list(fields), "additionalProperties": False}


TEXT = {"type": "string", "maxLength": 16000}
PATH = {"type": "string", "minLength": 1, "maxLength": 200}
NUMBER = {"type": "integer", "minimum": 0, "maximum": 1000000}
STOCK = {"type": "integer", "minimum": 0, "maximum": 1000}


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    output_schema: dict
    handler: Callable


class Registry:
    def __init__(self):
        self.tools = {}

    def add(self, tool):
        if tool.name in self.tools:
            raise ValueError("duplicate_tool")
        self.tools[tool.name] = tool

    def list_tools(self):
        return [{"name": t.name, "description": t.description,
                 "inputSchema": t.input_schema, "outputSchema": t.output_schema}
                for t in self.tools.values()]

    def call(self, call):
        call_id = call.get("id") if isinstance(call, dict) else None
        name = call.get("name") if isinstance(call, dict) else None
        try:
            if not isinstance(call, dict) or set(call) != {"id", "name", "arguments"}:
                raise ToolError("invalid_request", "need id, name, arguments")
            if type(call_id) is not str or not call_id or type(name) is not str:
                raise ToolError("invalid_request", "id and name must be nonempty strings")
            if name not in self.tools:
                raise ToolError("unknown_tool", "tool not registered")
            tool = self.tools[name]
            validate(call["arguments"], tool.input_schema)
            # JSON round-trip prevents handlers from mutating the caller's request.
            data = tool.handler(**json.loads(json.dumps(call["arguments"])))
            try:
                validate(data, tool.output_schema, "result")
            except ToolError as exc:
                raise ToolError("invalid_output", exc.message) from exc
            return {"call_id": call_id, "tool": name, "ok": True, "data": data, "error": None}
        except ToolError as exc:
            error = {"code": exc.code, "message": exc.message, "retryable": exc.retryable}
        except FileNotFoundError:
            error = {"code": "not_found", "message": "file does not exist", "retryable": False}
        except Exception:
            # Do not expose arbitrary exception strings (paths, secrets, provider bodies).
            error = {"code": "execution_error", "message": "handler failed", "retryable": False}
        return {"call_id": call_id, "tool": name, "ok": False, "data": None, "error": error}


def confined(root, relative):
    root = root.resolve()
    target = (root / relative).resolve()
    if Path(relative).is_absolute() or not target.is_relative_to(root):
        raise ToolError("path_denied", "relative path must remain inside tool root")
    return target


def simulate(steps, max_steps):
    history = [{"step": i, "tool": name} for i, name in enumerate(steps[:max_steps], 1)]
    return {"executed": len(history), "remaining": len(steps) - len(history),
            "completed": len(history) == len(steps), "history": history}


def execute_python(script, stdin, cwd, timeout=2, args=()):
    """Run a trusted script. -I isolates Python imports, not filesystem/network."""
    try:
        result = subprocess.run([sys.executable, "-I", str(script), *args], input=stdin,
                                cwd=cwd, env={"PYTHONIOENCODING": "utf-8"},
                                capture_output=True, text=True, encoding="utf-8",
                                timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise ToolError("timeout", "Python child exceeded deadline") from exc
    if result.returncode:
        raise ToolError("process_failed", "Python child exited nonzero")
    if len(result.stdout) > 16000:
        raise ToolError("output_too_large", "Python output exceeds limit")
    return {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr[:2000]}


def build_registry(workspace, corpus=None):
    corpus = (corpus or ROOT / "examples/corpus").resolve()
    workspace = Path(workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    registry = Registry()

    def search_docs(query, limit):
        matches = []
        for path in sorted(corpus.glob("*.md")):
            safe = confined(corpus, path.name)
            for line, text in enumerate(safe.read_text(encoding="utf-8").splitlines(), 1):
                if query.casefold() in text.casefold():
                    matches.append({"path": path.name, "line": line, "text": text})
        return {"matches": matches[:limit], "total": len(matches), "truncated": len(matches) > limit}

    def read_file(path):
        target = confined(workspace, path)
        if target.stat().st_size > 16000:
            raise ToolError("file_too_large", "file exceeds 16000 bytes")
        return {"path": path, "text": target.read_text(encoding="utf-8")}

    def write_file(path, text):
        target = confined(workspace, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return {"path": path, "bytes": len(text.encode("utf-8"))}

    def run_python(script, input_path):
        # This tool exposes only a reviewed fixture, not generated arbitrary code.
        if script not in {"compute.py", "simulate.py"}:
            raise ToolError("script_denied", "only reviewed compute.py or simulate.py is allowed locally")
        if script == "simulate.py":
            config = confined(workspace, input_path)
            output = confined(workspace, "runs/simulation")
            return execute_python(ROOT / script, "", workspace,
                                  args=("--config", str(config), "--output", "runs/simulation"))
        source = read_file(input_path)["text"]
        return execute_python(ROOT / "examples/compute.py", source, workspace)

    def simulate_loop(input_path, max_steps):
        steps = json.loads(read_file(input_path)["text"])
        if not isinstance(steps, list) or not steps or len(steps) > 100:
            raise ToolError("invalid_data", "need 1..100 tool names")
        if any(name not in {"read_file", "run_python", "write_file"} for name in steps):
            raise ToolError("invalid_data", "unknown step")
        return simulate(steps, max_steps)

    registry.add(Tool("search_docs", "在本地规则语料中逐行匹配查询词", obj(query={"type": "string", "minLength": 1, "maxLength": 100}, limit={"type": "integer", "minimum": 1, "maximum": 20}), obj(matches={"type": "array", "items": obj(path=PATH, line=NUMBER, text=TEXT)}, total=NUMBER, truncated={"type": "boolean"}), search_docs))
    registry.add(Tool("read_file", "读取本次工作目录中的小型 UTF-8 文件", obj(path=PATH), obj(path=PATH, text=TEXT), read_file))
    registry.add(Tool("write_file", "写入本次工作目录中的 UTF-8 文件", obj(path=PATH, text=TEXT), obj(path=PATH, bytes=NUMBER), write_file))
    registry.add(Tool("run_python", "执行已审阅的 compute.py 或 simulate.py，读取 JSON 输入", obj(script=PATH, input_path=PATH), obj(exit_code=NUMBER, stdout=TEXT, stderr=TEXT), run_python))
    registry.add(Tool("simulate_loop", "按步骤预算回放工具名称，不执行工具", obj(input_path=PATH, max_steps={"type": "integer", "minimum": 1, "maximum": 100}), obj(executed=NUMBER, remaining=NUMBER, completed={"type": "boolean"}, history={"type": "array", "items": obj(step=NUMBER, tool=PATH)}), simulate_loop))
    return registry
