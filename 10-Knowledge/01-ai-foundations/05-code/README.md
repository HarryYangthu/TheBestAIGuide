# AI 基础：可运行源码

> 状态：verified · 范围：对应4个教学Notebook调用的函数与断言已实跑；不是通用训练框架。

[foundations_core.py](foundations_core.py)包含线性损失与梯度、岭回归、稳定sigmoid/NLL、校准指标、反向标量自动微分、XOR训练、A*、五格价值迭代和Q-learning。只依赖NumPy与Python标准库；Notebook执行工具的固定依赖另见[requirements.txt](requirements.txt)。

| 函数/类 | 输入和输出 | 对应阅读与实验 |
|---|---|---|
| `mse_gradient` | X:(n,d)、y:(n,)、w:(d,) → 标量loss与(d,)梯度 | [数学](../01-concepts/math-and-statistics/README.md)、[实验](../04-labs/01-math-and-optimization.ipynb) |
| `ridge_fit` | 设计矩阵、标签、非负惩罚 → 权重；第一列视为偏置不惩罚 | [机器学习](../01-concepts/machine-learning/README.md)、[实验](../04-labs/02-generalization-and-calibration.ipynb) |
| `calibration_metrics` | 二分类logits与0/1标签 → accuracy/NLL/Brier/ECE/分箱 | [可信AI](../01-concepts/trustworthy-ai/README.md) |
| `Scalar`、`train_xor` | 标量计算图/固定教学配置 → 梯度与拟合结果 | [深度学习](../01-concepts/deep-learning/README.md)、[实验](../04-labs/deep-learning/01-autograd-and-training.ipynb) |
| `astar` | 非负权图、起终点、启发式 → 路径、成本、展开数 | [经典AI](../01-concepts/classical-ai/README.md) |
| `value_iteration`、`q_learning` | 五格环境超参数 → 状态值/Q表 | [强化学习](../01-concepts/reinforcement-learning/README.md)、[实验](../04-labs/search-and-rl/01-search-and-value-learning.ipynb) |

在仓库根目录创建并激活自己的Python 3.12虚拟环境后安装：

```bash
python -m pip install -r 10-Knowledge/01-ai-foundations/05-code/requirements.txt
```

从[Notebook入口](../04-labs/README.md)运行。源码故意避免框架封装，方便逐行对照公式；例如`Scalar.backward()`先清零再沿逆拓扑累加梯度，这个行为与某些框架默认梯度累积不同。A*图节点在本例中都是字符串，优先队列平局时会比较节点；若扩展到不可比较对象，应增加稳定序号作为tie-breaker。

[真实运行记录](../04-labs/run-report.md)。
