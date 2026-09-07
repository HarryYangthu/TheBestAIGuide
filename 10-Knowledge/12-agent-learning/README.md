# Agent Learning：从可靠轨迹到可验证改进

> 状态：draft · 更新：2026-09-06

本域回答：一条执行记录能不能用于训练、应该优化哪个目标、怎样避免模型只学会刷分。先把数据与验收做对，再选择微调或强化学习。

| 阅读顺序 | 学完应能做什么 | 实现/实验 |
|---|---|---|
| [轨迹数据](01-concepts/01-trajectory-data.md) | 区分观察、动作、验收，阻止组泄露 | [learning.py](05-code/learning.py) |
| [SFT 与偏好优化](01-concepts/02-sft-and-preference-optimization.md) | 解释掩码和 DPO 损失 | [损失与奖励 Notebook](04-labs/01-trajectories-and-rewards.ipynb) |
| [Agentic RL](01-concepts/03-agentic-reinforcement-learning.md) | 理解 PPO/GRPO、优势和信用分配 | [组内优势函数](05-code/learning.py) |
| [验证器与奖励投机](01-concepts/04-verifiers-and-reward-hacking.md) | 构造伪造成功、越权成功反例 | [测试](05-code/test_learning.py) |
| [评分到改进](02-patterns/01-feedback-to-improvement.md) | 按故障证据选择改动层 | [浏览器恢复案例](../13-application-engineering/03-cases/browser-agents/README.md) |

[来源索引](references.md)固定 DPO、PPO、GRPO 等原论文版本。[代码说明](05-code/README.md)包含运行方法与结果。本域 Notebook 用手填概率解释 loss；配套 Tiny Transformer 用真实小模型执行 SFT/LoRA/DPO，并演示一次两动作策略更新。这两个实践层次各有用途，均不能代替独立任务上的能力评测；文章保持 draft 等待人工终审。

## 从算清损失到更新参数

先跑本域 Notebook，回答“哪些位置计 loss、参考模型为什么固定、全失败组优势是多少”；再运行 [Tiny Transformer](../../20-Projects/tiny-transformer/README.md)，对照 [experiment.py](../../20-Projects/tiny-transformer/src/tiny_transformer/experiment.py) 找到 `backward`、优化器与冻结参数。先验算，再看真实更新，能避免把手动改小 loss 的数值例子误当成训练。
