"""阶段 1：先手动调用两次，再写循环。只提供 read_file。"""
from shared import (add_assistant, add_observation, initial_messages, read_file)

TOOLS = [{"name": "read_file", "description": "读取实验目录内的文本文件", "parameters": {
    "type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}]
TASK = "请读取 notes.txt，并告诉我本周完成了什么。"


def run_manual(model, workspace):
    messages = initial_messages(TASK)
    response = model(messages, TOOLS)          # 第一次：模型提出读文件请求
    add_assistant(messages, response)
    if len(response["tool_calls"]) != 1 or response["tool_calls"][0]["name"] != "read_file":
        raise ValueError("手动示例第一轮需要一个 read_file 请求；请查看 responses.jsonl。")
    call = response["tool_calls"][0]
    observation = read_file(workspace, call["arguments"]["path"])
    add_observation(messages, call, observation)
    response = model(messages, TOOLS)          # 第二次：输入里已有真实文件内容
    add_assistant(messages, response)
    if response["tool_calls"]:
        raise ValueError("第二轮仍有工具请求，请运行自动循环版本继续处理。")
    return messages


def run_loop(model, workspace, max_steps=10):
    messages = initial_messages(TASK)
    for _ in range(max_steps):                # 上限仅用于避免示例意外无限运行
        response = model(messages, TOOLS)
        add_assistant(messages, response)
        if not response["tool_calls"]:         # 本阶段简化规则；空响应问题留到后面
            return messages
        for call in response["tool_calls"]:
            if call["name"] != "read_file":
                raise ValueError("阶段 1 只支持 read_file。")
            observation = read_file(workspace, call["arguments"]["path"])
            add_observation(messages, call, observation)
    raise RuntimeError("最小示例达到调用上限。")


def main():
    from live_run import cli
    cli("v1")


if __name__ == "__main__":
    main()
