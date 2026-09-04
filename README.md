# TheBestAIGuide

面向个人学习与工程实践的 AI 与 AI Agent 知识库。内容按知识领域组织，每个领域把概念、模式、案例、实验和配套代码放在同一条学习路径中。

当前不收录求职、面试、简历、薪酬和培训交付内容。

## 从这里开始

1. 阅读[知识库首页](00-Home/README.md)，了解使用方式和当前状态。
2. 按[连续学习路线](00-Home/Learning-Paths.md)从基础知识逐步进入 Agent 系统。
3. 通过[完整知识地图](00-Home/Knowledge-Map.md)查找尚未拆成独立文章的知识点。
4. 进入[`10-Knowledge`](10-Knowledge/README.md)，在一个领域内依次学习概念、模式、案例、实验和代码。

## 当前可以连续阅读的专题

| 专题 | 学习链路 | 状态 |
| --- | --- | --- |
| [Context Engineering](10-Knowledge/04-context-engineering/README.md) | 原理 → Context Builder → 优化 → 评测 → Notebook | draft |
| [RAG 与知识系统](10-Knowledge/06-rag-and-knowledge-systems/README.md) | 流程 → 混合检索 → 模式 → 运维案例 → 实验/代码 | draft |
| [Evaluation 与 Observability](10-Knowledge/10-evaluation-observability/README.md) | 对象 → 数据集 → Grader → 统计 → Trace → 运营 | draft |
| [AgentGuide 参考案例](00-Home/reference-cases/AgentGuide/repository-walkthrough.md) | 仓库走读 → 内容取舍 → 知识库映射 | reviewed snapshot |

`draft` 表示已有结构化正文，但不代表配套实验或代码已经运行。

## 目录结构

| 目录 | 职责 |
| --- | --- |
| `00-Home/` | 全局入口、知识地图、学习路线、范围、规范和建设状态 |
| `10-Knowledge/` | 按知识领域组织概念、模式、案例、实验和主题代码 |
| `20-Projects/` | 跨越多个知识领域的完整工程项目 |
| `90-Sources/` | 论文、官方文档、标准、数据集和代码仓来源 |
| `99-Inbox/` | 尚未消化、验证或归类的输入材料 |
| `assets/` | 文档引用的图片和图表 |
| `scripts/` | 链接、Markdown、Notebook 等仓库维护工具 |

## 组织原则

```text
Sources / Inbox
       ↓ 整理与核验
Knowledge Domain
       ↓
Concepts → Patterns → Cases → Labs → Code
                                  ↓
                      Cross-domain Projects
```

- 一个知识点只保留一份正式定义，其余位置使用链接。
- 主题入口负责给出前置知识、阅读顺序和当前证据边界。
- Notebook 保存实验过程、输入、输出和结论；可复用逻辑进入源码工程。
- 案例参数、架构方案、空 Notebook 和代码骨架不能当作已验证结果。

内容状态和下一步建设顺序见[知识库建设状态](00-Home/Knowledge-Status.md)与[待补充计划](00-Home/待补充计划.md)。
