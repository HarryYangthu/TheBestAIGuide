# Context Engineering 资源索引

> 状态：draft
> 最近整理：2026-09-03
> 用途：记录来源类型、支持的结论和使用边界；正式知识见 [Context Engineering](../../20-Knowledge/04-context-engineering/README.md)。

## 核心一手资料

| 来源 | 类型 | 主要用途 | 使用边界 |
| --- | --- | --- | --- |
| [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 官方工程文章，2025-09-29 | 有效上下文、检索、长任务、压缩和子 Agent | 厂商经验，需要在自身模型与任务上验证 |
| [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | 官方工程文章，2024-12-19 | Workflow/Agent 边界、简单组合模式 | 主要描述 Anthropic 实践，不是协议标准 |
| [LangChain: Context engineering for agents](https://blog.langchain.com/context-engineering-for-agents/) | 框架作者文章 | Write、Select、Compress、Isolate 分类 | 分类可复用，示例 API 可能随框架变化 |
| [langchain-ai/how_to_fix_your_context](https://github.com/langchain-ai/how_to_fix_your_context) | 官方配套代码 | RAG、工具筛选、隔离、修剪、摘要、卸载示例 | 运行前锁定依赖并检查当前 API |
| [Lost in the Middle](https://arxiv.org/abs/2307.03172) | 论文 | 长上下文中信息位置与利用问题 | 结论受模型、任务和上下文长度约束 |
| [A Survey of Context Engineering for Large Language Models](https://arxiv.org/abs/2507.13334) | 综述论文 | 术语、方法分类和研究全景 | 综述覆盖广，具体结论需回到原论文 |

## 一手工程案例

| 来源 | 可提炼内容 | 不直接继承的内容 |
| --- | --- | --- |
| [Manus: Lessons from building Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) | 缓存友好前缀、文件系统卸载、工具选择和错误保留 | 未公开数据和环境下的效果数字 |
| [Anthropic: Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | 子任务上下文隔离、并行研究和协作取舍 | 不假设多 Agent 对所有任务都更好 |
| [Anthropic: The think tool](https://www.anthropic.com/engineering/claude-think-tool) | 在工具交互过程中显式增加决策步骤 | 不等同于获取或保存隐藏思维链 |

## 社区方法与二手资料

这些来源适合发现术语、模式和案例，但正式结论应回到论文、官方文档、源代码或本地实验：

- [Drew Breunig: How Long Contexts Fail](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html)：Poisoning、Distraction、Confusion、Clash 的诊断框架。
- [12 Factor Agents](https://github.com/humanlayer/12-factor-agents)：强调拥有 Context、确定性控制和小型 Agent 组合。
- [Philipp Schmid: Context Engineering](https://www.philschmid.de/context-engineering)：概念入口和上下文组成。
- [phodal/build-agent-context-engineering](https://github.com/phodal/build-agent-context-engineering)：中文工程实践导航。
- [Awesome Context Engineering](https://github.com/Meirtz/Awesome-Context-Engineering)：论文与资料发现入口。

## 资源使用矩阵

| 主题 | 优先来源 |
| --- | --- |
| 定义与系统边界 | Anthropic Effective Context、LangChain 分类 |
| 长上下文问题 | Lost in the Middle、具体模型评测 |
| 失败模式 | Drew Breunig 框架 + 本地失败 Trace |
| Context Builder | 官方工程文章 + 本仓设计与测试 |
| 压缩与卸载 | Anthropic、LangChain 代码、Manus 案例 |
| 多 Agent 隔离 | Anthropic Multi-Agent + 单 Agent 基线 |
| 缓存 | 模型供应商当前缓存文档 + 本地 Token/成本记录 |
| 安全与注入 | 模型供应商安全文档、威胁模型和本地对抗 Eval |

## 已删除或降级的结论

旧资源表中的以下写法不再作为正式知识保留：

- 没有任务、模型、数据和运行记录支撑的固定“性能提升”数字；
- 没有统一计费与缓存口径支撑的成本节省比例；
- “固定分钟粒度”“固定 Token 压缩比例”等通用最佳值；
- 根据 Star、篇幅或主观印象给代码质量打分；
- 将厂商个案直接写成所有 Agent 的普适规律。

这些内容如需恢复，必须记录原始来源、发布日期、实验设置和适用条件。

## 维护规则

- 先记录来源，再提炼知识结论；同一结论尽量有论文、官方文档或源代码支撑。
- 链接到框架代码时保存提交或版本，不只链接 `main`。
- 厂商性能数字保留原测量对象和限制，不跨模型、任务或价格版本外推。
- 博客中的模式可进入 `draft`，进入 `reviewed` 前需要交叉核对。
- 本地实验结果进入 Labs，并记录数据、版本、运行命令和原始输出。
