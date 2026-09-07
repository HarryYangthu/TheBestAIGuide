# 连续学习路线

> 状态：draft
> 原则：先理解模型和最小 Agent，再学习信息、行动、编排、验证与生产系统。

## 如何阅读一个知识领域

先读领域 README，再进入概念和模式。用案例理解取舍，在 Notebook 中修改输入，最后去源码查执行过程。

每次学习至少回答三个问题：它实际做了什么？在什么条件下会错？对应代码在哪里？

## 选一个起点，沿同一问题走下去

| 起点 | 阅读与动手顺序 | 第一段学习的完成条件 |
| --- | --- | --- |
| 想理解模型为什么这样算 | 数学与梯度 → Token/Embedding → Attention → 推理 → Tiny Transformer | 手算一行注意力；从输入形状跟到输出；说明训练预测哪个标签 |
| 想自己做 Agent | 根目录的两条入门命令 → Agent Loop → Tools → Context/RAG → State/Memory → Runtime | 区分“程序固定选动作”和“模型选动作”；复现有证据回答与拒答，再观察一次恢复 |
| 已有 Agent，需要定位问题 | Evaluation → 失败对应的领域 → 修改一个变量 → 同题对照 | 能解释失败发生在哪一层；用结果与轨迹验证修改，而不只比较回答措辞 |

不需要先读完所有数学才能开始系统实验。遇到交叉熵、矩阵形状或置信区间，再回对应基础篇补；每个阶段只改变一个条件，先预测再运行。

## 主线与自检

下表是学习检查点，不是要求背诵的题库。先遮住“检查要点”作答；答不上来时回到同一行的实验或正文。能复述术语还不足以进入下一步，需要解释一次具体计算或状态变化。

| 顺序与入口 | 动手入口 | 检查自己是否理解 | 检查要点 |
| --- | --- | --- | --- |
| 1 [AI 基础](../10-Knowledge/01-ai-foundations/README.md) | 该域的梯度与拟合 Notebook | 训练误差下降，为什么测试误差可能上升？ | 拟合了样本中的噪声；验证集选配置，测试集留作最终评估 |
| 2 [基础模型](../10-Knowledge/02-foundation-models/README.md) | Attention Notebook → [Tiny Transformer](../20-Projects/tiny-transformer/README.md) | 为什么 Softmax 沿候选位置算？KV Cache 保存了什么？ | 每个查询对所有可见候选分配权重；缓存历史 K/V，当前查询仍需和历史比较 |
| 3 [Agent Core](../10-Knowledge/03-agent-core/README.md) | Agent Loop Notebook | 工具执行成功能否结束整个任务？ | 只证明这一步执行成功；还须判断任务目标是否满足 |
| 4 [Context](../10-Knowledge/04-context-engineering/README.md) | 预算与压缩 Notebook | 资料没超窗口，为什么仍可能影响错误决策？ | 可能有冲突、无关内容或信任边界混淆；长度只解释一部分失败 |
| 5 [Tools / Skills / 协议](../10-Knowledge/05-tools-skills-protocols/README.md) | Runtime 与 MCP 实验 | JSON 符合 Schema，能否立即执行？ | 还要检查业务参数、身份、权限、预算以及当前状态 |
| 6 [RAG](../10-Knowledge/06-rag-and-knowledge-systems/README.md) | 检索消融 Notebook → 工作台检索/生成结果 | 排第一、引用存在，为什么仍不保证答案正确？ | 相关性排序不是真伪判断；证据还要支持该结论且版本/范围适用 |
| 7 [State / Memory](../10-Knowledge/07-state-and-memory/README.md) | Memory Notebook → 工作台跨会话任务 | 数据库里有条记录，为什么本轮可能不读取？ | 主体不匹配、已删除/过期，或与当前任务无关；存储不等于入上下文 |
| 8 [Planning / Workflow / Multi-Agent](../10-Knowledge/08-planning-workflow-multi-agent/README.md) | 并行调度 Notebook → 工作台 DAG | 某条资料更新，需要重跑所有角色吗？ | 使依赖它的结果失效，并保留无依赖分支；靠版本/依赖记录判断 |
| 9 [Runtime / Harness](../10-Knowledge/09-runtime-harness-environment/README.md) | 故障恢复 Notebook | 请求超时，为什么不能直接重复执行？ | 结果未知不等于动作未发生；先查状态，再按幂等与恢复约定处理 |
| 10 [Evaluation](../10-Knowledge/10-evaluation-observability/README.md) | 评分 Notebook → 工作台任务配对统计 | 同一道题重复 20 次，能当 20 道题比较吗？ | 题目覆盖没有增加；统计应保留任务分组和系统间配对关系 |
| 11 [Safety](../10-Knowledge/11-safety-security-governance/README.md) | 权限实验 → 工作台注入报告 | 非法操作发生次数为 0，是否证明模型没被诱导？ | 分开看模型提出什么、是否合格式、执行层允许了什么 |
| 12 [Agent Learning](../10-Knowledge/12-agent-learning/README.md) | 轨迹数据 Notebook → Tiny 的训练实验 | 测试通过的轨迹为什么不能直接全量拿来训练？ | 还需排除泄漏、越权、低质量步骤，明确损失作用于哪些 token/动作 |
| 13 [应用工程](../10-Knowledge/13-application-engineering/README.md) | 学习工作台网页与 API | 刷新网页后，审批能否重复产生动作？ | UI 只是入口；服务端需校验 run、状态版本与动作是否已处理 |
| 14 [生产工程](../10-Knowledge/14-production-engineering/README.md) | 成本算例与工作台队列 | 加重试为什么可能让拥塞更严重？ | 每次重试又占容量；同时看接收量、等待、拒绝和完成情况 |
| 15 [多模态](../10-Knowledge/15-multimodal-and-embodied/README.md) | 文档证据 Notebook → 工作台 PDF | 抽出正确数字，为什么仍可能回答错误？ | 表头、单位、行列或页内归属可能丢失，数字必须与结构绑定 |
| 16 [研究前沿](../10-Knowledge/16-research-frontiers/README.md) | 科研实验与文献角色对照 | 多写一个 Reviewer，为什么不一定更可靠？ | 需要独立证据和可执行判据；角色名称不能消除共同错误 |

