# OpenHands 固定版本源码与校验说明

[返回 06 号文件](../06-openhands-source.md) · [返回本章阅读路线](../README.md)

这些文件供最后一份源码导读使用，保留原始路径、行号和许可证。它们是阅读快照，不是可独立安装运行的 SDK。

| 项目 | 固定值 |
|---|---|
| 上游仓库 | [OpenHands/software-agent-sdk](https://github.com/OpenHands/software-agent-sdk) |
| 快照记录的发布版本 | `v1.49.2` |
| 快照记录的提交 | `d128a786ee2ee570eb23ff5862ec148b43cfad0b` |
| 许可证 | MIT，见 [完整许可声明](LICENSE.OpenHands) |
| 原文件 | `upstream/` 下 6 个 Python 文件 |
| 本章原始摘录 | `excerpts/` 下 8 个逐行切片 |
| 校验清单 | [source-manifest.json](source-manifest.json) |
| 校验日期 | 2026-09-20 |

## 本轮校验确认了快照与文档的一致性

源文件沿用此前保存的固定版本快照。本轮重新计算了每个文件的 SHA-256 与 Git blob SHA-1，与既存清单比对一致；重新生成了八个原始切片，再检查切片字节、正文代码块及 1-based inclusive 行号一致。

2026-09-20 重新从上游固定提交读取了六个原文件和 MIT 许可证，SHA-256 均与本地副本一致；`git ls-remote` 确认 `v1.49.2` 指向上述提交。以下命令供读者离线校验本地文件；本章未执行 OpenHands SDK 的模型任务或测试套件。

在本章目录执行：

```bash
python sources/verify_sources.py
```

预期输出：

```text
PASS: 6 source files; 8 excerpts; matching Markdown; MIT license.
This is local integrity verification, not remote provenance or SDK execution verification.
```

## 原文件保留了源码阅读所需的相邻分支

| 原文件 | 阅读目的 |
|---|---|
| [local_conversation.py](upstream/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py) | `run`、停止钩子、确认与拒绝、运行上限 |
| [agent.py](upstream/openhands-sdk/openhands/sdk/agent/agent.py) | 待办动作、输入准备、模型调用、工具与批次收尾 |
| [response_dispatch.py](upstream/openhands-sdk/openhands/sdk/agent/response_dispatch.py) | 响应分类与各类 handler |
| [state.py](upstream/openhands-sdk/openhands/sdk/conversation/state.py) | 动作与结果的关联 |
| [finish.py](upstream/openhands-sdk/openhands/sdk/tool/builtins/finish.py) | 完成请求的动作、执行器与定义 |
| [critic_mixin.py](upstream/openhands-sdk/openhands/sdk/agent/critic_mixin.py) | 结束前继续修订的条件 |

原文件未改写。`excerpts/` 中的切片保留原缩进，通常不具备独立运行条件。正文标记为“流程简写”的代码块是本指南为讲解编写的，不属于上游摘录。
