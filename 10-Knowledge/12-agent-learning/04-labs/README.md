# Agent Learning 实验

> 状态：draft · 更新：2026-09-06

打开[轨迹与奖励 Notebook](01-trajectories-and-rewards.ipynb)，从第一格运行到最后一格。可先查看已保存输出，再修改 mask、偏好对与奖励反例。

环境：Python 3.12；计算只依赖标准库，Notebook 界面需要 Jupyter/IPython。源码与独立测试在[05-code](../05-code/README.md)。本次用仓库的独立进程 IPython 执行器逐格执行 6 个代码单元；环境拒绝 Jupyter kernel 通道，因此没有把 kernel 协议运行写成通过。

从仓库根目录可使用：

```bash
python scripts/check_notebooks.py --execute --backend ipython-fallback 10-Knowledge/12-agent-learning/04-labs/01-trajectories-and-rewards.ipynb
```

已验证：泄露被拒绝、mask 保持上下文位置不计损失、偏好目标变化、奖励伪造反例、等分组优势为零。未验证：真实模型训练收敛、跨任务泛化或任何生产指标。

## 标准内核验证更新（2026-09-06）

提交 `5e5a40c09e00028c7887fd3bf3bd559d96fc972f` 的 [GitHub Actions 标准 Jupyter 执行](https://github.com/HarryYangthu/TheBestAIGuide/actions/runs/34013521515)已成功。原 Notebook 保存输出的本地 IPython 来源保留；这条更新补充标准内核证据，不代表交互控件或所有前端已验收。本轮新项目与后续结果见仓库 `00-Home/Round2-Completion.md`。
