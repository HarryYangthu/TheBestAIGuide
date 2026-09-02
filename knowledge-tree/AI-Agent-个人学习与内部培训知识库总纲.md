# AI Agent 个人学习与内部培训知识库总纲

> 目标：建立一套可持续维护、既能个人系统学习，也能直接拆成内部培训课程、实验和案例的 AI Agent 技术知识库。
> 参考来源：AgentGuide 的技术主线；按照本知识库目标重新组织，不照搬其目录结构。
> 当前版本：v0.1，2026-09-02

## 范围与定位

这套知识库只围绕四件事展开：

1. **原理讲清楚**：理解模型、Agent、RAG、Memory、Tools、Harness、Eval 的关键机制。
2. **系统做出来**：从最小 Agent Loop 逐步走到可运行、可恢复、可观测的系统。
3. **质量测得准**：所有重要能力都要有案例、指标、Trace 和失败分析。
4. **经验沉淀下来**：把项目经验转成模式、反模式、实验和可复用教学材料。

不纳入当前主线的内容：职业选择、招聘信息、公司题库、应聘话术、个人履历包装、薪酬与 HR 主题。

## 知识库的总骨架

```text
L0  大模型与软件基础
  ↓
L1  Agent 概念、Loop 与状态
  ↓
L2  Context、Tools、RAG 与 Memory
  ↓
L3  Workflow、Multi-Agent 与 Harness
  ↓
L4  Evaluation、Observability 与 Safety
  ↓
L5  应用工程、部署、可靠性与成本
  ↓
L6  数据合成、Post-training 与 Agentic RL
  ↓
L7  综合项目、案例复盘与研究前沿
```

这条主线同时服务两种使用方式：

- **个人学习**：按层级推进，每一层必须完成一个可验证产出。
- **内部培训**：按专题拆课，每节课由“概念 → 架构 → Demo → 实验 → 讨论”构成。

---

## 建议的知识库目录

当前文件可以先保持扁平结构，内容增长后再逐步迁移到下面的目录，不需要一次性重构。

```text
knowledge-tree/
├── 00-总览与导航/
│   ├── README.md
│   ├── 知识地图.md
│   ├── 学习路线.md
│   ├── 内部培训课程表.md
│   └── 术语表.md
│
├── 01-大模型基础/
├── 02-Agent核心范式/
├── 03-Context-Engineering/
├── 04-Tools与协议/
├── 05-RAG与知识系统/
├── 06-Memory与状态/
├── 07-Workflow与Multi-Agent/
├── 08-Agent-Harness与Runtime/
├── 09-Evaluation与Observability/
├── 10-Safety与治理/
├── 11-模型与数据优化/
├── 12-应用工程与部署/
├── 13-项目实验室/
├── 14-案例复盘/
├── 15-研究前沿/
│
├── 90-资源索引/
│   ├── 官方文档.md
│   ├── 论文索引.md
│   ├── 开源项目索引.md
│   └── 素材收集箱.md
│
└── 99-归档/
```

每个技术模块内部统一使用以下结构：

```text
模块名/
├── README.md          # 本模块地图、前置知识和推荐顺序
├── concepts/          # 概念卡和术语
├── architecture/      # 架构、机制和设计模式
├── implementation/    # 最小实现与工程实践
├── labs/              # 可运行实验
├── evaluation/        # 数据集、指标和评测脚本
├── cases/             # 真实案例与失败复盘
└── references/        # 一手资料索引
```

---

## 01. 大模型基础

### 01.1 Transformer 与注意力

- Token、Embedding 与位置编码。
- Self-Attention、Multi-Head Attention。
- FFN、Residual、Normalization。
- KV Cache 与自回归生成。
- GQA、MQA、稀疏注意力与线性注意力。
- MoE 的路由、专家负载和推理特点。

### 01.2 模型训练链路

- Pre-training 的目标和数据组织。
- SFT 与指令跟随。
- Reward Model 与偏好数据。
- RLHF、RLAIF、DPO、GRPO 的位置和关系。
- LoRA、QLoRA 与参数高效微调。
- 数据污染、过拟合和评测泄漏。

### 01.3 推理与模型使用

- Temperature、Top-p、Top-k 和采样稳定性。
- Structured Output 与 JSON Schema。
- Function Calling 的模型侧机制。
- 长上下文、Lost in the Middle 和上下文成本。
- 推理模型与普通生成模型的使用边界。
- 模型能力、延迟、成本和隐私的选型方法。

### 01.4 最小实验

- 比较不同采样参数的输出稳定性。
- 比较普通文本输出与 Schema 约束输出。
- 测量上下文长度对准确率、延迟和成本的影响。
- 实现一个最小模型 Provider Adapter。

