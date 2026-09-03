# Agent 系统知识地图

> 状态：draft
> 目标：从一个最小 Agent Loop 出发，逐层理解上下文、工具、状态、工作流、运行时、评测与安全之间的关系。

## 先建立系统边界

Agent 不是“模型加一段 Prompt”，而是一个能够在环境中循环决策和行动的系统：

```text
目标与约束
   ↓
Context Builder ──> Model Policy ──> Action / Tool Call
      ↑                                  │
      ├──────── Observation ─────────────┤
      └──────── State / Memory ──────────┘
                         │
                         └─> Harness：权限、重试、恢复、Trace、预算
```

模型只负责其中一部分决策。系统能否可靠完成任务，还取决于输入信息、工具契约、环境状态、执行控制和验收方式。

## 知识主线

| 层 | 需要回答的问题 | 当前入口 | 状态 |
| --- | --- | --- | --- |
| Agent Core | 一轮感知、决策、行动、反馈如何闭环？ | [Agent Core](../20-Knowledge/03-agent-core/README.md) | seed |
| Context | 下一步决策需要哪些信息，如何选择和压缩？ | [Context Engineering](../20-Knowledge/04-context-engineering/README.md) | draft |
| Tools 与协议 | 模型如何表达动作，系统如何校验和执行？ | [Tools、Skills 与协议](../20-Knowledge/05-tools-skills-protocols/README.md) | seed |
| RAG | 外部知识如何被解析、检索、重排和引用？ | [RAG 与知识系统](../20-Knowledge/06-rag-and-knowledge-systems/README.md) | draft |
| Memory 与 State | 什么应进入当前状态，什么应跨会话保存？ | [Memory 与状态](../20-Knowledge/07-memory-and-state/README.md) | seed |
| Planning 与 Multi-Agent | 任务如何分解、路由、交接与合并？ | [Planning、Workflow 与 Multi-Agent](../20-Knowledge/08-planning-workflow-multi-agent/README.md) | draft |
| Runtime 与 Harness | 如何控制循环、超时、重试、恢复和副作用？ | [Runtime 与 Harness](../20-Knowledge/09-runtime-harness-environment/README.md) | seed |
| Evaluation | 如何证明结果正确、过程稳定且成本可控？ | [Evaluation 与 Observability](../20-Knowledge/10-evaluation-observability/README.md) | draft |
| Safety | 谁能做什么，危险动作如何限制和审计？ | [Safety、Security 与 Governance](../20-Knowledge/11-safety-security-governance/README.md) | seed |
| Application | 系统如何接入 UI、服务、存储和模型路由？ | [应用工程](../20-Knowledge/13-application-engineering/README.md) | seed |

## 建议理解顺序

### 1. 最小闭环

先掌握这些最小概念：

1. `goal`：要达到的结果与不可违反的约束。
2. `observation`：模型本轮可以看到的信息。
3. `action`：回复、工具调用、委托或停止。
4. `state`：任务在多轮之间延续的事实。
5. `termination`：成功、失败、超时或需要人工决策。

最小实现入口：[Python Agent Loop 骨架](../60-Code/agent-loop-python/README.md)。该工程目前仍是占位，不能视为已验证实现。

### 2. 信息面：Context、RAG 与 Memory

这三个概念容易混淆：

| 概念 | 核心职责 | 典型时间尺度 |
| --- | --- | --- |
| Context | 组装“这一轮”交给模型的有效输入 | 单次模型调用 |
| RAG | 从外部知识源检索与当前问题相关的证据 | 查询时 |
| Memory | 选择、保存和读取跨轮次或跨会话状态 | 多轮到长期 |

统一入口：[Context、RAG 与 Memory 地图](04-Context-RAG-Memory-Map.md)。

### 3. 行动面：Tools、Environment 与 Harness

可靠工具调用至少需要：

- 明确的输入、输出与错误 Schema；
- 参数校验、权限边界和幂等策略；
- 超时、重试、取消与补偿；
- 可隔离、可重放的执行环境；
- 工具调用和环境变化的 Trace。

入口：[Tools 与协议地图](05-Tools-Protocols-Map.md) 和 [Runtime 与 Harness 地图](06-Runtime-Harness-Map.md)。

### 4. 编排面：Workflow 与 Multi-Agent

先判断一个确定性工作流能否解决问题，再决定是否引入模型路由或多个 Agent。多 Agent 不是默认升级路径，它增加了：

- 路由与交接错误；
- 状态同步和上下文隔离成本；
- 重复调用与冲突输出；
- 更复杂的归因和评测。

当角色具备清晰边界、上下文确实需要隔离，或工作能够并行时，多 Agent 才可能值得采用。

### 5. 验证面：Evaluation、Observability 与 Safety

系统评测至少同时观察：

- `Outcome`：最终环境状态是否满足成功条件；
- `Trajectory`：是否出现越权、无效循环或错误传播；
- `Reliability`：多次运行是否稳定；
- `Efficiency`：延迟、Token、调用次数和成本；
- `Safety`：权限、数据和外部副作用是否受控。

入口：[Evaluation 与 Observability 地图](07-Evaluation-Observability-Map.md) 和 [Safety 与 Governance 地图](08-Safety-Governance-Map.md)。

## 当前已有内容

- Context Engineering 已从单篇长文拆为概念模型、Context Builder、失败模式、优化策略和评测笔记。
- Evaluation 已拆为评测模型、任务与试验、评分器、统计可靠性、Trace、Multi-Agent 和发布运营。
- RAG 已从两个运维案例中提炼出通用流程与混合检索模式。
- [AgentGuide 仓库走读](../40-Cases/external-repositories/AgentGuide/repository-walkthrough.md) 提供了一个“内容仓库如何转化为知识库”的案例。

这些内容当前均属于文档层 `draft`；未完成的 Notebook 和源码骨架不构成实验或工程验证。

## 后续补充顺序

1. 写出最小 Agent Loop 的正式知识笔记和可测试实现。
2. 补齐 Tool Schema、错误协议、权限与幂等。
3. 补齐 State、Checkpoint、Memory 写入和遗忘策略。
4. 补齐 Workflow、Planning、路由、交接和冲突处理。
5. 用同一组任务贯通 Trace、Eval、回放和发布门禁。
6. 最后再扩展 Browser、Computer Use、多 Agent 和长程自治。

完整覆盖范围见：[知识体系总纲](00-Master-Map.md)。
