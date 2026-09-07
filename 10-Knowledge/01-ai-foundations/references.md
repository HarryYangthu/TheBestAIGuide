# AI 基础：来源与核验范围

> 状态：draft · 核验日期：2026-09-06

以下是本域使用的一手教材、论文与官方文档。已通过网页读取或检索定位对应内容；这表示出处核验，不表示人工学术审稿。数学推导、数据、代码和小例子为本库原创教学材料，不是原论文实验复现。动态文档记录核验日快照，不声称其版本与本地安装版本相同。

| 编号 | 来源与版本 | 支持的内容 | 本次核验与边界 |
|---|---|---|---|
| F1 | Goodfellow、Bengio、Courville，[Deep Learning 第2章](https://www.deeplearningbook.org/contents/linear_algebra.html)，2016在线教材 | 向量、矩阵、张量、矩阵乘法与线性系统 | 读取章节；本库的二维例子独立构造 |
| F2 | 同书[第3章 Probability and Information Theory](https://www.deeplearningbook.org/contents/prob.html)，2016 | 概率、期望、方差、熵与KL | 读取章节；告警后验例子的参数为教学假设 |
| F3 | 同书[第4章 Numerical Computation](https://www.deeplearningbook.org/contents/numerical.html)，2016 | 数值稳定性、梯度与二次优化 | 读取章节；学习率界与有限差分在本地独立验证 |
| F4 | 同书[第8章 Optimization](https://www.deeplearningbook.org/contents/optimization.html)，2016 | 训练目标与泛化目标、批次优化、优化算法 | 读取章节；不把训练损失当测试性能 |
| F5 | [scikit-learn Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html)，核验日页面标1.9.0 | 训练/测试分离、预处理泄漏与Pipeline的用途 | 读取官方文档；本地教学代码使用NumPy，不依赖此版本sklearn |
| F6 | [PyTorch Autograd mechanics](https://docs.pytorch.org/docs/2.8/notes/autograd.html)，2.8 文档（2026-09-07 对齐项目依赖复核） | 计算图、反向微分与梯度行为 | 读取官方文档；本域实验运行自写标量引擎；另有 [tiny-transformer](../../20-Projects/tiny-transformer/README.md) 的 PyTorch 2.8.0 CPU 训练，两个实现范围分开记录 |
| F7 | Berkeley CS188，[State Spaces](https://inst.eecs.berkeley.edu/~cs188/textbook/search/state.html)与[Informed Search](https://inst.eecs.berkeley.edu/~cs188/textbook/search/informed.html)，核验日网页 | 状态空间、A*、可采纳与一致性条件 | 检索定位正文；本库有限图和可重开实现独立编写 |
| F8 | Berkeley CS188，[Monte Carlo Tree Search](https://inst.eecs.berkeley.edu/~cs188/textbook/games/monte-carlo.html)，核验日网页 | 选择、扩展、模拟与回传的搜索过程 | 读取章节；本域未提供完整MCTS实现 |
| F9 | Berkeley CS188，[MDP](https://inst.eecs.berkeley.edu/~cs188/textbook/mdp/markov-decision-processes.html)与[Value Iteration](https://inst.eecs.berkeley.edu/~cs188/textbook/mdp/value-iteration.html)，核验日网页 | Markov状态、Bellman分解与价值迭代 | 读取/检索定位章节；五格奖励规则与输出来自本库 |
| F10 | Berkeley CS188，[Model-Free Learning](https://inst.eecs.berkeley.edu/~cs188/textbook/rl/mfl.html)，RL目录标2024-09更新 | TD学习、Q-learning与采样更新 | 读取章节；本地只验证小型确定环境 |
| F11 | Guo et al.，[On Calibration of Modern Neural Networks](https://arxiv.org/abs/1706.04599)，2017，v2 | 校准问题、温度缩放与评估 | 读取摘要与HTML页面；不借用论文数据或性能数字 |
| F12 | NIST，[AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)，核验日官方入口 | 可信AI需要在可靠性、安全、透明、公平与隐私等维度管理风险 | 读取官方入口；本文不是合规认证或法律结论 |
| F13 | Samuel Williams，[Introduction to the Roofline Model](https://amcr.lbl.gov/wp-content/uploads/2025/11/ECP21-Roofline-1-intro-compressed.pdf)，ECP 2021讲义；[官方索引](https://amcr.lbl.gov/departments/computer-science-department/ppan/roofline-performance-model/ppan-roofline-publications/) | 算术强度、计算峰值与带宽上界 | 从作者所在实验室页面打开PDF；URL中的上传年不是讲义年份 |
| F14 | Schulman et al.，[Proximal Policy Optimization Algorithms](https://arxiv.org/pdf/1707.06347v2)，2017，v2 | 策略 log 概率梯度、优势与 PPO 裁剪目标 | 2026-09-07 读取第 2–3 节；本库只用两动作一步更新解释方向，不复现 PPO 训练任务 |

## 按问题追溯

| 本域文章 | 首要来源 | 可以直接运行的本库证据 |
|---|---|---|
| [数学与统计](01-concepts/math-and-statistics/README.md) | F1–F3 | [梯度、收敛、后验实验](04-labs/01-math-and-optimization.ipynb) |
| [机器学习](01-concepts/machine-learning/README.md) | F4、F5 | [泛化与校准](04-labs/02-generalization-and-calibration.ipynb) |
| [深度学习](01-concepts/deep-learning/README.md) | F4、F6 | [自动微分与XOR](04-labs/deep-learning/01-autograd-and-training.ipynb) |
| [经典AI](01-concepts/classical-ai/README.md) | F7、F8 | [图搜索](04-labs/search-and-rl/01-search-and-value-learning.ipynb) |
| [强化学习](01-concepts/reinforcement-learning/README.md) | F9、F10、F14 | [价值迭代与Q-learning](04-labs/search-and-rl/01-search-and-value-learning.ipynb) |
| [可信AI](01-concepts/trustworthy-ai/README.md) | F11、F12 | [独立校准集与测试集](04-labs/02-generalization-and-calibration.ipynb) |
| [计算基础](01-concepts/compute-foundations/README.md) | F13与[基础模型来源](../02-foundation-models/references.md) | [容量与量化](../02-foundation-models/04-labs/02-decoding-cache-and-precision.ipynb) |

[回到领域入口](README.md)。