---

## 02. Agent 核心范式

### 02.1 先分清系统边界

- Chatbot：主要生成回答。
- Workflow：按照确定流程执行。
- Agent：模型动态决定下一步动作。
- Multi-Agent：多个角色通过协议协同。
- Browser/Computer-Use Agent：进入真实软件环境执行动作。

### 02.2 Agent 的最小组成

- Goal：任务目标与成功标准。
- State：当前状态和已完成步骤。
- Context：本轮送入模型的信息。
- Tools：可调用能力及其边界。
- Policy/Model：下一步动作决策。
- Observation：环境或工具反馈。
- Loop：循环、停止和恢复机制。
- Guardrails：权限、预算和安全约束。
- Trace：全过程记录。
- Eval：完成质量判断。

### 02.3 最小 Agent Loop

```text
Task
  -> Build Context
  -> Model Decides Action
  -> Validate Action
  -> Execute Tool
  -> Observe Result
  -> Update State
  -> Continue / Stop / Ask Human
```

重点问题：

- 最大步数怎么定。
- 什么条件下结束。
- 工具不存在或参数错误怎么办。
- 工具超时、部分成功和限流怎么办。
- 什么时候允许重试。
- 什么时候必须请求人工确认。
- 如何避免重复动作和无限循环。

### 02.4 典型推理与控制模式

- ReAct。
- Plan-and-Execute。
- Router。
- Reflection/Self-Critique。
- Generator-Verifier。
- Tree/Graph Search。
- Delegation 与 Handoff。
- Human-in-the-loop。

### 02.5 最小实验

- 不依赖框架手写一个 50～150 行 Agent Loop。
- 只接两个低风险工具。
- 设置最大步数、预算和停止条件。
- 保存 JSONL Trace。
- 使用固定任务集做首次回归测试。

---

## 03. Context Engineering

### 03.1 上下文的组成

- System/Policy。
- 当前任务与成功标准。
- 用户输入。
- 当前状态与计划。
- 最近执行轨迹。
- 检索证据。
- 长期记忆。
- 工具描述。
- 输出格式约束。
- 剩余步数、Token 和成本预算。

### 03.2 Context Builder

- 不让业务代码到处拼 Prompt。
- 明确每一层信息的来源、优先级和生命周期。
- 对工具结果进行摘要、裁剪和引用保留。
- 将事实、指令、历史和不可信输入分区。
- 为子 Agent 构造独立上下文。
- 记录每次上下文构建的版本和摘要。

### 03.3 四类常见失效

- Context Poisoning：错误信息持续污染后续决策。
- Context Distraction：无关信息抢占注意力。
- Context Confusion：指令、证据和历史混在一起。
- Context Conflict：不同来源相互冲突。

### 03.4 主要优化策略

- Offload：把状态和大结果移到文件或数据库。
- Retrieve：只取当前任务需要的信息。
- Reduce：总结、裁剪、去重和结构化。
- Isolate：为工具、角色和子任务隔离上下文。
- Compaction：长任务中压缩历史但保留 lineage。
- Prompt Cache：稳定前缀、降低重复计算。
- Just-in-time Context：在真正需要时注入。

### 03.5 评测问题

- 关键事实召回率。
- 指令遵循率。
- 上下文利用率。
- 冲突消解正确率。
- 压缩前后任务成功率。
- Token、延迟和成本变化。

### 03.6 已有专题

- [Context Engineering](./Context-Engineering.md)
- [Context Engineering Resources](./Context-Engineering-Resources.md)

---

## 04. Tools、Skills 与协议

### 04.1 Function Calling 与 Tool Schema

- 工具名称和职责边界。
- 参数 Schema 与字段语义。
- 返回 Schema 与可读错误。
- 必填、枚举、默认值和约束。
- 正例、反例和调用时机。
- 工具结果长度控制。

### 04.2 Tool Runtime

- 工具注册表与白名单。
- 参数解析和校验。
- Timeout、Retry、Backoff。
- Idempotency Key。
- Pagination 与流式结果。
- Rate Limit 与熔断。
- 部分成功和可恢复错误。
- Artifact、日志和审计记录。

### 04.3 权限模型

- Read-only。
- Reversible Write。
- External Side Effect。
- Destructive Action。
- Sensitive Data Access。
- 不同等级对应的确认和隔离策略。

### 04.4 MCP

- Host、Client、Server 的关系。
- Tools、Resources、Prompts。
- Transport 与生命周期。
- Capability Discovery。
- 身份认证和权限传递。
- 不可信 Server 和工具描述注入风险。
- MCP 与本地函数工具的选型边界。

