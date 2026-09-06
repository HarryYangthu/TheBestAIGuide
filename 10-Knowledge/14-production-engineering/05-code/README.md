# 容量与故障算例

> 状态：verified · 更新：2026-09-06

[production_checks.py](production_checks.py)只用 Python 3.12 标准库：

```bash
python 10-Knowledge/14-production-engineering/05-code/production_checks.py
```

2026-09-06 实跑并通过内置断言。教学输入下服务能力约 1.333 次/秒，小于到达 2 次/秒；99% SLO、10000 任务、70 次失败剩 30 次预算；外部写入后中断的朴素恢复创建 2 条记录，按动作 ID 去重创建 1 条；单位成功任务成本分别 .4 与 .3333。

所有成本和流量为假设；去重使用单线程列表，不代表数据库原子事务。没有真实负载、线上服务或网络故障注入。真实浏览器中断实验在[相邻应用工程](../../13-application-engineering/05-code/browser-agent-typescript/README.md)。返回[生产概念](../README.md)。
