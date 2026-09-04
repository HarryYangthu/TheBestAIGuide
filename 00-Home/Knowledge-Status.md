# 知识库建设状态

> 盘点日期：2026-09-04
> 状态只描述仓库内证据，不根据目录数量推断完成度。

| 模块 | 当前状态 | 已有内容 | 主要缺口 |
| --- | --- | --- | --- |
| AI 基础 | seed | 范围与知识地图 | 正式专题、练习和实验 |
| 基础模型 | seed | Tokenizer、Transformer、训练与推理大纲 | 独立笔记与实验 |
| Agent Core | seed | 总纲与最小工程入口 | Agent Loop 正文、实现和测试 |
| Context Engineering | draft | 领域内已串联总览、信息模型、失败模式、Builder、优化、评测、来源和 Notebook 入口 | Notebook 内容、框架版本验证和实测结果 |
| Tools 与协议 | seed | 总纲级覆盖 | Tool Schema、错误协议、权限、MCP 和实现 |
| RAG | draft | 领域内已串联端到端流程、混合检索、模式、两个运维案例、Lab 和代码入口 | 样例数据、标注集、Pipeline 和 Eval |
| State 与 Memory | seed | 概念边界、生命周期、四类模式入口和实验计划 | 独立专题、实现、冲突/遗忘和评测 |
| Workflow 与 Multi-Agent | draft | 适用边界与 Multi-Agent 评测 | 拓扑、路由、交接、共享状态和案例 |
| Runtime 与 Harness | seed | 七层模型与工程骨架入口 | 可运行 Runtime、恢复、回放和幂等测试 |
| Evaluation 与 Observability | draft | 领域内已串联系统模型、任务、评分器、统计、Trace、Multi-Agent、运营、模板、来源和工程入口 | Eval Harness、校准集和运行报告 |
| Safety 与 Governance | seed | 总纲级威胁与信任边界 | 威胁模型、策略、红队任务和治理流程 |
| Agent Learning | seed | 数据、SFT、偏好优化和 Agentic RL 大纲 | 正式专题和实验 |
| 应用与生产工程 | seed | 总纲级覆盖 | UI、API、存储、模型路由和部署实践 |
| 多模态与具身智能 | seed | 方向清单 | 视觉、语音、文档、Computer Use、VLA 基础 |
| Research Frontiers | seed | 方向清单 | 来源追踪、论文笔记和验证任务 |
| 主题 Labs | seed | Context 两个 Notebook 文件及多个领域的实验入口 | Notebook 内容、依赖、样例数据和执行记录 |
| 主题 Code | seed | Agent Loop、Tool Runtime 等领域代码骨架 | 源码、测试、锁文件和 CI |
| 综合 Projects | seed | 已定义准入边界，暂无符合条件的项目 | 首个跨领域、可运行、可测试的端到端工程 |

## 本版完成的内容整理

- 将顶层结构简化为 Home、Knowledge、Projects、Sources 和 Inbox，移除重复的 Maps/Patterns/Cases/Labs/Code 顶层分类。
- 按知识领域聚合概念、模式、案例、实验和代码，并重写全局与主题级学习路线。
- 将 Context、RAG、Evaluation 的已有内容整理成可连续阅读的主线。
- 将 Context Engineering 的 1319 行长文改为短总览，并拆成 5 篇专题和 1 个模式。
- 将 Evaluation 与 Multi-Agent 的两篇长文改写为 9 个职责清晰的入口。
- 从运维 RAG 案例提炼通用 RAG 流程与 Hybrid Retrieval 模式。
- 重写 AgentGuide 走读，删除求职细节，保留固定提交下的代码和证据边界。
- 删除虚构团队案例、无来源成本表和未经限定的性能数字。
- 保留旧主文件名作为入口，避免已有链接失效。

## 当前可验证与不可验证

已验证：仓库结构、内部 Markdown 链接、Notebook JSON 格式、固定 AgentGuide 提交的远端 HEAD，以及本次 Markdown 重构本身。

未验证：Context/RAG/Evaluation 策略的实验效果、Notebook 执行、Agent/RAG/Eval 工程运行、任何生产指标。

状态含义见[目录与写作规范](Conventions.md)。