### 04.5 Skills 与程序性知识

- Skill 与 Prompt、Tool、Memory 的区别。
- Progressive Disclosure。
- Skill 的触发、读取、执行和验证。
- Skill 版本、依赖和适用范围。
- 从成功/失败轨迹提炼 Skill。
- Skill 污染、供应链和越权风险。

### 04.6 Agent 间协议

- A2A、ACP 等协议解决什么问题。
- Agent 身份、能力声明和消息格式。
- Task、Artifact、Status 和 Handoff。
- 跨 Agent 权限和责任边界。

### 04.7 最小实验

- 为三个工具分别写 Tool Card。
- 实现一个带校验、超时和结构化错误的工具注册表。
- 编写一个最小 MCP Server 和 Client。
- 对高风险工具加入人工确认。

---

## 05. RAG 与知识系统

### 05.1 Ingestion

- 文件类型、大小、Hash 和版本。
- 数据来源、授权和生命周期。
- 文本、PDF、Office、网页、图片、音视频。
- 增量更新和重复内容处理。

### 05.2 Parsing

- 文本抽取和 OCR。
- Layout、标题、段落和列表。
- 表格、公式和图像说明。
- 页码、坐标和原始文件引用。
- 解析质量检测与人工抽检。

### 05.3 Chunking 与 Enrichment

- 固定长度、语义和结构化切分。
- Parent-Child Chunk。
- 标题路径和章节上下文。
- Metadata、实体、关键词和摘要。
- 多模态描述与视觉特征。

### 05.4 Indexing

- Sparse/BM25。
- Dense Embedding。
- Hybrid Index。
- Vector Database。
- Knowledge Graph/GraphRAG。
- 多索引和权限过滤。

### 05.5 Retrieval 与 Rerank

- Query Rewrite/Expansion/Decomposition。
- 多路召回和结果融合。
- Cross-Encoder、LLM Rerank。
- Context Packing。
- Query Router。
- Agentic Retrieval。

### 05.6 Evidence-grounded Generation

- Claim 与 Evidence 绑定。
- 文档、页码、章节、URL 引用。
- 证据不足时的拒答和不确定性表达。
- 相互冲突证据的处理。
- 输出后 Citation Verification。

### 05.7 Multimodal RAG

- 文本、版面和视觉三路信息。
- 图表、截图、公式和表格检索。
- ColPali 类视觉文档检索思路。
- 多模态 Context Packing。
- 多模态引用和人工抽检。

### 05.8 RAG Evaluation

- 解析准确率。
- Retrieval Recall/Precision/nDCG/MRR。
- Rerank 增益。
- Context Relevance。
- Faithfulness 与 Citation Precision。
- Answer Correctness。
- 延迟、成本和索引新鲜度。
- 失败类型：解析、召回、排序、生成、引用。

### 05.9 已有案例

- [运维领域 RAG 问答系统](./运维领域-RAG-问答系统.md)
- [运维 RAG 双索引检索设计](./运维RAG-双索引检索设计.md)

---

## 06. Memory 与状态管理

### 06.1 先区分 State 与 Memory

- State：完成当前任务所需的权威运行状态。
- Memory：跨步骤或跨会话保留、供未来检索的信息。
- 对话历史不等于完整状态，也不等于长期记忆。

### 06.2 Memory 分类

- Working Memory。
- Short-term/Session Memory。
- Episodic Memory。
- Semantic Memory。
- Procedural Memory。
- User/Profile Memory。
- Shared/Team Memory。

### 06.3 Memory 生命周期

- Capture：从哪里获取候选记忆。
- Extract：抽取事实、偏好、经验和错误。
- Validate：验证来源与可信度。
- Write：决定是否写入及写到哪里。
- Retrieve：按任务需要召回。
- Update：新旧记忆合并与冲突处理。
- Consolidate：聚类、总结和抽象。
- Forget：过期、撤回和主动删除。

### 06.4 存储设计

- JSONL：简单、可审计。
- SQLite/PostgreSQL：结构化状态与事务。
- Vector Store：语义召回。
- Knowledge Graph：关系与推理。
- Object/File Store：大 Artifact。
- Checkpoint/Event Log：中断与恢复。

### 06.5 Memory Evaluation

- 写入准确率和写入必要性。
- 召回准确率和覆盖率。
- 冲突处理正确率。
- 过期记忆抑制能力。
- 隐私删除是否彻底。
- Memory 对任务质量、成本和延迟的真实增益。

### 06.6 最小实验

