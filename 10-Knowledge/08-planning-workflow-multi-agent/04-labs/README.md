# 协作实验

> 状态：verified（仅本地确定性 fixture 与异步调度）；执行日期：2026-09-06。

打开 [01-single-vs-multi-agent.ipynb](01-single-vs-multi-agent.ipynb)，从上到下运行。Python 3.11+；Notebook 前端需 Jupyter 和 ipykernel，项目运行代码本身只用标准库。

实验展示输入表、三个基线结果、实际事件序列、部分超时和冲突。教学 Worker 的等待用于模拟 I/O；没有调用大模型，没有真实硬件测量，不用该结果宣称多 Agent 质量提升。实跑证据保存在 [artifacts/experiment.json](artifacts/experiment.json)。

先读[案例](../03-cases/01-single-vs-multi-agent.md)，不想使用 Jupyter 则按[工程说明](../05-code/multi-agent-runtime-python/README.md)运行同一实验。返回[本域导航](../README.md)。

本次保存的输出由独立 Python 进程中的 IPython 顺序执行得到。环境禁止 Kernel socket，因此没有使用 Jupyter kernel；Notebook 元数据明确记录 `execution_backend`，错误会使执行失败。

[本次运行记录](run-report.md)列出命令、实际结果与未验证范围。
