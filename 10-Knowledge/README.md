# 知识领域

本目录是知识库主体。内容先按知识领域聚合，再在领域内部按“概念 → 模式 → 案例 → 实验 → 代码”组织，避免学习同一主题时跨多个顶层目录跳转。

## 推荐顺序

| 阶段 | 知识领域 | 当前状态 |
| --- | --- | --- |
| 基础 | [AI 基础](01-ai-foundations/README.md) → [基础模型](02-foundation-models/README.md) | seed |
| 最小系统 | [Agent Core](03-agent-core/README.md) | seed |
| 信息与行动 | [Context](04-context-engineering/README.md) → [Tools](05-tools-skills-protocols/README.md) → [RAG](06-rag-and-knowledge-systems/README.md) → [Memory](07-memory-and-state/README.md) | Context/RAG draft，其余 seed |
| 编排与执行 | [Planning 与 Multi-Agent](08-planning-workflow-multi-agent/README.md) → [Runtime 与 Harness](09-runtime-harness-environment/README.md) | seed/draft |
| 验证与治理 | [Evaluation](10-evaluation-observability/README.md) → [Safety](11-safety-security-governance/README.md) | Evaluation draft，Safety seed |
| 改进与产品化 | [Agent Learning](12-agent-learning/README.md) → [应用工程](13-application-engineering/README.md) → [生产工程](14-production-engineering/README.md) | seed |
| 扩展 | [多模态与具身智能](15-multimodal-and-embodied/README.md) → [研究前沿](16-research-frontiers/README.md) | seed |

完整路线见[连续学习路线](../00-Home/Learning-Paths.md)，尚未拆成独立文章的知识点见[完整知识地图](../00-Home/Knowledge-Map.md)。

## 领域内部约定

- `README.md`：唯一局部入口，说明前置知识、阅读顺序、已有内容和缺口。
- `01-concepts/`：定义、机制、边界和失败模式。
- `02-patterns/`：可复用方案、适用条件、工程取舍和反模式。
- `03-cases/`：具体系统、代码仓和失败复盘。
- `04-labs/`：可运行实验及其输入、输出和结论。
- `05-code/`：与该领域直接配套的可测试实现。
- `references.md`：本领域来源、版本和证据边界。

只有存在实际内容时才建立对应子目录；空骨架不算知识覆盖。
