"""阶段 4：错误反馈、空响应上限、编号冲突与有限的模型请求重试。

本章的 max_steps 精确定义为模型请求尝试次数：失败请求和重试也计数。
没有实现工具重试、进程恢复、费用预算或运行截止时间。
"""
import copy
import json
from shared import (TransientModelError, add_assistant, add_observation,
                    error_observation, execute_tool, initial_messages, make_registry,
                    make_result, tool_definitions, validate_arguments, validate_response)


def run_loop(model, workspace, max_steps=12, max_model_retries=2, max_empty_responses=2):
    if max_steps < 1 or max_model_retries < 0 or max_empty_responses < 1:
        raise ValueError("要求 max_steps>=1、max_model_retries>=0、max_empty_responses>=1。")
    registry = make_registry(workspace)
    messages, trace, seen_ids = initial_messages(), [], set()
    empty_count, retry_count = 0, 0

    for model_calls in range(1, max_steps + 1):
        trace.append({"event": "model_call", "model_call": model_calls, "messages": copy.deepcopy(messages)})
        try:
            response = model(messages, tool_definitions(registry))
        except TransientModelError as exc:
            retry_count += 1
            trace.append({"event": "model_error", "model_call": model_calls, "error": str(exc), "consecutive_failures": retry_count})
            if retry_count > max_model_retries:
                return make_result("failed", "model_retry_limit", model_calls, messages, trace)
            continue                         # 下一轮重试；消息历史没有伪造的工具结果
        except Exception as exc:
            trace.append({"event": "model_error", "model_call": model_calls, "error": type(exc).__name__ + ": " + str(exc)})
            return make_result("failed", "model_error", model_calls, messages, trace)

        retry_count = 0
        trace.append({"event": "model_response", "model_call": model_calls, "response": copy.deepcopy(response)})
        try:
            validate_response(response)
        except ValueError as exc:
            trace.append({"event": "protocol_error", "model_call": model_calls, "error": str(exc)})
            return make_result("failed", "invalid_response", model_calls, messages, trace)

        calls = response["tool_calls"]
        ids = [call["id"] for call in calls]
        if len(ids) != len(set(ids)) or seen_ids.intersection(ids):
            # 整批先检查，因此不会执行前半批后才发现后半批编号冲突。
            trace.append({"event": "protocol_error", "model_call": model_calls, "error": "duplicate_call_id", "call_ids": ids})
            return make_result("failed", "duplicate_call_id", model_calls, messages, trace)
        if any(call["name"] == "finish" for call in calls) and len(calls) != 1:
            trace.append({"event": "protocol_error", "model_call": model_calls, "error": "finish_must_be_alone"})
            return make_result("failed", "finish_must_be_alone", model_calls, messages, trace)

        seen_ids.update(ids)
        add_assistant(messages, response)
        if not calls:
            if not (response.get("content") or "").strip():
                empty_count += 1
                trace.append({"event": "empty_response", "model_call": model_calls, "consecutive_empty": empty_count})
                if empty_count >= max_empty_responses:
                    return make_result("failed", "empty_response_limit", model_calls, messages, trace)
            else:
                empty_count = 0
            messages.append({"role": "user", "content": "请继续执行任务，完成后单独调用 finish。"})
            continue

        empty_count = 0
        for call in calls:
            try:
                validate_arguments(call["name"], call["arguments"], registry)
                if call["name"] == "finish":
                    observation = {"ok": True, "output": {"stop_requested": True}}
                    add_observation(messages, call, observation)
                    trace.append({"event": "tool_result", "model_call": model_calls, "call_id": call["id"], "name": "finish", "observation": observation})
                    return make_result("stopped", "finish", model_calls, messages, trace)
                observation = execute_tool(call["name"], call["arguments"], registry)
            except (ValueError, OSError) as exc:
                # 未知工具、参数错误、文件错误可作为反馈；不自动重放工具。
                observation = error_observation(exc)
            except Exception as exc:
                observation = error_observation(exc)
                add_observation(messages, call, observation)
                trace.append({"event": "tool_result", "model_call": model_calls, "call_id": call["id"], "name": call["name"], "observation": observation})
                return make_result("failed", "tool_error", model_calls, messages, trace)
            add_observation(messages, call, observation)
            trace.append({"event": "tool_result", "model_call": model_calls, "call_id": call["id"], "name": call["name"], "observation": observation})

    return make_result("stopped", "step_limit", max_steps, messages, trace)


if __name__ == "__main__":
    from live_run import cli
    cli("v4")