- 实现 Session State + 长期事实记忆。
- 比较无 Memory、全量历史、检索式 Memory。
- 构造冲突和过期记忆案例。
- 输出 Memory 命中和最终答案的完整 Trace。

---

## 07. Workflow 与 Multi-Agent

### 07.1 Workflow 设计

- 顺序执行。
- 条件路由。
- 并行分支。
- Map-Reduce。
- Evaluator-Optimizer。
- 中断、恢复和人工审批。
- 状态图与持久化执行。

### 07.2 什么时候需要 Multi-Agent

- 不同角色需要独立上下文。
- 不同任务需要不同模型或工具权限。
- 子任务可以安全并行。
- 生成与评判需要职责隔离。
- 单 Agent 上下文或职责已经过载。

不应使用 Multi-Agent 的情况：

- 固定 Workflow 已能可靠完成。
- 角色只是名字不同，工具和上下文完全相同。
- 协调成本高于任务分解收益。
- 没有跨 Agent 的状态和评测设计。

### 07.3 常见协作模式

- Router + Specialists。
- Supervisor + Workers。
- Planner + Executor。
- Researcher + Writer + Reviewer。
- Generator + Critic + Verifier。
- Debate/Voting。
- Peer-to-Peer Handoff。

### 07.4 协调机制

- Task Contract。
- Input/Output Schema。
- Shared State 与私有 State。
- Context Isolation。
- Message、Artifact 和引用传递。
- Ownership、状态机和完成定义。
- Timeout、Cancellation 和重试。
- 去重、合并和冲突解决。

### 07.5 常见失败模式

- 重复劳动。
- 任务边界模糊。
- 多角色相互迎合。
- 错误在 Agent 间传播。
- 主 Agent 上下文被子任务污染。
- 死循环、饥饿和任务悬挂。
- 并行数量增加但总耗时和成本更差。

### 07.6 Multi-Agent Evaluation

- 最终任务成功率。
- 单角色贡献度。
- Handoff 正确率。
- 重复工作率。
- 消息和 Artifact 完整性。
- 并行效率。
- 协调成本。
- 故障恢复能力。

### 07.7 已有专题

- [Multi-Agent Evaluation Guide](./Multi-Agent-Evaluation-Guide.md)

---

## 08. Agent Harness 与 Runtime

### 08.1 Harness 的定位

Harness 是模型与真实任务环境之间的运行系统。它不只负责调用模型，还负责状态、工具、权限、恢复、观测和质量闭环。

### 08.2 七层模型

1. Model Layer：Provider、模型路由和结构化输出。
2. Loop Layer：Action/Observation、停止、Interrupt/Resume。
3. Tool Layer：Tools、Skills、MCP 和执行协议。
4. Memory Layer：State、Checkpoint、长期记忆和 Artifact。
5. Policy Layer：系统规则、权限、预算和行为约束。
6. Channel Layer：CLI、Web、IM、IDE 和 API。
7. Automation Layer：Scheduler、Heartbeat、Cron 和事件触发。

### 08.3 Runtime 核心能力

- Run、Task、Step、Attempt 的身份模型。
- 状态机与 Event Log。
- Checkpoint、Resume 和 Replay。
- Tool Runtime 和权限决策。
- Artifact 管理。
- 子 Agent 生命周期和并发控制。
- Token、时间和费用预算。
- 用户中断、取消和修改任务。
- 错误分类与恢复策略。

### 08.4 可靠性六件套

- Idempotency。
- Timeout。
- Retry/Backoff。
- Cost Guard。
- Permission Gate。
- Observability。

### 08.5 最小实验

- 给最小 Agent Loop 增加 Run/Step ID。
- 将每一步写入 Event Log。
- 中途终止后从 Checkpoint 恢复。
- 对同一 Tool Call 做幂等保护。
- 设置总步数、总耗时和总费用上限。
- 使用 Replay 重放一个失败任务。

---

## 09. Evaluation、Observability 与调试

### 09.1 Evaluation 的基本对象

- Task：要完成的真实任务。
- Case：一条固定评测输入。
- Dataset：有版本的 Case 集合。
- Run：一次系统执行。
- Trace/Trajectory：完整过程。
- Artifact：系统产生的文件或结构化结果。
- Grader：评分器。
- Report：聚合结果和失败分析。

### 09.2 评测维度

- 最终任务成功率。
- 约束满足率。
- 工具选择与参数正确率。
- 轨迹效率和冗余步骤。
- 证据完整性和事实一致性。
- 恢复率与人工介入次数。
- 安全动作拦截率。
- 延迟、Token、费用和资源占用。

### 09.3 Grader 体系

