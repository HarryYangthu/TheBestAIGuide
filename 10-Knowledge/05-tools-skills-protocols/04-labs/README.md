# 工具契约与错误实验

> 状态：verified | 范围：12个Schema正反例、TS执行控制与真实MCP stdio调用

打开[Notebook](01-tool-contracts-and-errors.ipynb)。Python段需要`jsonschema`；TS段先在两个[工程](../05-code/tool-runtime-typescript/README.md)执行`npm ci`。实验不接模型、不查询真实企业资料，不把本地教学数据当作业务结果。

执行说明：当前环境使用独立Python进程内的IPython顺序执行实际代码并保存输出；Jupyter内核的socket通信在本环境受限，未宣称验证其启动。读者可在本地Jupyter直接顺序运行；仓库提供`python scripts/check_notebooks.py --execute --backend ipython-fallback <Notebook路径>`作为显式替代方式。

## 标准内核验证更新（2026-09-06）

提交 `5e5a40c09e00028c7887fd3bf3bd559d96fc972f` 的 [GitHub Actions 标准 Jupyter 执行](https://github.com/HarryYangthu/TheBestAIGuide/actions/runs/34013521515)已成功。原 Notebook 保存输出的本地 IPython 来源保留；这条更新补充标准内核证据，不代表交互控件或所有前端已验收。本轮新项目与后续结果见仓库 `00-Home/Round2-Completion.md`。
