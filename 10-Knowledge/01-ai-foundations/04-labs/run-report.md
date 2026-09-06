# AI 基础实验运行记录

> 状态：verified · 执行日期：2026-09-06 · 验证对象：本域4本Notebook，共19个代码单元。

环境为Linux、Python 3.12.13、NumPy 2.5.2、IPython 9.17.1、nbformat 5.11.1、nbclient 0.11.0、ipykernel 7.3.0。每本在独立IPython进程中按顺序执行，stdout及assert结果保存到Notebook。环境限制使Jupyter内核socket不可用，未验证内核通信或GUI；没有GPU、API或模型下载。

复现命令（仓库根目录；替换为自己安装依赖的Python即可）：

```bash
python scripts/check_notebooks.py --execute --backend ipython-fallback 10-Knowledge/01-ai-foundations/04-labs/01-math-and-optimization.ipynb 10-Knowledge/01-ai-foundations/04-labs/02-generalization-and-calibration.ipynb 10-Knowledge/01-ai-foundations/04-labs/deep-learning/01-autograd-and-training.ipynb 10-Knowledge/01-ai-foundations/04-labs/search-and-rl/01-search-and-value-learning.ipynb
```

| Notebook | 实际结果 | 说明 |
|---|---|---|
| [数学与优化](01-math-and-optimization.ipynb) | 5/5代码单元通过；解析/数值梯度最大差约1.86×10^-10；恢复权重[1,2] | 输入形状错误被拒绝；学习率2.2的一维二次问题出现振荡发散 |
| [泛化与校准](02-generalization-and-calibration.ipynb) | 4/4通过；3阶测试网格MSE约0.03288；15阶约3.175×10^6；15阶岭回归约0.08719 | 高阶带噪拟合在训练边界外及覆盖薄弱区强烈不稳定，含多项式病态性影响；不能只用此例量化一般泛化风险 |
| 同本校准部分 | 校准集选T=2.85；测试NLL 0.779112→0.600481；ECE 0.162948→0.016775；准确率均0.675714 | logits人为乘3构造过度自信，测试集未用于选温度 |
| [自动微分与训练](deep-learning/01-autograd-and-training.ipynb) | 5/5通过；共享节点梯度7；XOR损失1.03539→约2.64×10^-30，四点符号全对 | 证明拟合/梯度机制，四点既是训练点也是检查点，不声称泛化 |
| [搜索与价值学习](search-and-rl/01-search-and-value-learning.ipynb) | 5/5通过；BFS成本9，UCS/A*成本5，展开数分别5/4；重开案例成本4 | 有限非负图；启发式人工给定 |
| 同本RL部分 | 学到最优值[0.729,0.81,0.9,1,0]，最大误差约8.88×10^-16；贪心评估4步终止 | epsilon=0对照Q表保持零；不是一般Q-learning收敛证明 |

运行时修复过搜索Notebook中一个输出字符串的换行转义错误，之后该Notebook全部单元重新执行通过。保存结果只保留修复后输出。所有数值来自实际执行，没有把预期值填作输出。

本报告不覆盖真实数据、PyTorch/GPU、MCTS/CSP实现、POMDP求解或生产安全与公平评测。文章保留`draft`状态，实验`verified`只对应本表范围。
