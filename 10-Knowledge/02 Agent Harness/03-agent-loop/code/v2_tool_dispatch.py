"""阶段 2：增加工具注册、参数校验和调用编号；错误暂时直接抛出。"""
from shared import (add_assistant, add_observation, execute_tool, initial_messages,
                    make_registry, make_result, tool_definitions, validate_response)


def run_loop(model, workspace, max_steps=12):
    registry = make_registry(workspace)
    del registry["finish"]                    # 阶段 3 才引入显式结束工具
    messages, trace, seen_ids = initial_messages(), [], set()
    for model_calls in range(1, max_steps + 1):
        response = model(messages, tool_definitions(registry))
        validate_response(response)
        ids = [call["id"] for call in response["tool_calls"]]
        if len(ids) != len(set(ids)) or seen_ids.intersection(ids):
            raise ValueError("工具调用编号重复。")
        seen_ids.update(ids)
        add_assistant(messages, response)
        trace.append({"event": "model_response", "model_call": model_calls, "response": response})
        if not response["tool_calls"]:
            return make_result("stopped", "no_tool_calls", model_calls, messages, trace)
        for call in response["tool_calls"]:
            observation = execute_tool(call["name"], call["arguments"], registry)
            add_observation(messages, call, observation)
            trace.append({"event": "tool_result", "model_call": model_calls, "call_id": call["id"], "name": call["name"], "observation": observation})
    return make_result("stopped", "step_limit", max_steps, messages, trace)


def main():
    from live_run import cli
    cli("v2")


if __name__ == "__main__":
    main()
