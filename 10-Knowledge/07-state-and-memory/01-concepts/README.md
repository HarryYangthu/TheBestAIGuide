# State 与 Memory：概念和边界

> 状态：seed

## 一句话区分

- **State**：当前任务继续执行所需的权威运行事实。
- **Checkpoint**：State 在某个可恢复时间点的持久化快照或事件位置。
- **Session**：一段交互或运行的边界，不自动等于 State 或 Memory。
- **Memory**：经过选择、为未来任务保留并按需读取的信息。
- **Context**：一次模型调用实际可见的输入，其中可以包含 State 和检索到的 Memory。

## 核心差异

| 维度 | State | Memory |
| --- | --- | --- |
| 主要问题 | 系统现在处于什么状态 | 以后可能需要记住什么 |
| 典型内容 | 当前步骤、工具结果、审批、重试、Artifact | 偏好、历史事实、经验、任务摘要 |
| 读取方式 | 按任务或运行标识精确加载 | 按相关性、主体、时间和权限检索 |
| 更新方式 | 由工作流或 Runtime 确定性更新 | 经过写入策略选择、验证和合并 |
| 一致性要求 | 应能恢复和解释当前运行 | 允许摘要和抽象，但必须保留来源与时效 |

## Memory 类型

- Working Memory：为当前推理暂时保留的信息，通常接近 Context。
- Episodic Memory：一次任务或经历的记录。
- Semantic Memory：从经历或资料中抽取的事实与关系。
- Procedural Memory：可复用的步骤、规则和操作经验。
- Profile Memory：与主体相关的稳定偏好或约束。

这些类型是分析框架，不要求使用不同数据库实现。

## 必须保持的边界

- 对话历史不自动等于 State，也不自动等于 Memory。
- 数据库是存储手段，不代表其中的数据都是 Memory。
- 不是所有 State 都值得写入长期 Memory。
- Memory 在重新进入 Context 前需要检查主体、来源、时效、权限和冲突。
- 旧 Memory 不能静默覆盖当前 State；冲突应由确定性规则、验证或人工决策处理。

## 生命周期

```text
Observation / Tool Result
          ↓
      Update State
          ↓
Checkpoint / Continue / Finish
          ↓
  Select + Validate + Write
          ↓
        Memory
          ↓ future retrieval
Context Candidate → Policy Check → Model Context
```
