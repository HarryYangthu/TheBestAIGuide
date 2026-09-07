# Agent Loop 实验

> 状态：verified | 验证范围：本地规则策略、工具返回、重复停止和预算停止

打开[01-agent-loop.ipynb](01-agent-loop.ipynb)，顺序执行。实验导入[完整源码工程](../05-code/agent-loop-python/README.md)，无模型API和网络依赖。Notebook展示的“完成”只证明控制流程满足规则，不代表真实LLM任务成功率。

先按[统一环境说明](../../../scripts/README.md)安装 Notebook 依赖并选择对应内核，再“重启内核并运行全部”。也可从仓库根目录执行：

```bash
python scripts/check_notebooks.py --execute 10-Knowledge/03-agent-core/04-labs/01-agent-loop.ipynb
```

应看到正常任务两步完成、重复任务第二步停止、一步预算只能完成搜索而无法再生成结束动作。把查询改成不存在的词后，工具成功返回空列表；请区分“没有证据”和“工具报错”。

## 标准内核验证更新（2026-09-06）

初次保存输出的本地环境限制内核 socket，因此用了独立进程内的 IPython；提交 `5e5a40c09e00028c7887fd3bf3bd559d96fc972f` 的 [GitHub Actions 标准 Jupyter 执行](https://github.com/HarryYangthu/TheBestAIGuide/actions/runs/34013521515)随后成功。两条记录验证的后端不同，不代表所有 Notebook 前端均已验收。后续结果见 [Round2 完成记录](../../../00-Home/Round2-Completion.md)。
