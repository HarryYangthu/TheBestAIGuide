# 上下文工程参考资料

本章正文、输入和本地实验覆盖表见 [README](README.md) 与 [coverage.md](coverage.md)。以下区分研究结果、作者工程经验、本地实验和延伸阅读。

## 核心来源

| 来源 | 支撑内容 | 使用方式 |
|---|---|---|
| [Anthropic：Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 每轮管理输入，长任务的压缩、状态保存与隔离 | 采用机制动机，不移植厂商效果数字 |
| [LangChain：Context engineering for agents](https://www.langchain.com/blog/context-engineering-for-agents) | Write、Select、Compress、Isolate 分类 | 与本文八项具体操作对照，不依赖其框架 API |
| [Lost in the Middle v3](https://arxiv.org/abs/2307.03172v3) | 所测试任务和模型中的位置效应 | 作为位置探针的依据，重新测当前模型 |
| [Manus：Context Engineering for AI Agents](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) | 文件卸载、错误保留、前缀组织 | 对照本文回读与缓存失效，不继承未公开环境的数据 |
| [OpenAI：Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) | 渲染前缀匹配、缓存配置与 usage 口径 | 具体行为按所用模型及接口核对 |
| [tiktoken 0.12.0](https://github.com/openai/tiktoken/tree/0.12.0) | 本地编码计数的真实实现 | 本章保留固定版本源码、许可证与哈希 |

表中的官方文章与论文已在本轮补充时打开核对；tiktoken 复用已固定版本的源码快照，并重新执行哈希检查。本地实验使用自带模拟资料，结果保存在 `reports/engineering/`；其数值不来自上表的论文或厂商基准。

## 延伸阅读

归档版以下入口继续保留，覆盖研究全景、编排边界、工具决策及社区方法；它们不构成本次已运行模型实验的证据。

| 来源 | 阅读主题 |
|---|---|
| [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | Workflow 与 Agent 的组合边界 |
| [Anthropic：Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | 隔离、交接与并行研究的取舍 |
| [Anthropic：The think tool](https://www.anthropic.com/engineering/claude-think-tool) | 工具流程中的显式决策步骤，不等于获取隐藏思维链 |
| [A Survey of Context Engineering](https://arxiv.org/abs/2507.13334) | 研究分类；具体结论回到原论文 |
| [LangChain 配套代码](https://github.com/langchain-ai/how_to_fix_your_context) | 检索、筛选、修剪、摘要和卸载；运行前锁定版本 |
| [Drew Breunig：How Contexts Fail](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html) | 失败排障名称的社区来源，不是固定分类标准 |
| [12 Factor Agents](https://github.com/humanlayer/12-factor-agents) | 控制上下文与确定性流程 |
| [Philipp Schmid：Context Engineering](https://www.philschmid.de/context-engineering) | 概念入口 |
| [中文上下文工程导航](https://github.com/phodal/build-agent-context-engineering) | 实践资料发现 |
| [Awesome Context Engineering](https://github.com/Meirtz/Awesome-Context-Engineering) | 论文与资源发现 |

## 证据使用

工程经验可用于提出方案，实验结果需要同时记录任务、模型、输入、策略、计数与运行条件。压缩比例、窗口分配比例、缓存节省比例和子 Agent 数量没有统一的最优值，不从个案直接推导通用推荐。

原始资源分级和历史核验记录保存在[归档 references](../../_archive/04-context-engineering/references.md)。正文采用短概念标题与实际输入输出，重要结论回到一手资料或本地可核对记录。
