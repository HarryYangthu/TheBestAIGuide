# 本地标准库源码来源

本目录保存 CPython 3.12.14 运行时实际使用的 `Lib/graphlib.py` 及随运行时附带的许可证。来源绝对路径、Python 版本和文件 SHA-256 见 [manifest.json](manifest.json)。文件未经修改，便于离线走读 `TopologicalSorter.prepare/get_ready/done`。

上游项目为 [python/cpython](https://github.com/python/cpython)，模块接口参见 [Python 官方 graphlib 文档](https://docs.python.org/3.11/library/graphlib.html)。这里固定的是已安装运行时的版本和源码字节；本次没有从远端发布包重新下载并进行字节比对，清单中的 `remote_bytes_verified` 因此为 `false`。

在章节目录运行 `python sources/verify_sources.py`。它只读两份快照并校验清单，标准输出是 `verified=2 runtime=CPython 3.12.14`，不生成产物。
