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

[来源索引](references.md)固定 DPO、PPO、GRPO 等原论文版本。[代码说明](05-code/README.md)包含运行方法与结果。Notebook 的 CPU 计算已实际运行，但本库没有进行语言模型 SFT、DPO 或 RL 训练；文章保持 draft 等待内容终审。

## 配套项目扩展（2026-09-06）

[真实 SFT/LoRA/DPO 更新与正负优势 clipping](../../20-Projects/tiny-transformer/README.md)已提供源码、输入数据、运行入口和实际结果。默认机制验证与可选真实模型结果分开记录，具体适用范围见项目说明。
