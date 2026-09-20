# AI 基础

> 状态：draft · 7篇概念正文；4个教学Notebook已实跑，具体范围见[运行记录](04-labs/run-report.md)。

这一域为理解基础模型和Agent提供理论底座。先读机制与算例，再运行对应实验，最后到源码查看完整实现。教程保留推导、错误条件与实践边界，来源核验不等于人工审稿。

| 顺序 | 学习主题 | 最值得掌握的内容 | 对应实践 |
|---|---|---|---|
| 1 | [数学与统计](01-concepts/math-and-statistics/README.md) | 张量轴、点积、后验、交叉熵、梯度和实验单位 | [矩阵与优化](04-labs/01-math-and-optimization.ipynb) |
| 2 | [机器学习](01-concepts/machine-learning/README.md) | 目标与指标、数据划分、泄漏、泛化与分布偏移 | [泛化对照](04-labs/02-generalization-and-calibration.ipynb) |
| 3 | [深度学习](01-concepts/deep-learning/README.md) | 非线性、计算图、梯度累加、训练循环与优化器 | [标量Autograd与XOR](04-labs/deep-learning/01-autograd-and-training.ipynb) |
| 4 | [经典AI](01-concepts/classical-ai/README.md) | 状态空间、搜索最优性、启发式、MCTS与约束 | [BFS/UCS/A*](04-labs/search-and-rl/01-search-and-value-learning.ipynb) |
| 5 | [强化学习](01-concepts/reinforcement-learning/README.md) | MDP/POMDP、回报、Bellman、Q学习与探索 | [价值迭代与Q-learning](04-labs/search-and-rl/01-search-and-value-learning.ipynb) |
| 6 | [可信AI](01-concepts/trustworthy-ai/README.md) | 校准、OOD、鲁棒、公平、解释和隐私的分开评测 | [温度缩放与覆盖率](04-labs/02-generalization-and-calibration.ipynb) |
| 7 | [计算基础](01-concepts/compute-foundations/README.md) | 显存组成、算力/带宽、精度、性能测量 | [缓存容量与量化](../02-foundation-models/04-labs/02-decoding-cache-and-precision.ipynb) |

[实验与运行方法](04-labs/README.md) · [可复用源码](05-code/README.md) · [一手来源与主张范围](references.md)。下一域：[基础模型](../02-foundation-models/README.md)。