- Code-based Grader：确定性规则和硬约束。
- Model-based Grader：语义质量和开放输出。
- Human Grader：高风险、主观或难自动化场景。
- Reference-based 与 Reference-free。
- Point-based、Rubric-based、Pairwise。

### 09.4 Capability Eval 与 Regression Eval

- Capability Eval：系统能否完成一类新任务。
- Regression Eval：已有能力是否因改动退化。
- 每次能力扩展都要把代表性案例加入回归集。

### 09.5 Trace 与 Observability

- Run/Step/Tool Span。
- 输入输出摘要与完整 Artifact 引用。
- Prompt、模型和工具版本。
- Token、延迟、费用和重试次数。
- 状态变化、权限决策和人工操作。
- Error Type、Root Cause 和 Recovery Action。

### 09.6 非确定性处理

- 固定模型、Prompt、工具和数据版本。
- 同一案例多次运行。
- 报告均值、方差和置信区间。
- 区分偶发失败与稳定退化。
- 对 LLM-as-a-Judge 做校准和一致性检查。

### 09.7 Failure Taxonomy

- 需求理解失败。
- 规划失败。
- 工具选择失败。
- 工具执行失败。
- 检索失败。
- 上下文构建失败。
- Memory 污染。
- 权限与安全失败。
- 终止条件失败。
- 最终表达或 Artifact 失败。

### 09.8 CI 与发布 Gate

- Unit Test。
- Static Check。
- Offline Eval。
- Integration Eval。
- End-to-End Eval。
- Safety/Red-team Eval。
- Canary/Shadow Test。
- Production Monitoring。

### 09.9 已有专题

- [Evaluation](./Evaluation.md)
- [Multi-Agent Evaluation Guide](./Multi-Agent-Evaluation-Guide.md)

---

## 10. Safety、权限与治理

### 10.1 Threat Model

- Prompt Injection。
- Indirect Prompt Injection。
- Tool Abuse。
- Data Exfiltration。
- Secret Leakage。
- Unsafe Code Execution。
- Unauthorized External Action。
- Memory Poisoning。
- MCP/Skill Supply-chain Risk。
- Hallucinated Authority。

### 10.2 Trust Boundary

- 用户输入不可信。
- 网页、文档和工具结果不可信。
- 模型输出不是授权。
- 检索到的内容不是系统指令。
- 外部 Agent 的消息不是事实。
- 高风险动作必须经过确定性策略检查。

### 10.3 权限与审批

- 最小权限。
- Allowlist/Denylist。
- Read/Write/Execute/External Side Effect 分级。
- 目标、参数和影响范围预览。
- Human Approval。
- 双人审批或策略引擎。
- 可撤销操作优先。

### 10.4 Sandbox

- 文件系统隔离。
- 进程与命令限制。
- 网络访问控制。
- CPU、内存、时间和磁盘配额。
- Secret 注入和回收。
- 临时环境与销毁。
- Artifact 导出审查。

### 10.5 数据治理

- 数据来源和授权。
- PII/敏感数据识别。
- 数据最小化。
- 加密与访问控制。
- Retention 与删除。
- Audit Log。
- 模型供应商数据政策。

### 10.6 安全评测

- 攻击样本集。
- 越权工具调用。
- 跨租户和跨会话泄漏。
- 恶意文档和网页。
- 社会工程与确认绕过。
- 拒绝是否过度。
- 事件响应和复盘演练。

---

## 11. 模型、数据与 Agentic RL

### 11.1 先做优化决策

遇到质量问题时依次判断：

1. 需求和成功标准是否清楚。
2. 工具和环境是否提供了必要能力。
3. Context 是否正确、充分且无冲突。
4. RAG/Memory 是否召回了正确信息。
5. Workflow/Harness 是否限制了错误路径。
6. 模型是否真的缺少能力。
7. 是否值得通过训练更新权重。

### 11.2 数据合成

- Seed Task 与场景覆盖。
- Self-Instruct/Evol-Instruct。
- Tool-use/Function Calling 数据。
- 多步轨迹和失败轨迹。
- Rejection Sampling。
- 去重、去污染和质量评分。
- 数据 Lineage 与版本管理。

### 11.3 SFT 与偏好优化

- 训练目标和数据格式。
- Tool Call、Observation 与 Final Answer 的 Loss Mask。
- 正确轨迹、纠错轨迹和拒绝轨迹。
- DPO/IPO/KTO 等偏好方法。
- 训练稳定性和能力退化。

### 11.4 Agentic RL

- Environment 与可验证任务。
- Episode、Trajectory、Action、Reward。
- Outcome Reward 与 Process Reward。
- Credit Assignment。
- Verifier/Reward Model。
- 长程任务和稀疏奖励。
- 工具效率、成本和安全奖励。
- GRPO/PPO 等算法在 Agent 场景的使用边界。

