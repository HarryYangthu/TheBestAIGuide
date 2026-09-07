# Trace 与失败归因

> 状态：draft

## Trace 的目的

Trace 不是把所有文本永久保存，而是为以下问题提供最小充分证据：

- 发生了什么；
- 哪个系统版本做的；
- 最终环境变成什么；
- 第一次偏离预期发生在哪里；
- 是否能够重放、复现或解释；
- 是否存在越权、泄露或成本异常。

## Trace、Span、Event 分别是什么

| 名词 | 记录的对象 | 教学例子 |
|---|---|---|
| Trace | 一次请求跨组件的整条执行路径 | run-42 从收到任务到最终验收 |
| Span | 一段有开始、结束和父子关系的操作 | 第一次调用检索服务，耗时 80 ms |
| Event | 某个时刻发生的一件事 | 开始重试、权限拒绝、Checkpoint 提交 |

一个工具动作重试三次，应保留同一逻辑 step 和不同 attempt；否则无法区分三次尝试与三个业务动作。计算本进程耗时用单调时钟，跨机器关联依赖 ID 与调用关系，不能只按墙钟时间排序推断先后因果。配套 Harness 的 `sequence/type/attributes` 是顺序事件列表，没有实现完整 Span 树。

## 事件模型

一次 Agent Run 可以作为根 Span，下面连接模型、工具、检索、工作流节点和环境操作：

| 父 Span | 子操作示例 | 对应观察 |
|---|---|---|
| agent.run | context.build、model.invoke、tool.call、grader.evaluate | 每段耗时、状态和输入输出引用 |
| tool.call | external.request | 下游请求 ID、attempt、错误与回执 |

同名 `model.invoke` 可以出现多次，各自要有独立 Span ID；表中的名称只是本库结构示意。

每个事件至少记录：

- `run_id`、`task_id`、`trial_id`；
- 父子关系、开始与结束时间；
- 操作类型和版本；
- 状态、错误类型与重试关系；
- 输入输出的安全引用或摘要；
- Token、延迟和成本口径；
- 工具权限与副作用标记。

OpenTelemetry 的 GenAI 语义约定仍在演进。采用时固定版本，并为未稳定字段提供内部兼容层，不要把当前字段名当成永久标准。

## Outcome Snapshot

对有状态任务，在 Trial 前后保存可比较快照，例如：

- 文件树、内容哈希和测试结果；
- 数据库关键行或事件日志；
- 浏览器 DOM、截图和网络结果；
- 外部 API 的测试环境记录；
- 已创建的 Artifact 及其校验值。

必须避免把生产密钥、完整 PII 或受限内容复制到评测存储。

## 失败分类

| 层 | 典型失败 |
| --- | --- |
| Task/Spec | 成功标准模糊、参考答案错误、非法唯一路径 |
| Data/Fixture | 环境未重置、样本泄露、版本不匹配 |
| Context/Retrieval | 必要证据缺失、错误片段进入、约束被截断 |
| Model/Policy | 计划错误、错误理解、无法利用已有证据 |
| Routing/Handoff | 路由到错误角色、交接丢失信息、责任循环 |
| Tool/Runtime | Schema、权限、超时、重试、幂等或执行错误 |
| Environment | 外部依赖、网络、时间或基础设施噪声 |
| Outcome | 最终状态部分完成、污染其他状态或未持久化 |
| Grader | 过严、漏判、Judge 漂移或被输出注入 |

一个 Run 可以有多个标签，但应标出 `first_failure` 和后续传播关系。

## 归因流程

1. 先检查 Outcome 和硬门禁，确认真实失败。
2. 找到第一个与预期不一致的可观察事件。
3. 查看该事件当时的输入、权限、状态和工具结果。
4. 判断错误是缺少信息、错误决策还是执行失败。
5. 用最小修改构造反事实：只替换 Context、模型、工具或 Grader 中的一项。
6. 能稳定复现后，将样本加入对应层的回归集。

不要从最终一句错误回答直接推断“模型能力不够”。

## 隐私与安全

- 默认关闭完整 Prompt、Completion 和工具正文采集；
- 仅在受控环境按需开启，并设置保留期限；
- 记录数据分类、访问主体和审计日志；
- 对密钥、身份信息和业务敏感字段做源头脱敏；
- Trace UI 也要执行租户和角色隔离；
- 模型 Judge 看到的 Trace 仍需经过最小化和授权。

## 从失败到知识

每个确认失败至少产出：

```yaml
failure_id: "..."
first_failure_layer: "tool_runtime"
symptom: "..."
root_cause: "..."
affected_versions: []
minimal_reproduction: "..."
fix: "..."
regression_task: "..."
remaining_risk: "..."
```

这份记录应进入 Failure Postmortem 或 Eval 数据集，而不是只留在聊天和临时日志中。

## 来源

- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [OpenTelemetry GenAI conventions migration notice](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

## 一条最小可用的失败轨迹

[教学案例](../03-cases/01-from-task-dataset-to-regression.md)的越权任务记录：`trial_start → lookup(scope_checked=False) → trial_end(success=False)`。与候选版对比，首次差异是缺少 `filter(authorized=False)`，结合源码可确认候选版补了返回前的范围判断。因此先修这一逻辑；改回答文风解决不了返回了其他租户记录的问题。这里被测函数本来就持有完整 fixture，事件不证明存储层已按权限隔离读取。

这里事件由被测教学函数主动 emit，不能当独立审计事实。生产工具权限与副作用记录应由 Runtime 产生，防止被测 Agent 漏报。当前工程保留任务/Trial 的顺序事件，不自称完整 OpenTelemetry 导出器。

2026-09-06 核验发现 GenAI 约定文档已迁移到独立维护位置；应跟随[迁移入口](https://opentelemetry.io/docs/specs/semconv/gen-ai/)固定实际采用的仓库提交和 schema。实验使用自己的 `type/sequence/attributes` 字段，不声称这些是已稳定的 `gen_ai.*` 标准。
