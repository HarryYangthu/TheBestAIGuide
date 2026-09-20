# 权限与注入后果实验

> 状态：verified（本地 fixture、授权和审批绑定）；执行日期：2026-09-06。

[01-policy-and-injection.ipynb](01-policy-and-injection.ipynb)包含 2 条合法读取与 4 条越权动作，再验证合法审批删除、跨对象令牌拒绝和审计字段。运行后的结构化证据保存在 [artifacts/policy.json](artifacts/policy.json)。

实验不执行网络、shell 或真实文件删除，只对 Python 字典中的教学记录操作。它假定模型已经提出动作，再测执行边界；不能拿拒绝比例当真实模型抗注入成功率。正常请求通过同样是验收条件。

Python 3.11+，代码只用标准库；Notebook 使用 Jupyter / ipykernel。也可直接按[代码说明](../05-code/README.md)运行测试。先读[注入机制](../01-concepts/01-threat-model-and-injection.md)，返回[本域导航](../README.md)。

本次保存的输出由独立 Python 进程中的 IPython 顺序执行得到。环境禁止 Kernel socket，因此没有使用 Jupyter kernel；Notebook 元数据明确记录 `execution_backend`，错误会使执行失败。

[本次运行记录](run-report.md)列出命令、实际结果与未验证范围。

## 标准内核验证更新（2026-09-06）

提交 `5e5a40c09e00028c7887fd3bf3bd559d96fc972f` 的 [GitHub Actions 标准 Jupyter 执行](https://github.com/HarryYangthu/TheBestAIGuide/actions/runs/34013521515)已成功。原 Notebook 保存输出的本地 IPython 来源保留；这条更新补充标准内核证据，不代表交互控件或所有前端已验收。本轮新项目与后续结果见仓库 `00-Home/Round2-Completion.md`。
