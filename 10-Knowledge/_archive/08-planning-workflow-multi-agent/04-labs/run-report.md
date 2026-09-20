# 协作实验运行记录

> 状态：verified（本地 fixture）；日期：2026-09-06。

运行环境：CPython 3.12；代码要求 Python 3.11+，仅标准库。单元测试命令在工程目录执行：

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

6 项 unittest 通过，覆盖合法路由与单/并发基线、超时部分结果、错误契约与输入隔离、父任务取消、总任务预算拒绝、不同结果冲突。

[Notebook](01-single-vs-multi-agent.ipynb)的 5 个代码单元真实执行并保存输出。三个模式均选择 A；顺序/并行最大活跃 Worker 为 1/2；本次耗时分别约 40.8/20.4 ms，使用 20 ms 人工等待模拟独立 I/O。不要将该耗时解释为真实模型收益。精确事件见 [experiment.json](artifacts/experiment.json)。

执行后端是独立 Python 进程内 IPython 顺序执行，因环境禁止 Kernel socket 而未使用 Jupyter kernel。尚未验证真实 LLM、分布式队列、不可信代码隔离或不合作的取消。
