# 统一验证记录

> 日期：2026-09-06；基线提交：`f9729ba319a5cf0911b009c863a4796a888d8306`。

| 验证 | 实际结果 | 记录 |
| --- | --- | --- |
| Python unittest | 12 组、67 项全部通过 | [完整输出](verification/python-tests.txt) |
| 生产/研究机制脚本 | 两份脚本的内置断言通过 | 同上，日志末尾 |
| TypeScript Tool Runtime | 8 项通过，含共享 Schema 的 12 个正反例 | [输出](verification/tool-runtime-tests.txt) |
| MCP stdio 集成 | 2 项通过，真实启动服务端子进程 | [输出](verification/mcp-tests.txt) |
| Chromium 本地页面 | 3 项端到端测试通过 | [输出](verification/browser-tests.txt) |
| Notebook | 18 本、86 个代码单元实际执行通过，输出保存在各本中 | [逐本记录](verification/notebooks.jsonl) |
| 综合项目 | 6 项集成测试；4 类构造任务各 2 次均通过 | [运行报告](../20-Projects/domain-research-agent/run-report.md) |
| 文档链接与元数据 | 本次全库检查通过；具体数量见机器记录 | [链接](verification/links.json)、[元数据](verification/metadata.json) |

## 环境和复现

Python 3.12.13、NumPy 2.5.2；开发依赖固定在根目录 `requirements-dev.lock`。TypeScript 实测 Node 24.19.0，各工程 package-lock 固定依赖；CI 使用 Node 22，兼容性以对应远端运行结果为准。

Notebook 的 Jupyter TCP 与 IPC 通信均被本地环境拒绝，因此使用 `--backend ipython-fallback`：每本独立进程，通过 IPython 从头依次执行所有代码格，捕获真实输出和异常。没有跳过断言或手工填结果；尚未验证完整 Jupyter 内核通信、前端交互。CI 默认使用 nbclient 和标准内核。

复现命令见[scripts](../scripts/README.md)。GitHub Actions 是否成功以本次分支对应的远端运行记录为准，不以工作流文件存在代替运行结果。

## 本轮修正的实际反例

| 发现 | 为什么会错 | 修正 |
| --- | --- | --- |
| Attention 导数变量不清 | 对缩放后 logits 与未缩放点积分数求导不同 | 明确变量并说明链式缩放 |
| 模型替换错误码 | 原文真实，但回答的是另一个问题 | 综合项目绑定原查询 |
| 多编号文档块继承所有编号 | 精确匹配退化为“同文档出现过” | 按块定位编号，补缺失 metadata 情形 |
| Top-k 先截块再去重 | 文档数量不足，评测口径失真 | 按文档去重后截断 |
| Grader 配置非法 | 评分器异常被误算成被测系统失败 | 加载时拒绝不合法配置 |
| 工具参数在异步启动前被改 | 校验和实际执行不再使用同一输入 | 参数与身份在入口保存快照 |
| 取消后仍启动 Handler | 外层返回取消，内部却执行动作 | 启动前再次检查取消 |
| 非法 JSON / 共享返回对象 | 未捕获异常或历史状态被后续调用改写 | 严格 JSON 契约、结果与事件快照 |

这些反例均进入了针对性修复与测试。合作取消仍不能强杀不配合的工具；隔离、幂等、权限和持久化也都限定在各章明确的实现范围。

## 不能从这些结果推出什么

全部能力测量均是数值实验、确定性策略或构造 fixture。没有实际训练大模型，没有完成真实语义向量检索、LLM Judge 专家校准、任意网页自主操作、线上负载测试或外部科研基准复现。各专题已把这些扩展方向与本地已运行部分分开说明。
