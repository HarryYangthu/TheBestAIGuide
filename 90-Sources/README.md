# 来源：遇到问题时，知道去哪里核对

这里维护跨领域的精选入口。先读知识正文，遇到公式、接口行为或实验结论需要核对时，再查来源。与某个知识点直接对应的证据保存在该领域的 `references.md`；本目录负责分类，不重复定义知识点。

本轮核验日期：2026-09-06。已读取所列官方页面、论文摘要与版本记录、固定提交的仓库 README；未因此宣称复现论文或运行外部工程。具体阅读范围和限制写在各分类页。

| 你要核对什么 | 入口 | 应该带回什么 |
| --- | --- | --- |
| 一个方法最初解决什么问题 | [论文](papers/README.md) | 方法适用条件、对照实验、原始版本 |
| 一个 API 的参数到底怎么用 | [官方文档](official-docs/README.md) | 输入输出、异常、版本差异 |
| 协议要求什么、哪些只是建议 | [标准与协议](standards/README.md) | 固定修订、必需行为、实现边界 |
| 怎样客观比较两个系统 | [数据集与评测基准](datasets-and-benchmarks/README.md) | 任务、切分、判分器、运行条件 |
| 基础不牢，应该补哪部分 | [教材与课程](books-and-courses/README.md) | 指定章节、前置知识、练习路线 |
| 正式实现如何组织 | [代码仓](repositories/README.md) | 固定提交、阅读入口、复现限制 |

## 按学习主题找证据

| 基础与模型 | Agent 系统 | 应用与运行 |
| --- | --- | --- |
| [AI 基础](../10-Knowledge/01-ai-foundations/references.md) | [Agent Core](../10-Knowledge/03-agent-core/references.md) | [评测与可观测性](../10-Knowledge/10-evaluation-observability/references.md) |
| [基础模型](../10-Knowledge/02-foundation-models/references.md) | [上下文工程](../10-Knowledge/04-context-engineering/references.md) | [安全与治理](../10-Knowledge/11-safety-security-governance/references.md) |
| [检索与知识系统](../10-Knowledge/06-rag-and-knowledge-systems/references.md) | [工具、Skill 与协议](../10-Knowledge/05-tools-skills-protocols/references.md) | [应用工程](../10-Knowledge/13-application-engineering/references.md) |
| [Agent 学习](../10-Knowledge/12-agent-learning/references.md) | [状态与记忆](../10-Knowledge/07-state-and-memory/references.md) | [生产工程](../10-Knowledge/14-production-engineering/references.md) |
| [研究前沿](../10-Knowledge/16-research-frontiers/references.md) | [规划、工作流与多 Agent](../10-Knowledge/08-planning-workflow-multi-agent/references.md) | [多模态与具身](../10-Knowledge/15-multimodal-and-embodied/references.md) |
| | [运行时与 Harness](../10-Knowledge/09-runtime-harness-environment/references.md) | |

新增来源时使用 [来源卡模板](../00-Home/templates/source.md)。如何区分“打开过页面”“读过方法”和“实际复现”，见 [来源记录说明](source-notes/README.md)。
