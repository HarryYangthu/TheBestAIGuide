# 本地标准库源码来源

本目录保存 CPython 3.12.14 运行时实际使用的 `Lib/asyncio/queues.py` 及随运行时附带的许可证。来源绝对路径、Python 版本和 SHA-256 见 [manifest.json](manifest.json)。原文件未经改动，用于走读 `Queue.put/get/task_done/join`。

上游项目为 [python/cpython](https://github.com/python/cpython)，接口参见 [Python 官方 Queue 文档](https://docs.python.org/3.11/library/asyncio-queue.html)。固定的是已安装运行时的版本和源码字节；本次未从远端发布包下载并逐字节比较，清单中的 `remote_bytes_verified` 为 `false`。

在章节目录运行 `python sources/verify_sources.py`，标准输出为 `verified=2 runtime=CPython 3.12.14`，不生成产物。源码含相对导入，供阅读和核对，不作为本章独立执行入口。