### 11.5 训练后评测

- 基线模型与同 Harness 对比。
- 防止把 Harness 改进误记为模型改进。
- Capability、Regression、Safety 三套评测。
- 对不同任务、工具和环境做 Holdout。
- 检查 Reward Hacking 和评测污染。

---

## 12. 应用工程、交互与部署

### 12.1 后端架构

- API Gateway 和身份认证。
- Sync/Async 请求模型。
- Streaming。
- Queue、Worker 和 Scheduler。
- Run/Task/Artifact 数据模型。
- 状态数据库、向量库和对象存储。
- Event Bus 与 Webhook。

### 12.2 前端与人机协作

- Chat、Form、Canvas 和 Task UI。
- 计划、步骤和状态实时同步。
- Tool Call 和证据展示。
- Artifact 预览与下载。
- Approval、Edit、Retry、Cancel。
- 错误、部分成功和恢复提示。
- 多 Agent 角色与任务关系展示。

### 12.3 模型服务与路由

- 多 Provider Adapter。
- 模型能力和任务路由。
- Fallback 与降级。
- Prompt/Response Cache。
- Batch、Streaming 和并发控制。
- Rate Limit 和配额。
- 本地模型、云模型和混合部署。

### 12.4 部署与运行环境

- Serverless、Container、Kubernetes。
- CPU/GPU 资源。
- vLLM/SGLang 等 Serving 思路。
- 环境变量、Secret 和配置管理。
- CI/CD 与数据迁移。
- 灰度、回滚和灾难恢复。
- 内网、离线和受限网络环境。

### 12.5 SLO 与成本

- Availability。
- Latency。
- Task Success Rate。
- Error Budget。
- Token/Run、Cost/Task。
- Tool/API 成本。
- GPU 利用率和排队时间。
- 缓存命中和降级比例。

---

## 13. 项目实验室

实验室不是“看完教程”，而是每个阶段都必须产生可以运行和验证的 Artifact。

### Lab 0：最小 Agent Loop

- 两个工具。
- 最大步数和停止条件。
- JSONL Trace。
- 10～20 条固定 Eval Case。
- 输出：源码、README、Trace、Eval Report。

### Lab 1：领域 RAG Agent

- 文档解析、双路检索、Rerank 和引用。
- Query Router 与权限过滤。
- 证据不足拒答。
- 输出：数据清单、索引配置、Golden Set、失败分析。

建议直接使用现有运维 RAG 专题作为第一版案例。

### Lab 2：Paper/Deep Research Agent

- 多源检索。
- PDF 解析。
- Evidence Store。
- Claim-Citation 绑定。
- 多文档对比和审阅。
- 输出：综述、证据表、Trace、引用准确率报告。

### Lab 3：Web/Browser Agent

- 页面观察、Click/Type/Extract/Screenshot。
- 可访问性树、DOM 摘要和视觉观察。
- 本地测试网页。
- 高风险动作确认。
- 输出：任务集、动作轨迹、截图、恢复率和安全评测。

### Lab 4：Multi-Agent 工作流

- Planner、Researcher、Writer、Reviewer。
- 私有上下文和共享 Artifact。
- 并行任务与 Handoff。
- 单 Agent 基线对比。
- 输出：协作协议、任务图、贡献度和成本对比。

### Lab 5：生产级 Harness

- Run/Step/Event 数据模型。
- Interrupt/Resume/Replay。
- Permission Gate。
- Timeout/Retry/Idempotency。
- 成本预算和可观测性。
- 输出：运行面板、故障注入实验、回归报告。

---

## 14. 案例复盘

每个案例都使用同一套结构，避免只记录“做了什么”。

### 14.1 案例模板

1. 背景和用户任务。
2. 为什么选择 Workflow 或 Agent。
3. 成功标准和非目标。
4. 系统架构与关键数据流。
5. Context、Tools、Memory 和 State 设计。
6. 权限与安全边界。
7. 评测集和基线。
8. 结果、成本和资源使用。
9. 失败类型与根因。
10. 消融实验和替代方案。
11. 当前限制。
12. 可迁移的设计模式。

### 14.2 反模式库

- 把所有信息一次性塞进 Prompt。
- 用角色名称代替真正的多 Agent 分工。
- 工具直接接受任意 Shell、SQL 或 URL。
- 没有最大步数和预算。
- 只看最终回答，不看执行轨迹。
- 只展示 Demo，不维护固定评测集。
- 把模型增强、检索增强和 Harness 增强混为一谈。
- 只记录成功案例，不记录失败和恢复过程。
- 将本地 Mock 成功当成真实 Provider 或部署成功。

