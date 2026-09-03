# TheBestAIGuide

面向个人学习与工程实践的 AI 与 AI Agent 知识库。

仓库以 Markdown 保存知识结论，以 Jupyter Notebook 保存可复现实验，以 Python/TypeScript 工程保存可复用实现。当前不纳入求职、面试、简历、薪酬和培训交付内容。

## 从这里开始

- [开始阅读](00-Home/Start-Here.md)
- [知识体系总纲](10-Maps/00-Master-Map.md)
- [AI 基础知识地图](10-Maps/01-AI-Foundations-Map.md)
- [Agent 系统知识地图](10-Maps/03-Agent-Systems-Map.md)
- [知识库建设状态](00-Home/Knowledge-Status.md)
- [待补充计划](00-Home/待补充计划.md)

## 当前已有正文

| 主题 | 内容 | 状态 |
| --- | --- | --- |
| Context Engineering | [概念、Builder、失败模式、优化和评测](20-Knowledge/04-context-engineering/README.md) | draft |
| RAG | [端到端流程、混合检索与重排](20-Knowledge/06-rag-and-knowledge-systems/README.md) | draft |
| Agent Evaluation | [任务、Trial、Grader、统计、Trace 和发布门禁](20-Knowledge/10-evaluation-observability/README.md) | draft |
| Multi-Agent Evaluation | [路由、交接、共享状态、协作和成本](20-Knowledge/10-evaluation-observability/Multi-Agent-Evaluation-Guide.md) | draft |
| 运维 RAG | [系统设计与双索引决策](40-Cases/rag-systems/README.md) | draft / design case |
| AgentGuide | [固定提交的代码仓走读与知识提炼](40-Cases/external-repositories/AgentGuide/repository-walkthrough.md) | reviewed snapshot |

这里的 `draft` 表示已有结构化正文，但不代表配套实验和实现已运行。

## 目录分工

| 目录 | 用途 |
| --- | --- |
| `00-Home/` | 入口、范围、规范、状态和建设计划 |
| `10-Maps/` | 知识地图、依赖关系和阅读路径 |
| `20-Knowledge/` | 概念、原理、机制和知识结论 |
| `30-Patterns/` | 可复用设计模式、工程取舍和反模式 |
| `40-Cases/` | 系统案例、仓库走读和失败复盘 |
| `50-Labs/` | 可逐步运行和验证的 Jupyter 实验 |
| `60-Code/` | 可复用、可测试的 Python/TypeScript 工程 |
| `90-Sources/` | 论文、官方文档、标准和代码仓来源 |
| `99-Inbox/` | 尚未消化、验证或归类的材料 |
| `assets/` | 文档引用的图片和图表 |

## 内容流转

```text
Sources / Inbox
      ↓ 整理与核验
Knowledge ──> Maps
      ↓ 提炼      ↓ 导航
Patterns / Cases
      ↓ 验证
Labs / Code
```

每个知识点只保留一份正式定义。地图负责导航，模式说明可复用取舍，案例保留具体约束，实验与代码负责验证。

## 状态约定

- `seed`：只有主题边界或占位。
- `draft`：已有正文，但尚未完成来源或实验验证。
- `reviewed`：结构、事实和来源已审查。
- `verified`：相关代码或实验已实际运行并记录结果。

占位目录、代码片段、架构设计和构建成功都不自动等于功能或效果已经验证。
