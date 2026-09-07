# 运行实验与维护检查

所有命令从仓库根目录执行，即同时能看到 `10-Knowledge/`、`20-Projects/` 和 `scripts/` 的目录。先按要做的实验安装依赖；阅读 Markdown 和 GitHub 上已保存的 Notebook 输出无需安装环境。

## 只想先运行一个学习项目

Python 3.11 或更高即可，以下命令只用标准库：

```bash
python scripts/run_python.py -m domain_research.cli --query ERR-12003 --run-id first --output .runs/first-lesson
python scripts/run_python.py -m learning_workbench.cli memory --output .runs/memory-lesson
```

第一条直接打印回答和引用，第二条打印报告路径；怎样读结果分别见[领域资料研究助手](../20-Projects/domain-research-agent/README.md)和[学习工作台](../20-Projects/learning-workbench/README.md)。生成文件进入指定输出目录；比较新方案时使用新的 run-id 或目录，避免把恢复旧任务误当成重新实验。

`run_python.py` 只把本仓库的各个 `src/` 加入 Python 导入路径，因此项目可以复用其他知识领域的实现。它不会安装依赖；请保持完整仓库结构，不能只复制一个 `src/` 就认为依赖齐全。

## 执行 Notebook

完整复现环境使用 Python 3.12（与 CI 一致）。先创建虚拟环境：

```bash
python -m venv .venv
```

| 终端 | 激活命令 | 验证选中了哪个解释器 |
| --- | --- | --- |
| macOS / Linux bash | `source .venv/bin/activate` | `python -c "import sys; print(sys.executable)"` |
| Windows PowerShell | `.\.venv\Scripts\Activate.ps1` | 同上 |
| Windows cmd | `.venv\Scripts\activate.bat` | 同上 |

解释器路径应指向这个仓库的 `.venv`。也可不激活，直接用 `.venv/bin/python`（Windows 为 `.\.venv\Scripts\python.exe`）替代下面的 `python`。

```bash
python -m pip install -r requirements-dev.lock
python -m ipykernel install --sys-prefix --name python3
```

`requirements-dev.lock` 固定本库已验证的 Python 依赖版本，提供 NumPy、IPython、Notebook 执行与 Schema 校验。它不包含编辑器或 Notebook 网页服务。可以在已有的 Jupyter 前端或 VS Code 中选择这份 `.venv` 的内核，然后执行“重启内核并运行全部”；只打开页面查看旧输出不算重新执行。

先运行一本纯 Python 基础实验：

```bash
python scripts/check_notebooks.py --execute 10-Knowledge/02-foundation-models/04-labs/01-tokenization-and-attention.ipynb
```

脚本以 Notebook 所在目录为工作目录，从干净内核运行，并把新输出保存回该 `.ipynb`。正常结果含 `status: executed`；想只检查文件结构和已有错误输出，去掉 `--execute`。

要运行全部 20 本 Notebook，还需下面的 CPU 训练/PDF 依赖，以及 Node.js 22 或更高版本。Tools Notebook 会实际运行 TypeScript 工具执行器和 MCP stdio 客户端/服务端；这一步并非只用 Python 演示接口。

```bash
python -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install pypdf==6.1.0 reportlab==4.4.3
npm ci --prefix 10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript
npm ci --prefix 10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript
python scripts/check_notebooks.py --execute
```

上述过程不下载预训练语言模型，也不调用付费 API。Tiny Transformer 会在构造的小数据上实际训练；学习工作台 Notebook 会读取仓库中的历史模型报告，运行当下的离线实验，二者在各本 Notebook 中分别标明。想重跑预训练模型，按[工作台的可选模型步骤](../20-Projects/learning-workbench/README.md)安装 `requirements-learning.txt` 并下载固定模型。

如果环境明确禁止 Jupyter 内核所需的本地 socket，可运行 `python scripts/check_notebooks.py --execute --backend ipython-fallback`。它为每本 Notebook 启动独立 Python 进程，经 IPython 依次执行代码并保存输出，元数据会注明后端。该模式不验证内核通信或前端交互；CI 仍用标准 Jupyter 后端。

## 修改后怎样检查

在上面的完整环境中运行：

```bash
python scripts/check_links.py
python scripts/check_metadata.py
python scripts/run_python_tests.py
```

| 脚本 | 检查或执行内容 | 如何理解通过结果 |
| --- | --- | --- |
| [check_links.py](check_links.py) | Markdown 与 Notebook Markdown 的相对路径、支持范围内的标题锚点 | 能找到目标文件/标题，不代表读者能理解或远端链接可访问 |
| [check_metadata.py](check_metadata.py) | 一级标题、概念/模式/案例状态字段 | 格式有效，不等于事实已审查 |
| [check_notebooks.py](check_notebooks.py) | 格式、代码单元和错误输出；加 `--execute` 才重跑 | 区分 `format-valid` 与 `executed`；每格默认超时 180 秒 |
| [run_python_tests.py](run_python_tests.py) | 各工程 `unittest` 及指定算例断言 | 看实际失败和 skip；依赖缺失导致跳过不算对应功能已验证 |
| [run_python.py](run_python.py) | 按本仓库源码路径运行模块或脚本 | 只提供导入路径，不自动安装库或覆盖版本 |

TypeScript 工程各自在项目目录运行 `npm ci`、`npm run build`、`npm test`；[浏览器工程](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/README.md)还需要安装 Chromium。对应自动检查见 [workflows](../.github/workflows/README.md)，实际结果以具体提交的 Actions 为准。

## 遇到运行问题先检查哪里

| 现象 | 最先检查 | 原因 |
| --- | --- | --- |
| 找不到 `scripts/run_python.py` | 终端是否处于仓库根目录 | 文档命令的相对路径以根目录为基准 |
| `ModuleNotFoundError` 指向本库包 | 是否通过 `run_python.py` 启动，是否保留完整仓库 | 综合项目跨领域复用 `src/`，不是独立发布的包 |
| 缺少 `torch`、`nbformat` 等外部包 | 安装依赖与运行时是否用了同一个 Python | 在另一个环境安装不影响当前内核 |
| Notebook 里变量不存在 | 重启内核并从第一格依次执行 | 后面格依赖前面构造的对象 |
| Notebook 提示内核不存在 | 执行 `ipykernel install`，确认前端选中该环境 | 有 `.ipynb` 文件不代表已经有可运行内核 |
| 改问题后仍看到旧任务结果 | run-id 与输出目录是否复用 | 持久任务身份用于恢复，比较实验应使用新身份 |