---

## 15. 研究前沿

### 15.1 长程任务与 Harness

- Task State Externalization。
- Long-horizon Planning。
- Context Compaction。
- Failure Recovery。
- Dense Process Grading。
- Long-horizon Benchmark。

### 15.2 Agent 自进化

- Experience Reflection。
- Memory Consolidation。
- Trace-to-Skill。
- Skill 自动生成与验证。
- Harness/Prompt 自修改。
- 持续学习与灾难性遗忘。

### 15.3 Verifier 与 Agentic RL

- Verifiable Environment。
- Outcome/Process Verifier。
- Credit Assignment。
- Environment Synthesis。
- Reward Hacking。
- Scalable Oversight。

### 15.4 Browser、Computer Use 与多模态

- DOM、Accessibility Tree 和 Vision 融合。
- GUI Grounding。
- OS/Web Environment Drift。
- 视频、语音和屏幕状态。
- VLA 与具身智能。

### 15.5 Agent 安全与可信

- 不可信工具生态。
- Agent 间信任与委托。
- 可解释轨迹。
- 自动化红队。
- Policy Learning 与 Runtime Enforcement。

### 15.6 AI for Science/Engineering

- Deep Research。
- Literature Agent。
- Coding/Experiment Agent。
- Simulation 与自动实验。
- 证据链、可复现性和科研诚信。

### 15.7 研究卡片模板

每个前沿方向只在满足以下字段后进入主知识库：

- 问题定义。
- 代表论文及版本日期。
- 核心方法。
- 实验环境和 Benchmark。
- 关键结果及证据位置。
- 已知限制。
- 与现有系统的关系。
- 可复现实验。
- 下一步研究问题。

---

## 内部培训课程设计

### 核心课程：10 讲

| 课次 | 主题 | 课堂 Demo | 课后产出 |
| ---: | --- | --- | --- |
| 1 | Agent 全景与最小 Loop | 两工具 Agent | Loop + Trace |
| 2 | Tool Schema、Runtime 与 MCP | 结构化工具调用 | Tool Card + MCP Demo |
| 3 | Context Engineering | 对比全量上下文与 Context Builder | Context 设计文档 |
| 4 | RAG 全链路 | 文档解析、检索和引用 | 小型 RAG + Golden Set |
| 5 | Memory 与状态 | Session/长期 Memory 对比 | Memory 消融报告 |
| 6 | Workflow 与 Multi-Agent | Planner/Worker/Reviewer | 协作协议 + 单 Agent 基线 |
| 7 | Agent Harness | Interrupt/Resume/Replay | Event Log + Checkpoint |
| 8 | Evaluation 与 Observability | 同一 Case 多次运行 | Eval Report + Failure Taxonomy |
| 9 | Safety 与权限 | Prompt Injection + 高风险工具 | Threat Model + Safety Cases |
| 10 | 综合项目评审 | 端到端演示 | 架构、源码、Trace、评测和复盘 |

### 进阶选修

1. 数据合成与 Tool-use 轨迹。
2. SFT、DPO、GRPO 与 Agentic RL。
3. Browser/Computer-Use Agent。
4. Multimodal RAG。
5. 推理服务、模型路由和成本优化。
6. 长程任务、自进化 Memory 与 Skills。

### 每节课的固定结构

```text
课前：20～40 分钟阅读 + 3 个预习问题
课堂：概念 20% + 架构 20% + Demo 30% + 讨论 30%
课后：一个可运行实验 + 一页复盘
验收：固定 Case、Trace、指标和失败解释
```

### 培训材料包

每一讲至少包含：

- `outline.md`：课程大纲。
- `slides.md` 或 PPT：授课内容。
- `demo/`：可运行 Demo。
- `lab.md`：实验任务。
- `cases.jsonl`：固定评测案例。
- `answer-key.md`：讲师参考答案和讨论边界。
- `references.md`：一手资料。
- `changelog.md`：版本变化。

---

## 统一内容模板

以后新建技术专题时，建议直接套用下面的结构：

```markdown
# 专题名称

> 状态：seed / draft / reviewed / verified
> 难度：L0 / L1 / L2 / L3
> 前置知识：
> 最近验证日期：
> 维护人：

## 1. 学习目标

## 2. 问题定义与适用边界

## 3. 核心概念

## 4. 工作机制

## 5. 系统架构与数据流

## 6. 最小实现

## 7. 工程化设计

## 8. 常见失败模式

## 9. 评测方法

## 10. 实验与练习

## 11. 案例复盘

## 12. 关键结论

## 13. 参考资料

## 14. 更新记录
```

