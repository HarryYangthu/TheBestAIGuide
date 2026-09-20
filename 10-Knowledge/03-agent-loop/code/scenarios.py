"""可复现离线场景：脚本预设下一步，文件和测试仍真实执行。

不能把这些输出当作任何真实大模型的性能或纠错能力。
"""
import tempfile
from shared import (BUGGY_SOURCE, FIXED_SOURCE, ScriptedModel, TransientModelError,
                    call_response, check_tests, create_workspace, text_response)
from v4_resilient_loop import run_loop

CASE_NAMES = ("normal", "bad_tool", "early_finish", "step_limit", "empty_response",
              "duplicate_id", "stale_test", "failing_test", "transient_model")


def normal_responses():
    return [
        call_response("c1", "read_file", path="stats.py"),
        call_response("c2", "write_file", path="stats.py", content=FIXED_SOURCE),
        call_response("c3", "check_tests"),
        call_response("c4", "finish", summary="已修复并测试。"),
    ]


def responses_for(name):
    if name in ("normal", "step_limit"):
        return normal_responses()
    if name == "bad_tool":
        return [call_response("bad0", "read_flie", path="stats.py")] + normal_responses()
    if name == "early_finish":
        return [call_response("c1", "finish", summary="问题已解决。")]
    if name == "empty_response":
        return [text_response(""), text_response(None)]
    if name == "duplicate_id":
        return [call_response("c1", "read_file", path="stats.py"),
                call_response("c1", "write_file", path="stats.py", content=FIXED_SOURCE)]
    if name == "stale_test":
        return normal_responses()[:3] + [
            call_response("c4", "write_file", path="stats.py", content=BUGGY_SOURCE),
            call_response("c5", "finish", summary="刚才测试已通过。"),
        ]
    if name == "failing_test":
        return [call_response("c1", "read_file", path="stats.py"),
                call_response("c2", "check_tests"),
                call_response("c3", "finish", summary="测试工具已经执行。")]
    if name == "transient_model":
        return [TransientModelError("离线注入：模型连接临时中断")] + normal_responses()
    raise ValueError(f"未知场景 {name!r}；可选：{', '.join(CASE_NAMES)}")


def run_case(name, max_steps=None):
    model = ScriptedModel(responses_for(name))
    limit = (2 if name == "step_limit" else 12) if max_steps is None else max_steps
    with tempfile.TemporaryDirectory(prefix="agent-loop-case-") as path:
        workspace = create_workspace(path)
        result = run_loop(model, workspace, max_steps=limit)
        # 在最终文件上重新执行检查，独立于模型的口头声明和之前的工具输出。
        result["acceptance"] = check_tests(workspace)
        result["artifact_source"] = (workspace / "stats.py").read_text(encoding="utf-8")
    result["case"] = name
    result["fixture_mode"] = "offline_scripted"
    result["model_inputs"] = model.inputs
    return result
