# Agent Learning：一手来源与证据边界

> 状态：draft · 更新：2026-09-06

检索核验日期：2026-09-06。已打开下列作者论文页面核对标题、版本与方法范围。此记录是来源核验，不是论文结果复现或人工终审。

| 来源 | 固定版本/日期 | 本域使用的证据 | 不能据此推出 |
|---|---|---|---|
| [Direct Preference Optimization](https://arxiv.org/abs/2305.18290v3) | v3，2024-07-29 | 偏好对、参考策略与 DPO 目标 | 任意工具任务一定优于 SFT |
| [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347v2) | v2，2017-08-28 | 策略概率比和裁剪目标 | 本库已运行 PPO 训练 |
| [DeepSeekMath](https://arxiv.org/abs/2402.03300v3) | v3，2024-04-27 | GRPO 与组内相对奖励思想 | 通用 Agent 任务具有同样收益 |
| [Let's Verify Step by Step](https://arxiv.org/abs/2305.20050v1) | v1，2023-05-31 | 数学任务过程/结果监督比较 | 过程奖励对所有任务都更好 |
| [SWE-agent](https://arxiv.org/abs/2405.15793v1) | v1，2024-05-06 | 代码执行接口与任务轨迹背景 | 本地价格函数等于 SWE-bench 复现 |

轨迹 Schema、失败定位表和奖励反例为本库教学设计。数值实验的实现、输入和输出在[Notebook](04-labs/01-trajectories-and-rewards.ipynb)与[源码说明](05-code/README.md)。真实训练应进一步按所用框架版本核对损失归一化、采样和 KL 实现，不能仅凭本文公式认定两个训练器行为一致。
