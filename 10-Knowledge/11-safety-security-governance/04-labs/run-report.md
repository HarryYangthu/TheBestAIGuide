# 策略实验运行记录

> 状态：verified（本地授权正反例）；日期：2026-09-06。

运行环境：CPython 3.12；代码要求 Python 3.11+，仅标准库。在 05-code 目录运行：

```bash
python -m unittest -v test_policy.py
```

5 项 unittest 通过，包括六条普通/恶意动作候选、合法批准删除、令牌跨用户/Run/对象拒绝、scope 与过期检查、secret 字段投影。

[Notebook](01-policy-and-injection.ipynb)的 4 个代码单元真实执行并保存输出。普通读取和引用恶意语句的正常读取均成功（2/2）；四条越权动作均拒绝（4/4）；批准后删除 a2 成功，换对象删除 a1 与令牌复用被拒绝。最终 a1、b1 保留，审计不含教学 secret 或审批令牌。证据见 [policy.json](artifacts/policy.json)。

执行后端是独立 Python 进程内 IPython 顺序执行，环境禁止 Kernel socket。本实验不运行模型，因此没有测量模型的真实抗注入成功率；也没有实现认证服务、持久审计、外部网络或生产删除。
