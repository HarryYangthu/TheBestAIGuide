# 上下文工程内容覆盖表

对照来源：[归档版上下文工程](../../_archive/04-context-engineering/README.md)。本表按知识点定位到当前正文和可运行材料；原版使用的 SDK 升级、告警等例子统一映射到本章发布审核任务。

| 归档来源 | 知识点 | 当前正文 | 代码或可核对产物 |
|---|---|---|---|
| 总览：定义 | 每轮选择、转换、排序、组织信息 | [01：上下文组成](01-isolation-and-loading.md) | `first_context.py`、实际 messages |
| 总览：相邻概念 | Prompt、RAG、Memory、Runtime、Training 边界 | [01：相关概念](01-isolation-and-loading.md) | 职责与例子对照表 |
| 总览：五个问题 | 来源、信任、相关性、表示、预算 | [01](01-isolation-and-loading.md)、[02](02-budget-and-tool-results.md) | 组成表、来源字段、预算公式 |
| 上下文模型：组成 | 指令、状态、历史、工具、证据、环境与多模态占用 | [01：上下文组成](01-isolation-and-loading.md) | `builder.py` 的完整 request |
| 上下文模型：三个维度 | 信任与来源、优先级与相关性、原文与派生内容 | [01：来源、优先级与表示](01-isolation-and-loading.md) | trust、data_only、来源哈希 |
| 上下文模型：生命周期 | 路径、读取请求、观察、本轮输入、回读 | [01：生命周期](01-isolation-and-loading.md) | 消息时序表与循环图 |
| 上下文模型：容量 | 字符、字节、token、协议及输出预留 | [02：计数与预算](02-budget-and-tool-results.md) | `measure`、完整请求计数 |
| 上下文模型：质量 | 相关性、时效、可信度、具体性、信息价值 | [01](01-isolation-and-loading.md)、[06](06-optimization-strategies.md) | 服务、版本和范围过滤 |
| 上下文模型：分段读取 | 原行号、next_start、单次范围与完整性 | [02](02-budget-and-tool-results.md)、[06：回读](06-optimization-strategies.md) | `crop_tool_result`、`read_back` |
| 上下文模型：冲突 | 版本比较、同版本矛盾、用户更正与旧偏好 | [03](03-history-compression.md)、[05：冲突](05-failure-modes.md) | e10、conflicting-policy、UNKNOWN |
| 上下文模型：消息不变量 | 完整动作组、最新要求、待办、停止条件 | [02：完整工具交互](02-budget-and-tool-results.md) | `trim_action_groups`、完整性测试 |
| 上下文模型：隔离 | 对象独立、信息选择、证据交接与权限区别 | [01：上下文隔离](01-isolation-and-loading.md) | `isolate_worker` 与污染反例 |
| 上下文模型：状态失真 | 失败不变成功、假设不变事实、否定与条件 | [03：失败、假设与待办](03-history-compression.md) | `scoped_summary`、s3 与 s6 |
| 失败模式 | Poisoning、Distraction、Confusion、Clash | [05](05-failure-modes.md) | 对应真实 fixture 与最小反例 |
| 失败模式 | Rot 与 Overflow，腐化不等于事实过期 | [05](05-failure-modes.md)、[07](07-evaluation-and-regression.md) | 预算失败、真实模型位置探针 |
| 失败模式 | Leakage 与 Injection，信任与动作授权 | [05](05-failure-modes.md) | beta 标记、外部笔记、权限章链接 |
| 失败模式：排障 | 首次偏离、实际输入、最小复现、回归 | [05：排障顺序](05-failure-modes.md) | request、envelope、故障清单 |
| Builder：职责与适用 | 多来源调用何时需要独立构建器 | [01](01-isolation-and-loading.md)、[04](04-experiments-and-source.md) | 简单组装到 `build_context` |
| Builder：输入契约 | 请求、状态、候选、工具与预算 | [04：构建器输入](04-experiments-and-source.md) | engineering/task、index、TOOLS |
| Builder：流水线 | 读取前授权、范围过滤、去重、排序、转换、预算、覆盖 | [04：构建顺序](04-experiments-and-source.md) | `select_documents`、`build_context` |
| Builder：输出契约 | messages、selected、dropped、transformations、budget、warnings | [04：请求与构建记录](04-experiments-and-source.md) | current/envelope.json |
| Builder：分工 | 确定性校验与模型语义判断的职责 | [04](04-experiments-and-source.md) | 字段校验、live_compress 入口 |
| Builder：预算模型 | 输出、协议、必需项、下一轮余量、贪心反例 | [02：证据选择](02-budget-and-tool-results.md) | 500 额度算例、A/B/C 反例 |
| Builder：测试与代价 | 超限、版本、来源、重放、越权、冲突与维护成本 | [04](04-experiments-and-source.md)、[07](07-evaluation-and-regression.md) | `test_engineering.py` |
| 优化：Select | 权限独立于软相关性，先筛选再压缩 | [06：选择与检索](06-optimization-strategies.md) | select_documents |
| 优化：Retrieve | 数据库、关键词、向量、依赖、代码、工具与记忆 | [06：选择与检索](06-optimization-strategies.md) | 检索方式表、按需加载与回读 |
| 优化：Reorder | 按职责组织，不把首尾优势当通用规律 | [06](06-optimization-strategies.md)、[07](07-evaluation-and-regression.md) | head/middle/tail 探针 |
| 优化：Compress | 去重、解析、抽取、摘要、递归摘要与不宜压缩的情况 | [03](03-history-compression.md)、[06](06-optimization-strategies.md) | 事实、条件、来源与待办检查 |
| 优化：Isolate | 适用条件、交接代价、函数/工作流/子 Agent | [01](01-isolation-and-loading.md)、[06](06-optimization-strategies.md) | 独立消息与父上下文检查 |
| 优化：Offload | 状态、日志、代码、证据卸载，原子写、版本、并发 | [06：外部卸载与回读](06-optimization-strategies.md) | offload、read_back、状态管理衔接 |
| 优化：Cache | 前缀、响应、工具三种缓存；失效与费用口径 | [06：缓存类型](06-optimization-strategies.md) | cache_identity、当前官方文档 |
| 优化：Refresh | 版本变化、过期、冲突触发，失败时未知 | [06：事实刷新](06-optimization-strategies.md) | refresh_policy、v4 缺失反例 |
| 评测：任务集 | 事实、噪声、冲突、长对话、工具、恢复、注入、预算 | [07：任务集](07-evaluation-and-regression.md) | fault-cases.json、tests |
| 评测：指标 | 任务、约束、事实、引用、召回、精确率、冲突、来源、稳定性 | [07：指标分层](07-evaluation-and-regression.md) | evidence_metrics、grade 与报告 |
| 评测：统计边界 | 空集合、统一证据 ID、证据入窗与使用分开 | [07：证据指标](07-evaluation-and-regression.md) | None、别名归并与单元测试 |
| 评测：基线消融 | Full、Minimal、Current、单项变化、多次 Trial | [07：基线与消融](07-evaluation-and-regression.md) | 五组实际请求、36 项模型探针配置 |
| 评测：Trace | 版本、候选、选择、转换、模型、usage、动作、grader、脱敏 | [07：Trace 与失败归因](07-evaluation-and-regression.md) | envelope、逐次 request/response/grade |
| 评测：归因 | Source/Retrieval/Selection/Transformation/Packing/Reasoning/Action/Grader | [07：失败归因](07-evaluation-and-regression.md) | 分层定位表 |
| 评测：效率与门禁 | 延迟、缓存、费用、成功任务成本、硬门禁与质量回归 | [07：成本与回归](07-evaluation-and-regression.md) | usage、耗时、计划与通过分母 |
| 预算 Notebook | 权限过滤、硬约束保护、输出预留、截断对照 | [02](02-budget-and-tool-results.md)、[04](04-experiments-and-source.md) | overflow、foreign_body、五组请求 |
| 压缩 Notebook | 最新失败、否定约束、待办、来源与原事件保留 | [03](03-history-compression.md)、[05](05-failure-modes.md) | 新资料下 1/3 → 3/3，来源 s3 |
| references | 一手来源、工程经验、社区入口、证据等级与不外推数字 | [参考资料](references.md) | 原索引保留，核心来源重新核对 |

旧 Notebook 的字节数字与本章 token 数口径不同，不直接比较比例。位置效应和模型抵抗注入的代码已提供；是否已执行以 [README 验证记录](README.md) 为准。
