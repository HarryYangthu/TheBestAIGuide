# 恢复与幂等实验

> 状态：verified（本地 SQLite 模拟服务）；执行日期：2026-09-06。

[01-recovery-and-idempotency.ipynb](01-recovery-and-idempotency.ipynb)先演示重复动作的风险，再对三个崩溃位置逐一恢复，最后验证无副作用回放与退款补偿。Notebook 使用临时目录，保存执行输出，并将结构化证据写入 [artifacts/recovery.json](artifacts/recovery.json)。

Python 3.11+，代码只用标准库；Notebook 前端需要 Jupyter / ipykernel。所有金额为教学整数计数，无真实支付与外部连接。模拟异常覆盖逻辑提交窗口，不模拟断电造成文件系统损坏。

[原理](../01-concepts/02-durable-execution.md) · [代码和测试命令](../05-code/recoverable-runtime-python/README.md) · [本域导航](../README.md)

本次保存的输出由独立 Python 进程中的 IPython 顺序执行得到。环境禁止 Kernel socket，因此没有使用 Jupyter kernel；Notebook 元数据明确记录 `execution_backend`，错误会使执行失败。

[本次运行记录](run-report.md)列出命令、实际结果与未验证范围。

## 标准内核验证更新（2026-09-06）

提交 `5e5a40c09e00028c7887fd3bf3bd559d96fc972f` 的 [GitHub Actions 标准 Jupyter 执行](https://github.com/HarryYangthu/TheBestAIGuide/actions/runs/34013521515)已成功。原 Notebook 保存输出的本地 IPython 来源保留；这条更新补充标准内核证据，不代表交互控件或所有前端已验收。本轮新项目与后续结果见仓库 `00-Home/Round2-Completion.md`。
