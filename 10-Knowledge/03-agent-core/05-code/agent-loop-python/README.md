# 最小 Python Agent Loop

> 状态：verified | 验证：2026-09-06，Python 3.12，9项单元测试通过

输入查询“上下文”，离线规则策略调用只读搜索，取得教学文档，再返回带ID的文字。Python 3.11+，运行无需第三方包。

从本目录运行：

```bash
PYTHONPATH=src python -m agent_loop.cli 上下文
PYTHONPATH=src python -m unittest discover -s tests -v
```

PowerShell：先执行 `$env:PYTHONPATH="src"`，再执行上述`python`命令。也可 `python -m pip install -e .` 安装后正常import；打包工具需已安装或可联网取得。

| 文件 | 看什么 |
| --- | --- |
| [models.py](src/agent_loop/models.py) | Action、State、模型接口与两种离线策略 |
| [loop.py](src/agent_loop/loop.py) | 动作检查、调用、观察更新、预算和重复停止 |
| [tools.py](src/agent_loop/tools.py) | 只读中文子串检索教学语料 |
| [trace.py](src/agent_loop/trace.py) | 按事件写JSONL；使用新文件防覆盖 |
| [test_loop.py](tests/test_loop.py) | 成功、非法动作、工具错误、重复、预算、权限、状态隔离、非法JSON输出与历史观察防篡改 |

公开入口：`run_agent(model, tools, task, *, max_steps=8, repeat_limit=2, trace_path=None) -> AgentState`。`model.decide(state)`返回`Action`；`tools`是名称到`Tool(handler, allowed=True)`的映射。`--trace new-run.jsonl`写新文件，已存在则报错。Trace在结束时写出，不提供崩溃恢复。

本实现不执行外部命令、不接真实模型、不提供硬超时或沙箱；Python进程内的handler须可信。`completed`仅表示合法结束，需要另行评分。扩展前先读[Loop文章](../../01-concepts/02-agent-loop.md)和[实验](../../04-labs/01-agent-loop.ipynb)。
