# 自动检查

| 工作流 | 触发范围 | 门禁 |
| --- | --- | --- |
| [docs.yml](docs.yml) | Push / PR | 相对链接、文章状态格式、维护脚本测试 |
| [python.yml](python.yml) | Python、配置、数据、依赖变更 | 各工程测试与综合项目四类任务 |
| [typescript.yml](typescript.yml) | TypeScript、依赖、数据变更 | 三个工程独立安装、构建、测试；浏览器使用本地 fixture |
| [notebooks.yml](notebooks.yml) | Notebook、Python/TypeScript、数据、依赖变更 | 安装 Python 和两个工具工程的 Node 依赖，从干净内核执行全部 Notebook |

权限为 `contents: read`，CI 不自动改文章、提交文件或发布网站。外部链接由已创建的月度定时任务独立汇报；远端临时限流不能直接判成链接失效。

本地重现命令见 [scripts](../../scripts/README.md)。工作流文件存在不等于远端已成功运行；具体 Actions 状态以对应提交记录为准。

第二轮新增：共享 Schema/边界 JSON 改动会触发 Python、TypeScript 与 Notebook 工作流；Python/Notebook 安装 CPU PyTorch 与 PDF 依赖，避免新增测试仅以 skip 通过。浏览器矩阵同时验收学习工作台的审批/取消网页流程。预训练模型下载与长模型评测不在每次 PR 强制执行，已固定版本的本地真实结果保存在项目 artifacts。