### 状态定义

| 状态 | 含义 |
| --- | --- |
| `seed` | 只有素材或初步想法，尚未形成正文 |
| `draft` | 已有正文，但未完成来源与实验检查 |
| `reviewed` | 结构和事实经过人工复核 |
| `verified` | 关键代码、实验或运行路径已重新验证 |

`verified` 只代表注明范围内的验证，不自动代表生产可用、线上可用或所有结论都已复现。

---

## AgentGuide 内容转换规则

| AgentGuide 原表达 | 本知识库的处理方式 |
| --- | --- |
| 岗位学习路线 | 改为能力依赖和技术进阶路线 |
| 高频问答 | 改为概念检查题和设计讨论题 |
| 项目包装 | 改为架构说明、ADR 和技术复盘 |
| 项目亮点 | 改为可验证的技术决策、指标和取舍 |
| 公司案例 | 只保留有明确技术机制和证据的案例 |
| 时间承诺 | 改为前置条件、学习目标和验收标准 |
| 大量资源链接 | 进入资源索引，不直接进入主教程 |

保留的核心原则：

- 先建立 Agent/Workflow 的边界。
- 先做最小 Loop，再引入复杂框架。
- Tools、Context、Memory、State 必须分开设计。
- 没有 Trace 很难调试，没有 Eval 无法证明改进。
- 安全和权限要与工具设计同时开始。
- 每个专题都要落到可运行实验和失败分析。

---

## 现有文件的归位建议

暂时不移动文件，只建立逻辑映射：

| 现有文件 | 建议归属 |
| --- | --- |
| `AI-Agent-全栈知识树.md` | `00-总览与导航/` |
| `Context-Engineering.md` | `03-Context-Engineering/` |
| `Context-Engineering-Resources.md` | `90-资源索引/` |
| `Evaluation.md` | `09-Evaluation与Observability/` |
| `Multi-Agent-Evaluation-Guide.md` | `07-Workflow与Multi-Agent/` + `09-Evaluation与Observability/` |
| `运维领域-RAG-问答系统.md` | `05-RAG与知识系统/` + `13-项目实验室/` |
| `运维RAG-双索引检索设计.md` | `05-RAG与知识系统/` |
| `素材收集箱.md` | `90-资源索引/` |
| `AgentGuide-代码仓走读大纲.md` | `90-资源索引/外部仓库走读/` |

---

## 建设优先级

### P0：先形成最小学习闭环

1. Agent 定义、边界和最小 Loop。
2. Tool Schema、错误协议和权限等级。
3. Context Builder。
4. RAG 最小管线和引用。
5. Trace、Eval Case 和 Failure Taxonomy。
6. 一个可运行的领域 Agent 项目。

完成标准：新成员只依赖本知识库，就能理解主链路、运行 Demo，并读懂一次失败 Trace。

### P1：补齐系统工程

1. Memory 与状态管理。
2. Workflow 与 Multi-Agent。
3. Harness、Interrupt/Resume/Replay。
4. Safety、Sandbox 和审批。
5. 后端、前端和部署。

完成标准：能把最小 Demo 推进到可恢复、可观测、可安全操作的系统原型。

### P2：补齐算法与研究

1. 数据合成。
2. SFT 与偏好优化。
3. Agentic RL 与 Verifier。
4. 长程任务和自进化。
5. 多模态、Computer Use 和 VLA。

完成标准：能清楚区分模型能力改进、Context 改进、RAG 改进和 Harness 改进，并用独立实验验证。

### P3：建立长期运营机制

1. 每月检查失效链接和版本变化。
2. 每季度更新课程 Demo 和 Eval Dataset。
3. 新增内容先进入素材箱，再进入正式专题。
4. 过时结论移入归档，保留迁移说明。
5. 每个重要结论记录来源、日期和验证范围。

---

## 目标资产

1. **知识地图**：知道一个问题属于哪一层、依赖什么。
2. **技术专题**：能解释机制、边界和工程取舍。
3. **可运行实验**：不是只保留代码片段，而是能重复执行。
4. **评测与失败库**：知道系统为什么成功，也知道为什么失败。
5. **内部课程包**：任何维护者都能按统一材料复用和授课。

最终判断标准不是“收录了多少链接”，而是遇到一个真实 Agent 问题时，能否沿着这套知识库快速完成：

```text
定位问题
  -> 找到对应机制
  -> 选择设计模式
  -> 运行最小实验
  -> 查看 Trace
  -> 用 Eval 验证
  -> 沉淀案例与结论
```
