# 恢复实验运行记录

> 状态：verified（本地 SQLite 故障窗口）；日期：2026-09-06。

运行环境：CPython 3.12；代码要求 Python 3.11+，仅标准库。单元测试命令在工程目录执行：

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

6 项 unittest 通过，覆盖动作前/后/Checkpoint 后崩溃恢复、同 key 改参数拒绝、纯回放不变更账本、退款后崩溃再补偿、pending 先对账、组合步骤键无歧义。

[Notebook](01-recovery-and-idempotency.ipynb)的 4 个代码单元真实执行并保存输出：三种崩溃条件最终各产生 1 条扣款；总计 3 条、金额 30；两次回放账本无变化；补偿后再补偿仅 1 条退款，金额 10，最终净值 20。精确 trace 见 [recovery.json](artifacts/recovery.json)。

执行后端是独立 Python 进程内 IPython 顺序执行，环境禁止 Kernel socket。模拟异常不等于物理断电测试；单写者示例不具备分布式租约，真实外部服务必须支持查询或原子幂等才能复制相应保证。
