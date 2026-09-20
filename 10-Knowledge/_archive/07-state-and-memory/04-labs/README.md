# 状态与记忆实验

> 状态：verified | 范围：快照恢复、CAS冲突、TTL、主体隔离、删除与规则对照

[Notebook](01-state-memory-and-conflicts.ipynb)使用临时SQLite文件与人工构造事实，执行后清理临时目录。先观察事务和版本，再比较不读取Memory、全量历史和按主体/时间过滤。比较结果是规则行为，不代表LLM增益。

代码和测试入口见[工程README](../05-code/state-memory-python/README.md)。

执行说明：当前环境使用独立Python进程内的IPython顺序执行实际代码并保存输出；Jupyter内核的socket通信在本环境受限，未宣称验证其启动。读者可在本地Jupyter直接顺序运行；仓库提供`python scripts/check_notebooks.py --execute --backend ipython-fallback <Notebook路径>`作为显式替代方式。

## 标准内核验证更新（2026-09-06）

提交 `5e5a40c09e00028c7887fd3bf3bd559d96fc972f` 的 [GitHub Actions 标准 Jupyter 执行](https://github.com/HarryYangthu/TheBestAIGuide/actions/runs/34013521515)已成功。原 Notebook 保存输出的本地 IPython 来源保留；这条更新补充标准内核证据，不代表交互控件或所有前端已验收。本轮新项目与后续结果见仓库 `00-Home/Round2-Completion.md`。
