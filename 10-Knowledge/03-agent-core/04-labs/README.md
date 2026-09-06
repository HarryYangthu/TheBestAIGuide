# Agent Loop 实验

> 状态：verified | 验证范围：本地规则策略、工具返回、重复停止和预算停止

打开[01-agent-loop.ipynb](01-agent-loop.ipynb)，顺序执行。实验导入[完整源码工程](../05-code/agent-loop-python/README.md)，无模型API和网络依赖。Notebook展示的“完成”只证明控制流程满足规则，不代表真实LLM任务成功率。

执行说明：当前环境使用独立Python进程内的IPython顺序执行实际代码并保存输出；Jupyter内核的socket通信在本环境受限，未宣称验证其启动。读者可在本地Jupyter直接顺序运行；仓库提供`python scripts/check_notebooks.py --execute --backend ipython-fallback <Notebook路径>`作为显式替代方式。

## 标准内核验证更新（2026-09-06）

提交 `5e5a40c09e00028c7887fd3bf3bd559d96fc972f` 的 [GitHub Actions 标准 Jupyter 执行](https://github.com/HarryYangthu/TheBestAIGuide/actions/runs/34013521515)已成功。原 Notebook 保存输出的本地 IPython 来源保留；这条更新补充标准内核证据，不代表交互控件或所有前端已验收。本轮新项目与后续结果见仓库 `00-Home/Round2-Completion.md`。
