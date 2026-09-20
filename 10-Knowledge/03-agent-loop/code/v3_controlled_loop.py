"""阶段 3：显式 finish、调用次数预算、运行后独立验收；错误暂时抛出。"""
from shared import (add_assistant, add_observation, execute_tool, initial_messages,
                    make_registry, make_result, tool_definitions,
                    validate_arguments, validate_response)


def run_loop(model, workspace, max_steps=12):
    if max_steps < 1:
        raise ValueError("max_steps 必须至少为 1。")
    registry = make_registry(workspace)
    messages, trace, seen_ids = initial_messages(), [], set()
    for model_calls in range(1, max_steps + 1):
        response = model(messages, tool_definitions(registry))
        validate_response(response)
        ids = [call["id"] for call in response["tool_calls"]]
        if len(ids) != len(set(ids)) or seen_ids.intersection(ids):
            raise ValueError("工具调用编号重复。")
        if any(call["name"] == "finish" for call in response["tool_calls"]) and len(ids) != 1:
            raise ValueError("finish 必须单独调用，避免遗漏同轮其他动作。")
        seen_ids.update(ids)
        add_assistant(messages, response)
        trace.append({"event": "model_response", "model_call": model_calls, "response": response})
        if not response["tool_calls"]:
            messages.append({"role": "user", "content": "请继续执行任务，完成后单独调用 finish。"})
            continue
        for call in response["tool_calls"]:
            validate_arguments(call["name"], call["arguments"], registry)
            if call["name"] == "finish":
                observation = {"ok": True, "output": {"stop_requested": True}}
                add_observation(messages, call, observation)
                trace.append({"event": "tool_result", "model_call": model_calls, "call_id": call["id"], "name": "finish", "observation": observation})
                return make_result("stopped", "finish", model_calls, messages, trace)
            observation = execute_tool(call["name"], call["arguments"], registry)
            add_observation(messages, call, observation)
            trace.append({"event": "tool_result", "model_call": model_calls, "call_id": call["id"], "name": call["name"], "observation": observation})
    return make_result("stopped", "step_limit", max_steps, messages, trace)


def main():
    from live_run import cli
    cli("v3")


if __name__ == "__main__":
    main()
