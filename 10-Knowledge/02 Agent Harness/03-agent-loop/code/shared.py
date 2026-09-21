"""本文循环使用的消息、文件工具和固定检查。"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import shutil
import runpy
import csv
from pathlib import Path

TASK = (Path(__file__).resolve().parents[1] / "notes.txt").read_text(encoding="utf-8") + "\n本次工作区含 stats.py。先修复 mean，再用 run_python 执行 simulate.py，最后调用 check_tests 核对代码与仿真产物。"
BUGGY_SOURCE = "def mean(values):\n    return sum(values) / (len(values) + 1)\n"
FIXED_SOURCE = (
    "def mean(values):\n"
    "    if not values:\n"
    "        raise ValueError('values must not be empty')\n"
    "    return sum(values) / len(values)\n"
)


class TransientModelError(Exception):
    """仅表示本课允许有限重试的临时模型连接错误。"""


class ScriptedModel:
    """用于自动化测试的预设响应序列。"""

    def __init__(self, responses):
        self.responses = list(responses)
        self.inputs = []

    def __call__(self, messages, tools):
        self.inputs.append({"messages": copy.deepcopy(messages), "tools": copy.deepcopy(tools)})
        index = len(self.inputs) - 1
        if index >= len(self.responses):
            raise RuntimeError("脚本响应已用尽；请检查场景配置。")
        response = self.responses[index]
        if isinstance(response, Exception):
            raise response
        return copy.deepcopy(response)


def call_response(call_id, name, **arguments):
    return {"content": None, "tool_calls": [{"id": call_id, "name": name, "arguments": arguments}]}


def text_response(content):
    return {"content": content, "tool_calls": []}


def initial_messages(task=TASK):
    return [{"role": "user", "content": task}]


def add_assistant(messages, response):
    messages.append({"role": "assistant", **copy.deepcopy(response)})


def add_observation(messages, call, observation):
    messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(observation, ensure_ascii=False)})


def create_workspace(path):
    workspace = Path(path)
    workspace.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[1]
    (workspace / "notes.txt").write_text((root / "notes.txt").read_text(encoding="utf-8"), encoding="utf-8")
    (workspace / "stats.py").write_text((root / "examples" / "stats.py").read_text(encoding="utf-8"), encoding="utf-8")
    for name in ("simulate.py", "simulation.json"):
        shutil.copyfile(root / name, workspace / name)
    shutil.copyfile(root.parent / "_shared/simulation_core.py", workspace / "simulation_core.py")
    return workspace


def resolve_path(workspace, path):
    """文件工具只接受运行目录内的路径。"""
    root = Path(workspace).resolve()
    target = (root / path).resolve()
    if not target.is_relative_to(root):
        raise ValueError("文件路径不能越过实验目录。")
    return target


def read_file(workspace, path):
    return resolve_path(workspace, path).read_text(encoding="utf-8")


def write_file(workspace, path, content):
    target = resolve_path(workspace, path)
    if path != "stats.py":
        raise ValueError("本次修复只允许修改 stats.py；配置和仿真程序保持不变。")
    target.write_text(content, encoding="utf-8")
    return {"path": path, "bytes": len(content.encode("utf-8"))}


def run_python(workspace, script):
    if script != "simulate.py":
        raise ValueError("本章只执行工作区中的 simulate.py。")
    output = Path(workspace) / "runs/simulation"
    if output.exists():
        # A rerun replaces only the known simulation output, never another path.
        if output.is_symlink() or not output.resolve().is_relative_to(Path(workspace).resolve()):
            raise ValueError("仿真产物路径越界。")
        shutil.rmtree(output)
    completed = subprocess.run(
        [sys.executable, "-I", str(Path(workspace).resolve() / script),
         "--config", "simulation.json", "--output", "runs/simulation"],
        cwd=workspace, capture_output=True, text=True, encoding="utf-8", timeout=10,
        env={key: value for key, value in os.environ.items()
             if key in ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "LANG")},
    )
    return {"exit_code": completed.returncode, "stdout": completed.stdout,
            "stderr": completed.stderr, "artifacts": "runs/simulation"}


def check_simulation(workspace):
    root = Path(workspace)
    try:
        expected_config = Path(__file__).resolve().parents[1] / "simulation.json"
        if (root / "simulation.json").read_bytes() != expected_config.read_bytes():
            raise ValueError("仿真配置被修改")
        core = Path(__file__).resolve().parents[2] / "_shared/simulation_core.py"
        expected, expected_rows = runpy.run_path(str(core))["compute"](json.loads(expected_config.read_text()))
        output = root / "runs/simulation"
        actual = json.loads((output / "metrics.json").read_text())
        with (output / "samples.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        metrics_ok = all(type(actual[k]) is type(v) and
                         (abs(actual[k] - v) < 1e-10 if isinstance(v, float) else actual[k] == v)
                         for k, v in expected.items())
        samples_ok = len(rows) == len(expected_rows) and all(
            all(abs(float(a[k]) - b[k]) < 1e-10 for k in b)
            for a, b in zip(rows, expected_rows))
        hashes_ok = actual["stats_sha256"] == hashlib.sha256((root / "stats.py").read_bytes()).hexdigest()
        hashes_ok &= actual["config_sha256"] == hashlib.sha256(expected_config.read_bytes()).hexdigest()
        report = (output / "report.md").read_text(encoding="utf-8")
        report_ok = all(f"{actual[k]:.6f}" in report for k in ("input_mse", "output_mse"))
        return {"passed": bool(metrics_ok and samples_ok and hashes_ok and report_ok),
                "metrics": actual, "checks": {"metrics": metrics_ok, "samples": samples_ok,
                                                "input_versions": hashes_ok, "report": report_ok}}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {"passed": False, "error": str(exc)}


# 子进程只运行本课中展示的代码。接入真实模型时应另外配置执行隔离。
TEST_PROGRAM = r'''
import json, runpy, sys
checks = []
try:
    mean = runpy.run_path(sys.argv[1])["mean"]
    for name, values, expected in [
        ("two_values", [2, 4], 3),
        ("negative_values", [-2, 2], 0),
        ("singleton", [10], 10),
    ]:
        try:
            actual = mean(values)
            passed = isinstance(actual, (int, float)) and abs(actual - expected) < 1e-9
            checks.append({"name": name, "passed": passed, "detail": f"actual={actual!r}, expected={expected}"})
        except Exception as exc:
            checks.append({"name": name, "passed": False, "detail": type(exc).__name__ + ": " + str(exc)})
    try:
        mean([])
        checks.append({"name": "empty_raises", "passed": False, "detail": "未抛出 ValueError"})
    except ValueError:
        checks.append({"name": "empty_raises", "passed": True, "detail": "ValueError"})
    except Exception as exc:
        checks.append({"name": "empty_raises", "passed": False, "detail": type(exc).__name__})
except Exception as exc:
    checks.append({"name": "load_source", "passed": False, "detail": type(exc).__name__ + ": " + str(exc)})
print(json.dumps(checks, ensure_ascii=False))
'''


def check_tests(workspace):
    target = Path(workspace).resolve() / "stats.py"
    source = target.read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    try:
        completed = subprocess.run(
            [sys.executable, "-I", "-c", TEST_PROGRAM, str(target)],
            cwd=workspace, capture_output=True, text=True, timeout=5, check=False,
            env={key: value for key, value in os.environ.items()
                 if key in ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "LANG")},
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or "测试子进程异常退出")
        checks = json.loads(completed.stdout)
    except (subprocess.TimeoutExpired, RuntimeError, json.JSONDecodeError) as exc:
        checks = [{"name": "test_process", "passed": False, "detail": type(exc).__name__ + ": " + str(exc)}]
    simulation = check_simulation(workspace)
    checks.append({"name": "simulation_artifacts", "passed": simulation["passed"],
                   "detail": json.dumps(simulation, ensure_ascii=False)})
    return {"passed": bool(checks) and all(check["passed"] for check in checks), "checks": checks,
            "source_sha256": digest, "simulation": simulation}


def make_registry(workspace):
    """用小字典保持工具说明、参数规则、执行函数的一一对应。"""
    return {
        "read_file": {"description": "读取实验目录内的文本文件", "parameters": {"path": str}, "function": lambda path: read_file(workspace, path)},
        "write_file": {"description": "修改本次工作区的 stats.py，修复均值函数", "parameters": {"path": str, "content": str}, "function": lambda path, content: write_file(workspace, path, content)},
        "run_python": {"description": "运行 simulate.py，返回退出码、标准输出和错误；产物保存在 runs/simulation", "parameters": {"script": str}, "function": lambda script: run_python(workspace, script)},
        "check_tests": {"description": "检查 mean 函数、仿真指标、波形数据和报告是否符合要求", "parameters": {}, "function": lambda: check_tests(workspace)},
        "finish": {"description": "明确请求结束当前运行；不代表验收通过", "parameters": {"summary": str}, "function": None},
    }


def tool_definitions(registry):
    """只传描述和 JSON Schema 给模型，不传 Python 函数对象。"""
    return [
        {"name": name, "description": spec["description"], "parameters": {
            "type": "object", "properties": {key: {"type": "string"} for key in spec["parameters"]},
            "required": list(spec["parameters"]), "additionalProperties": False,
        }}
        for name, spec in registry.items()
    ]


def validate_arguments(name, arguments, registry):
    if name not in registry:
        raise ValueError(f"未知工具：{name}")
    expected = registry[name]["parameters"]
    if not isinstance(arguments, dict):
        raise ValueError("arguments 必须是字典。")
    if set(arguments) != set(expected):
        raise ValueError(f"{name} 需要参数 {list(expected)}，实际收到 {list(arguments)}")
    for key, kind in expected.items():
        if not isinstance(arguments[key], kind):
            raise ValueError(f"参数 {key} 必须是 {kind.__name__}")


def execute_tool(name, arguments, registry):
    validate_arguments(name, arguments, registry)
    function = registry[name]["function"]
    if function is None:
        raise ValueError("finish 必须由控制器处理。")
    return {"ok": True, "output": function(**arguments)}


def error_observation(exc):
    return {"ok": False, "error": {"type": type(exc).__name__, "message": str(exc)}}


def validate_response(response):
    if not isinstance(response, dict) or not isinstance(response.get("tool_calls"), list):
        raise ValueError("response 必须包含 tool_calls 列表。")
    if response.get("content") is not None and not isinstance(response["content"], str):
        raise ValueError("content 必须是字符串或 None。")
    for call in response["tool_calls"]:
        if not isinstance(call, dict) or not all(key in call for key in ("id", "name", "arguments")):
            raise ValueError("工具请求缺少 id、name 或 arguments。")
        if not isinstance(call["id"], str) or not call["id"]:
            raise ValueError("工具调用 id 必须是非空字符串。")
        if not isinstance(call["name"], str):
            raise ValueError("工具名称必须是字符串。")


def make_result(status, reason, model_calls, messages, trace):
    return {"status": status, "reason": reason, "model_calls": model_calls, "messages": messages, "trace": trace}
