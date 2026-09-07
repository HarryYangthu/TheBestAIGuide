# 术语表

> 状态：draft
> 用途：统一本仓库中的中文名、英文名和概念边界；详细机制以对应专题为准。

| 术语 | 本仓库定义 | 不等同于 |
| --- | --- | --- |
| Agent | 模型在目标、工具、状态和环境约束下循环观察、决策、行动并终止的系统 | 单次模型调用或聊天界面 |
| Workflow | 由代码或配置明确规定步骤、分支和状态转换的执行流程 | 必须自主规划的 Agent |
| Agent Loop | `observe → decide → act → observe` 的最小迭代闭环 | 完整生产 Runtime |
| Agent Harness / Scaffold | 把模型接入循环、工具、状态和环境的脚手架 | 模型本身 |
| Runtime | 实际调度 Run/Step、执行工具、管理超时、重试、权限和恢复的运行层 | Prompt 编排 |
| Context | 一次模型调用实际可见的指令、请求、状态、历史、证据和工具信息 | 全部可访问数据 |
| Context Builder | 在模型调用前收集、过滤、选择、转换、排序、打包并校验上下文的组件 | 简单字符串拼接 |
| State | 当前任务的权威运行事实，例如步骤、结果、版本和待办 | 可模糊召回的长期 Memory |
| Memory | 跨步骤或跨会话保存、更新并按需读取的信息 | 完整对话历史或数据库本身 |
| Tool | Agent 可请求执行的有明确输入、输出、权限和错误契约的动作 | 任意自然语言能力描述 |
| Skill | 可复用的程序性知识、规则和工作流说明，可能协调多个工具 | 工具执行接口本身 |
| MCP | Model Context Protocol，用于 Host/Client 与 Server 发现和调用工具、资源等能力的协议 | 权限、安全或业务语义的自动保证 |
| RAG | 在生成前从外部知识源取得可追溯证据的系统链路 | 只做向量相似度搜索 |
| Retrieval | 从候选知识中召回与 Query 相关的项目 | 最终答案生成 |
| Rerank | 对较小候选集重新计算 Query—Evidence 顺序 | 权限过滤或事实验证 |
| Artifact | Run 产生并可独立引用、校验或交付的文件、数据或结构化结果 | 仅存在于聊天中的声明 |
| Eval Task | 包含输入、初始状态、约束、成功条件和评分配置的一项测试 | 一句 Prompt |
| Trial | 固定 Task 和系统配置的一次完整运行 | 聚合后的评测结果 |
| Trajectory / Transcript | Trial 中可观察的消息、工具调用、路由、中间结果和错误记录 | 必须包含隐藏思维链 |
| Outcome | Trial 结束后文件、数据库、UI 或外部系统的真实状态 | Agent 声称完成的文字 |
| Grader | 对 Outcome 或 Trajectory 某个维度进行检查和计分的逻辑或评审者 | 整个 Eval Harness |
| Evaluation Harness | 调度任务、隔离环境、采集轨迹、运行评分器并汇总结果的基础设施 | Agent Harness |
| Trace | 按 Run/Span/事件关联起来的可观测执行记录 | 无限制保存所有 Prompt 和敏感正文 |
| Verifier | 对候选结果、步骤或证明执行明确验证的组件 | 一定正确的模型 Judge |
| pass@k | 允许 `k` 个候选时至少一个成功的概率或相应估计 | 单次运行可靠性 |
| pass^k | 本仓用于讨论连续或成组 `k` 次全部成功的自定义稳定性记号，使用时必须给出定义 | 统一标准化指标 |

## 读公式与报告时常见的缩写

| 记号 | 怎样读 | 在本库哪里看完整机制 |
| --- | --- | --- |
| Token / Embedding | 分词后的单位 / 单位对应的数值向量；不是同一件事 | [分词](../10-Knowledge/02-foundation-models/01-concepts/tokenization/README.md) |
| Q、K、V | Attention 的查询、键、值向量；Q 在强化学习中还可能指动作价值，应按本篇定义读 | [Attention](../10-Knowledge/02-foundation-models/01-concepts/transformer/README.md) |
| Logit / Softmax | 未归一化分数 / 将一组分数转成和为 1 的权重或概率 | [模型与推理](../10-Knowledge/02-foundation-models/README.md) |
| SFT / LoRA / DPO | 示范监督微调 / 低秩参数更新 / 偏好对优化；分别描述目标或参数化方法，可以组合 | [训练机制](../10-Knowledge/02-foundation-models/01-concepts/training/README.md) |
| TTL / CAS | 有效期限 / 写入前比较版本是否仍匹配；CAS 不判断事实真假 | [记忆生命周期](../10-Knowledge/07-state-and-memory/01-concepts/02-memory-lifecycle.md) |
| DAG | 有向无环的依赖图；图中边表示先有哪个结果，后续任务才能做 | [规划与重规划](../10-Knowledge/08-planning-workflow-multi-agent/01-concepts/01-planning-and-replanning.md) |
| SLI / SLO / p95 | 实测服务指标 / 该指标的目标 / 第 95 百分位；必须说明单位、统计窗口与样本范围 | [可靠性与成本](../10-Knowledge/14-production-engineering/01-concepts/02-slos-reliability-and-cost.md) |
| fixture / baseline / ablation | 固定实验输入 / 对照方案 / 移除或改变一个组件的实验 | [任务与数据集](../10-Knowledge/10-evaluation-observability/01-concepts/02-tasks-datasets-and-trials.md) |

## 术语关系入口

- [Agent 系统学习路线](Learning-Paths.md)
- [Context Engineering 主题入口](../10-Knowledge/04-context-engineering/README.md)
- [Evaluation 与 Observability 主题入口](../10-Knowledge/10-evaluation-observability/README.md)

术语含义随标准或工具版本变化时，应在具体来源笔记中记录版本，而不是静默修改历史结论。
