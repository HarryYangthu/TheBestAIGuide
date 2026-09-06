# AI 基础实验

> 状态：verified · 验证范围：4本Notebook共19个代码单元已真实执行；所有数据为教学构造。

| 实验 | 要观察的现象 | 先读 |
|---|---|---|
| [01 数学与优化](01-math-and-optimization.ipynb) | 形状拒绝、梯度差分、收敛与发散、告警后验 | [数学与统计](../01-concepts/math-and-statistics/README.md) |
| [02 泛化与校准](02-generalization-and-calibration.ipynb) | 高阶拟合在训练覆盖不足区域失稳；温度改善概率但不改准确率 | [机器学习](../01-concepts/machine-learning/README.md)、[可信AI](../01-concepts/trustworthy-ai/README.md) |
| [03 自动微分与训练](deep-learning/01-autograd-and-training.ipynb) | 共享节点梯度累加、tanh链式法则、XOR学习 | [深度学习](../01-concepts/deep-learning/README.md) |
| [04 搜索与价值学习](search-and-rl/01-search-and-value-learning.ipynb) | 步数/成本差别、A*重开、Q-learning探索失败 | [经典AI](../01-concepts/classical-ai/README.md)、[强化学习](../01-concepts/reinforcement-learning/README.md) |

## 运行

先安装[固定依赖](../05-code/requirements.txt)，再用已有的Jupyter或支持Notebook的编辑器按顺序运行。Notebook从当前路径向上定位仓库根目录，直接加载[完整源码](../05-code/foundations_core.py)，无需复制粘贴多个代码块。

也可在仓库根目录运行单本（默认后端使用Jupyter内核）：

```bash
python scripts/check_notebooks.py --execute 10-Knowledge/01-ai-foundations/04-labs/01-math-and-optimization.ipynb
```

本次环境禁止内核socket，因此已保存的输出采用每本独立IPython进程实际顺序执行，命令为：

```bash
python scripts/check_notebooks.py --execute --backend ipython-fallback 10-Knowledge/01-ai-foundations/04-labs/01-math-and-optimization.ipynb
```

这一执行验证了Python计算与断言，未验证Jupyter内核通信和交互界面。完整版本、命令和数值结果见[运行记录](run-report.md)。正文中没有对应实验的MCTS、POMDP、公平性评测等内容为机制说明，不列为实验已验证。

## 标准内核验证更新（2026-09-06）

提交 `5e5a40c09e00028c7887fd3bf3bd559d96fc972f` 的 [GitHub Actions 标准 Jupyter 执行](https://github.com/HarryYangthu/TheBestAIGuide/actions/runs/34013521515)已成功。原 Notebook 保存输出的本地 IPython 来源保留；这条更新补充标准内核证据，不代表交互控件或所有前端已验收。本轮新项目与后续结果见仓库 `00-Home/Round2-Completion.md`。
