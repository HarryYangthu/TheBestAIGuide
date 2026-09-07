# 虚拟项目与学习工程总表

**第一次学习 Agent，先做 [项目 00：Mini Agent](00-mini-agent/README.md)。** 它提供七步代码、使用教程、参考清单和一键验收；跑完后能直接检查自己是否完成。

从这里可以找到完整工程，也能看清哪些只是解释单一机制的算例。代码保持原目录，通过链接统一导航，避免打断 Notebook 导入。

| 类型 | 项目 | 任务与输入输出 | 运行和验收入口 |
| --- | --- | --- | --- |
| 入门项目 00 | [Mini Agent：从一个循环写起](00-mini-agent/README.md) | 对比资料→升级清单；逐步加入上下文、记忆、计划、并发与 Harness | README 一键运行；reference 参考报告；completion 总验收 |
| 组件 | [工具调用循环](../10-Knowledge/03-agent-core/05-code/agent-loop-python/README.md) | 输入任务→State/Trace；限步、错误、工具结果 | 项目 README 的命令与测试 |
| 组件 | [工具契约与授权](../10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/README.md) | 完整 ToolCall、参数校验、调用去重 | 项目 README 的命令与测试 |
| 组件 | [MCP 工具服务](../10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript/README.md) | stdio 客户端/服务端；固定 SDK | 项目 README 的命令与测试 |
| 组件 | [本地资料检索](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/README.md) | 文档→召回/排序/引用；默认词项检索 | 项目 README 的命令与测试 |
| 组件 | [版本化记忆存储](../10-Knowledge/07-state-and-memory/05-code/state-memory-python/README.md) | SQLite；主体、TTL、删除、CAS | 项目 README 的命令与测试 |
| 组件 | [并行任务调度](../10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/README.md) | 任务→结果；限并发、取消、确定性合并 | 项目 README 的命令与测试 |
| 组件 | [任务故障恢复](../10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python/README.md) | 事件、checkpoint、恢复与幂等 | 项目 README 的命令与测试 |
| 组件 | [任务评测](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/README.md) | JSONL→Trial/聚合；确定性评分 | 项目 README 的命令与测试 |
| 组件 | [浏览器动作与恢复](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/README.md) | 本地网页→动作；真实 Chromium，固定站点边界 | 项目 README 的命令与测试 |
| 综合/学习项目 | [领域资料研究助手](domain-research-agent/README.md) | 综合离线任务：检索→引用→记忆/事件→故障恢复 | README、tests 和 artifacts；真实结果及限制单列 |
| 综合/学习项目 | [Agent 学习工作台](learning-workbench/README.md) | Run API/网页、真实模型适配、两工具任务、生成式 RAG、跨会话记忆、文献角色比较、修复、PDF、队列与科研实验 | README、tests 和 artifacts；真实结果及限制单列 |
| 综合/学习项目 | [小型 Transformer](tiny-transformer/README.md) | 字符→多头因果 Attention→训练→生成；SFT/LoRA/DPO、缓存与权重重载 | README、tests 和 artifacts；真实结果及限制单列 |

## 章节机制算例

这些入口有可执行代码，但不单独包装成完整应用。企业、运维和科研旧案例仍是局部函数；其中科研已扩展出学习工作台的完整 CPU 对照任务。

| 算例 | 任务类型 | 代码入口 |
| --- | --- | --- |
| 搜索、RL、数值基础 | 机制实验或局部算例 | [01-ai-foundations](../10-Knowledge/01-ai-foundations/README.md) |
| 分词、Attention、推理与训练数值 | 机制实验或局部算例 | [02-foundation-models](../10-Knowledge/02-foundation-models/README.md) |
| 上下文预算与事件提取 | 机制实验或局部算例 | [04-context-engineering](../10-Knowledge/04-context-engineering/README.md) |
| 权限策略与注入执行边界 | 机制实验或局部算例 | [11-safety-security-governance](../10-Knowledge/11-safety-security-governance/README.md) |
| 学习数据与目标函数 | 机制实验或局部算例 | [12-agent-learning](../10-Knowledge/12-agent-learning/README.md) |
| 企业/运维/科研局部函数 | 机制实验或局部算例 | [13-application-engineering](../10-Knowledge/13-application-engineering/README.md) |
| 成本、容量与幂等算例 | 机制实验或局部算例 | [14-production-engineering](../10-Knowledge/14-production-engineering/README.md) |
| 结构证据与引用 | 机制实验或局部算例 | [15-multimodal-and-embodied](../10-Knowledge/15-multimodal-and-embodied/README.md) |
| 研究假设与资源约束 | 机制实验或局部算例 | [16-research-frontiers](../10-Knowledge/16-research-frontiers/README.md) |

建议学习顺序：Mini Agent 项目 00 → Agent Loop → Tools → RAG → Memory → 学习工作台。关注模型底层时走 Tokenization → Attention → Tiny Transformer。所有完成范围与未声称的能力见[本轮记录](../00-Home/Round2-Completion.md)。
