# 01：模型怎样通过一个循环做事

先运行 README 的 stage 1 命令，再打开 `trace.jsonl`。一次完整动作包含模型请求、模型返回的工具调用、Python 工具结果。模型没有直接打开硬盘文件：它输出 `read_file` 与 JSON 参数，宿主找到对应函数并执行。

打开 [runtime.py](../mini_agent/runtime.py) 的 `run`，沿着 `provider.respond → messages.append → box.call → messages.append` 阅读。循环不是预先把“查目录、读两份文件、写报告”写死；live 模式下下一步来自模型。demo 驱动器单独放在 [providers.py](../mini_agent/providers.py)，其中预设动作只用于复现教学结果。

```python
message, usage = provider.respond(request, schemas(stage))
messages.append(message)  # 必须保存模型发出的调用，不能只保存工具结果
for call in message.get("tool_calls") or []:
    result = box.call(call["function"]["name"], json.loads(call["function"]["arguments"]))
    messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result)})
```

上面是从主循环提取的数据流片段，完整错误处理看源码。`tool_call_id` 把结果与对应请求连起来；一轮可能有多个调用，必须逐个返回。最后一轮没有工具调用，表示模型请求结束，但宿主还要验收产物。

打开 `messages.json`，找到 `read_file` 的模型消息与紧随其后的工具消息，再找到写报告的调用。stage 1 的 demo 应有 4 次工具调用、5 次模型调用：查目录、读 v1、读 v2、写报告，最后返回结束消息。

**练习：** 用真实模型把任务改为“只列出资料文件名”。预期模型可以正常结束，但现有升级清单验收应 FAIL，因为它没有完成本项目规定的升级任务。尝试自行说明“执行正常”为什么不等于“验收通过”。没有模型时，对照测试中的 `test_early_model_finish_does_not_pass` 观察同一个现象。

关联知识：[Agent Core](../../../10-Knowledge/03-agent-core/README.md)。
