# 多 Worker 运行时（Python）

> 状态：verified（本地调度、契约、冲突及取消测试）；执行日期：2026-09-06。

Python 3.11+，无第三方运行依赖。进入本目录后运行：

```bash
PYTHONPATH=src python -m multi_agent.fixture
PYTHONPATH=src python -m unittest discover -s tests -v
```

Windows PowerShell 使用 `$env:PYTHONPATH="src"`，然后分别执行上述 `python` 命令。也可先 `python -m pip install -e . --no-build-isolation`，构建环境需已有 setuptools>=68。

| 文件 | 负责的机制 |
|---|---|
| [contracts.py](src/multi_agent/contracts.py) | Task 输入与 WorkerResult 返回契约 |
| [router.py](src/multi_agent/router.py) | 任务类型到 Worker 的明确映射 |
| [supervisor.py](src/multi_agent/supervisor.py) | 总任务预算、并发名额、总期限、父子取消 |
| [merge.py](src/multi_agent/merge.py) | 部分结果、字段来源和冲突拒绝 |
| [fixture.py](src/multi_agent/fixture.py) | 可替换的教学 Worker、确定性与顺序/并行基线 |
| [tests](tests/test_runtime.py) | 7 项用例，涵盖未知路由、契约错、隔离、超时、取消、冲突、预算与完整任务清单 |

使用 `merge_results(results, expected_task_ids=[...])` 合并时，清单必须来自实际委派任务；缺失结果会令 `complete=False`，重复/未知结果会被拒绝。省略清单只能检查已传入结果，不能发现调用方遗漏的任务。

公开入口：`Task`、`WorkerResult`、`Router`、`Supervisor`、`merge_results`、`MergeConflict`。`await Supervisor(router).run(tasks)` 返回 `RunResult(results, trace, max_active)`。每次 run 内部状态独立；`last_trace` 是调试便捷入口，同一个 Supervisor 并发多次调用时不应用它区分任务。

本实现没有模型 SDK、持久化队列或跨进程沙箱。输入深拷贝不是安全隔离；取消依赖 Worker 配合。真实 Agent 可包成 `async def worker(task) -> dict`，对外保持相同契约。先看[交接正文](../../02-patterns/01-task-contract-and-handoff.md)与[实验](../../04-labs/01-single-vs-multi-agent.ipynb)，返回[本域导航](../../README.md)。
