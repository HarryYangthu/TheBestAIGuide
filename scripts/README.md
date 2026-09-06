# 仓库维护与运行脚本

从仓库根目录运行。标准库检查不需要安装依赖；Notebook 和部分教学实验需要 Python 3.12 及根目录的 `requirements-dev.lock`。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.lock
pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
pip install pypdf==6.1.0 reportlab==4.4.3
python -m ipykernel install --sys-prefix --name python3
python scripts/check_links.py
python scripts/check_metadata.py
python scripts/run_python_tests.py
npm ci --prefix 10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript
npm ci --prefix 10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript
python scripts/check_notebooks.py --execute
```

Windows 激活命令是 `.venv\Scripts\activate`。锁文件记录本次实际安装版本，用于复现。

执行全部 Notebook 还需要 Node.js 22 或更高版本：Tools 实验会运行真实 TypeScript Runtime 和 MCP stdio 集成，所以先安装上面两个工程的 npm 依赖。单独执行纯 Python Notebook 时不需要这一步。

如果环境禁止 Jupyter 内核使用本地 socket，可显式运行 `python scripts/check_notebooks.py --execute --backend ipython-fallback`。它为每本 Notebook 启动独立 Python 进程，经 IPython 依次执行全部代码格并保存真实输出；元数据会注明后端。该模式不验证 Jupyter 内核通信和前端交互，CI 仍使用默认 Jupyter 后端。

| 脚本 | 检查或执行内容 | 边界 |
| --- | --- | --- |
| [check_links.py](check_links.py) | Markdown、Notebook Markdown 中的相对文件和目录链接；跳过代码围栏 | 不发外网请求；检查本仓 Markdown 的中文、重复标题锚点，支持范围见 heading_anchors；不验证远端内容 |
| [check_metadata.py](check_metadata.py) | 一级标题；概念、模式、案例的状态字段 | 不把格式通过当成事实审查 |
| [check_notebooks.py](check_notebooks.py) | Notebook 结构、非空代码、错误输出；`--execute` 从干净内核执行并更新输出 | 工作目录是 Notebook 所在目录，默认每格 180 秒 |
| [run_python_tests.py](run_python_tests.py) | 加入本库源码路径，分别运行各工程 `tests/test_*.py` 的 unittest | 失败返回非零；不运行外部服务或 GPU 训练 |
| [run_python.py](run_python.py) | 运行模块或脚本，复用各领域 `src/` | 不自动安装依赖，不覆盖包版本 |

例如 `python scripts/run_python.py -m domain_research.cli` 可运行综合项目。只执行一个 Notebook：`python scripts/check_notebooks.py --execute <相对路径.ipynb>`。

TypeScript 工程分别执行 `npm ci`、`npm run build`、`npm test`。浏览器工程还需 `npx playwright install chromium`。CI 定义见 [workflows](../.github/workflows/README.md)。
