# 工具契约与错误实验

> 状态：verified | 范围：12个Schema正反例、TS执行控制与真实MCP stdio调用

打开[Notebook](01-tool-contracts-and-errors.ipynb)。Python段需要`jsonschema`；TS段先分别在 [Tool Runtime](../05-code/tool-runtime-typescript/README.md) 和 [MCP Server/Client](../05-code/mcp-server-typescript/README.md) 工程执行`npm ci`。Notebook 的 Python 段展示 12 个基础正反例；TS 测试还会执行 47 个边界反例。实验不接模型、不查询真实企业资料，不把本地教学数据当作业务结果。

依赖与内核设置见[统一环境说明](../../../scripts/README.md)。完成上面两项 `npm ci` 后，从仓库根目录执行：

```bash
python scripts/check_notebooks.py --execute 10-Knowledge/05-tools-skills-protocols/04-labs/01-tool-contracts-and-errors.ipynb
```

先观察同一个空格查询：字符串 Schema 接受它，业务逻辑拒绝它；再观察 MCP `isError` 与正常返回空文档列表的区别。最后一个代码单元会启动真实 stdio 子进程，不能只看前面的 Python 校验就认为协议调用已跑通。

## 标准内核验证更新（2026-09-06）

初次保存输出的本地环境限制内核 socket，因此用了独立进程内的 IPython；提交 `5e5a40c09e00028c7887fd3bf3bd559d96fc972f` 的 [GitHub Actions 标准 Jupyter 执行](https://github.com/HarryYangthu/TheBestAIGuide/actions/runs/34013521515)随后成功。两条记录验证的后端不同，不代表所有 Notebook 前端均已验收。后续结果见 [Round2 完成记录](../../../00-Home/Round2-Completion.md)。
