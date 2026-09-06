# Context Engineering Labs

> 状态：verified
> 执行日期：2026-09-06；Python 3.12.13；两本共 7 个代码单元真实执行。

| 实验 | 看什么 | 实际结果 |
| --- | --- | --- |
| [预算打包](01-token-budget.ipynb) | 先权限过滤、保留硬约束、给输出留空间 | 318 字节头截断漏证据；212 字节打包保留目标/约束/证据 |
| [结构化压缩](02-context-compaction.ipynb) | 失败不能变成功，待办不能丢，事实带来源 | 原始 3388 字节 → 201 字节；已标注字段 3/3 保留，截断基线仅 1/3 |

输入全是人工构造教学事件。默认计数器每 UTF-8 字节算一个教学 token，不是任何商用模型的 tokenizer；代码允许注入真实计数函数。没有调用模型，没有测试 Context Rot 或开放式摘要质量。

[context_lab.py](context_lab.py)是完整可读实现，正文对应 [Context Builder](../02-patterns/01-context-builder.md) 和 [优化策略](../02-patterns/02-optimization-strategies.md)。所有 Notebook 均保存中间量、检查、对照和局限。

环境禁止 Jupyter TCP/IPC socket，实际后端为每本独立 Python 进程内的 IPython 顺序执行；Jupyter 内核通信本环境未验证。nbformat 5.11.1、IPython 9.17.1，正常 Jupyter 环境可使用 nbclient 0.11.0/ipykernel 7.3.0 Run All。源码只依赖标准库。

## 标准内核验证更新（2026-09-06）

提交 `5e5a40c09e00028c7887fd3bf3bd559d96fc972f` 的 [GitHub Actions 标准 Jupyter 执行](https://github.com/HarryYangthu/TheBestAIGuide/actions/runs/34013521515)已成功。原 Notebook 保存输出的本地 IPython 来源保留；这条更新补充标准内核证据，不代表交互控件或所有前端已验收。本轮新项目与后续结果见仓库 `00-Home/Round2-Completion.md`。
