# 仿真任务报告

任务：执行一次 Python 信号去噪仿真，并根据实际结果生成报告。
执行：python simulate.py --config simulation.json --output runs/simulation
输入：64 个采样点，2 个正弦周期，交替噪声幅度 0.3，均值滤波窗口 3。
检查：核对进程退出码和输出 MSE；若存在 stats.py，核对 mean 的除数和空列表处理。
产物：runs/simulation/metrics.json、runs/simulation/samples.csv、runs/simulation/report.md
要求：保留原始配置；报告引用真实指标，运行失败时记录原因，不编造成功。

样本数：64；输入 MSE：0.090000；输出 MSE：0.010082。

| 步骤预算 | 已执行 | 剩余 | 完成 |
|---:|---:|---:|---|
| 2 | 2 | 1 | False |
| 3 | 3 | 0 | True |

规则：glossary.md:3、policy.md:1、policy.md:3、policy.md:4。