项目命令和具体输出从[项目总表](../20-Projects/README.md)进入。上表覆盖学习主线；世界模型、具身和真实生产环境等方向的演示深度不同，不能将小实验理解为这些领域已完整复现。

## 专题顺序：Context Engineering

1. [主题总览](../10-Knowledge/04-context-engineering/01-concepts/00-overview.md)
2. [上下文模型](../10-Knowledge/04-context-engineering/01-concepts/01-context-model.md)
3. [上下文失败模式](../10-Knowledge/04-context-engineering/01-concepts/02-failure-modes.md)
4. [Context Builder](../10-Knowledge/04-context-engineering/02-patterns/01-context-builder.md)
5. [上下文优化策略](../10-Knowledge/04-context-engineering/02-patterns/02-optimization-strategies.md)
6. [上下文评测](../10-Knowledge/04-context-engineering/01-concepts/03-context-evaluation.md)
7. [配套实验](../10-Knowledge/04-context-engineering/04-labs/README.md)

## 专题顺序：RAG

1. [RAG 端到端流程](../10-Knowledge/06-rag-and-knowledge-systems/01-concepts/01-rag-pipeline.md)
2. [混合检索与重排机制](../10-Knowledge/06-rag-and-knowledge-systems/01-concepts/02-hybrid-retrieval-and-reranking.md)
3. [Hybrid Retrieval 模式](../10-Knowledge/06-rag-and-knowledge-systems/02-patterns/hybrid-retrieval.md)
4. [运维领域 RAG 案例](../10-Knowledge/06-rag-and-knowledge-systems/03-cases/运维领域-RAG-问答系统.md)
5. [双索引设计决策](../10-Knowledge/06-rag-and-knowledge-systems/03-cases/运维RAG-双索引检索设计.md)
6. [实验入口](../10-Knowledge/06-rag-and-knowledge-systems/04-labs/README.md)与[代码入口](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/README.md)

## 专题顺序：Evaluation

1. [Agent Evaluation 总览](../10-Knowledge/10-evaluation-observability/01-concepts/00-overview.md)
2. [评测对象与系统模型](../10-Knowledge/10-evaluation-observability/01-concepts/01-evaluation-model.md)
3. [任务、数据集与多次试验](../10-Knowledge/10-evaluation-observability/01-concepts/02-tasks-datasets-and-trials.md)
4. [评分器与组合计分](../10-Knowledge/10-evaluation-observability/01-concepts/03-graders-and-scoring.md)
5. [统计与可靠性](../10-Knowledge/10-evaluation-observability/01-concepts/04-statistics-and-reliability.md)
6. [Trace 与失败归因](../10-Knowledge/10-evaluation-observability/01-concepts/05-traces-and-failure-analysis.md)
7. [Multi-Agent 系统评测](../10-Knowledge/10-evaluation-observability/01-concepts/06-multi-agent-evaluation.md)
8. [评测运营](../10-Knowledge/10-evaluation-observability/02-patterns/01-evaluation-operations.md)和[模板清单](../10-Knowledge/10-evaluation-observability/02-patterns/02-templates-and-checklists.md)

## 如何使用配套实验

先阅读 Notebook 的问题和预期现象，再执行代码，最后改变一个参数：例如 Attention 的维度、Context 预算、检索查询或记忆有效期。不要一次改多个条件，否则很难解释结果为什么变了。

[统一运行说明](../scripts/README.md)提供依赖安装、Python/TypeScript 测试和 Notebook 执行命令。[综合项目](../20-Projects/domain-research-agent/README.md)把多个领域的真实源码连起来，可以作为第二轮阅读的入口。

## 证据边界

正文、源码测试、Notebook 和外部系统复现分别记状态。本地小实验可检验机制和边界，不能直接推出真实 LLM、真实用户流量或生产环境的效果。具体已执行范围见[建设状态](Knowledge-Status.md)。
