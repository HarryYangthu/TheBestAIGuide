# 知识领域

按领域聚合概念、模式、案例、Notebook 和源码。每一行的 README 给出具体阅读顺序；详细执行记录见[建设状态](../00-Home/Knowledge-Status.md)。

| 顺序 | 领域 | 本轮学习重点 |
| --- | --- | --- |
| 1 | [AI 基础](01-ai-foundations/README.md) | 补齐数学统计、ML、DL、搜索规划、RL、可信 AI、计算基础；配四个小实验 |
| 2 | [基础模型](02-foundation-models/README.md) | 补齐 Tokenizer、Transformer、训练对齐、推理、推理模型、选型；配输入/注意力与解码/缓存实验 |
| 3 | [Agent Core](03-agent-core/README.md) | 完成边界、Loop、停止与错误处理、ReAct/Plan-and-Execute；实现最小 Python Agent |
| 4 | [Context Engineering](04-context-engineering/README.md) | 保留六篇正文，核对论据并补贯穿案例；实现预算与压缩实验 |
| 5 | [Tools / Skills / MCP](05-tools-skills-protocols/README.md) | 完成工具契约、Skills、MCP、Agent 协议和授权；实现 TypeScript Runtime、MCP Server 与共享 Schema |
| 6 | [RAG](06-rag-and-knowledge-systems/README.md) | 完善已有案例；补解析、切块、索引更新、查询/图检索和引用；建立语料、标注集、Pipeline、消融实验 |
| 7 | [State / Memory](07-state-and-memory/README.md) | 补状态事务、Checkpoint、记忆生命周期、冲突遗忘与评测；实现存储与恢复实验 |
| 8 | [Planning / Workflow / Multi-Agent](08-planning-workflow-multi-agent/README.md) | 补规划、状态图、协作拓扑、交接合并；实现协作 Runtime 与单 Agent 基线 |
| 9 | [Runtime / Harness](09-runtime-harness-environment/README.md) | 补运行生命周期、持久执行、并发预算、环境与 Harness 职责；验证恢复/回放/幂等 |
| 10 | [Evaluation / Observability](10-evaluation-observability/README.md) | 保留正文，增加手算与可运行评分；构造任务/校准数据、Harness、Trace、回归报告 |
| 11 | [Safety / Security / Governance](11-safety-security-governance/README.md) | 完成威胁边界、授权、数据与供应链；用本地任务验证越权拒绝及合法请求通过 |
| 12 | [Agent Learning](12-agent-learning/README.md) | 完成轨迹数据、SFT/偏好优化、Agentic RL、Verifier/奖励与反馈闭环；小规模可复现实验 |
| 13 | [应用工程](13-application-engineering/README.md) | 完成 API/流式事件/交互/存储/模型网关；补 Coding、Browser、企业、运维、科研案例与浏览器测试工程 |
| 14 | [生产工程](14-production-engineering/README.md) | 完成部署容量、SLO/成本、发布回滚；补有出处的系统分析与本地故障复盘 |
| 15 | [多模态与具身](15-multimodal-and-embodied/README.md) | 完成视觉文档、语音视频、多模态 RAG/上下文、VLA/具身；配文档结构与引用实验 |
| 16 | [研究前沿](16-research-frontiers/README.md) | 形成有日期和论文版本的长程、自进化、世界模型、神经符号、Test-time Learning、AI for Science 知识快照 |

## 领域内怎么找

- `01-concepts/`：定义、机制、公式与失败原因。
- `02-patterns/`：适用条件、设计步骤和代价。
- `03-cases/`：真实来源分析或明确标注的构造案例。
- `04-labs/`：输入、执行过程、中间量、结果和练习。
- `05-code/`：文章和实验复用的完整实现、样例与测试。
- `references.md`：一手来源、版本和证据范围。

[连续学习路线](../00-Home/Learning-Paths.md)按前置知识安排顺序，[综合项目](../20-Projects/domain-research-agent/README.md)展示组件如何一起运行。
