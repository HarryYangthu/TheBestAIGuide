# Multi-Agent 系统评测

> 状态：draft
> 前置：[Agent Evaluation](Evaluation.md)

## 核心结论

Multi-Agent 评测的对象是“协作系统”，不是若干单 Agent 分数的平均值。除了最终结果，还必须检查路由、交接、共享状态、并行协作、冲突处理和额外开销。

最关键的基线不是另一个 Multi-Agent 框架，而是：同一个任务能否由更简单的单 Agent 或确定性工作流以更低成本完成。

## 系统模型

```text
Task + Shared Environment
          │
          ▼
Supervisor / Router
   ├─> Agent A ──┐
   ├─> Agent B ──┼─> Merge / Review ─> Outcome
   └─> Agent C ──┘
          │
          ▼
Messages + Handoffs + Shared State + Tool Effects
```

一个 Trial 要绑定：

- 拓扑和角色版本；
- 路由策略；
- 每个 Agent 的模型、Prompt、工具和权限；
- 共享与私有 Context 规则；
- 消息、状态和 Artifact 协议；
- 并发、超时、重试和终止策略；
- 合并或裁决逻辑。

## 为什么更难

### 错误传播

上游 Agent 的错误可能被下游当作已验证事实。需要记录首次错误、传播路径和哪个边界缺少验证。

### 路由本身是决策

最终失败可能不是专家能力不足，而是任务被路由给错误角色、重复分发或无人负责。

### 局部最优不等于系统最优

每个 Agent 都完成自己的子任务，合并后仍可能冲突、重复或无法满足总目标。

### 并行带来共享状态问题

并发写文件、数据库或计划时会出现覆盖、竞态和版本冲突。评测环境必须能复现这些情况。

### 成本被拓扑放大

多 Agent 会增加模型调用、上下文复制、通信和等待。只比较答案质量会忽略系统取舍。

## 评测维度

### 1. Router / Supervisor

检查：

- 是否识别需要拆分的任务；
- 是否选对角色与工具权限；
- 是否避免不必要的重复分发；
- 是否在信息不足时补充调查或升级；
- 是否能停止，而不是形成委托循环。

可构造带有人工标注路由集合的 Task，并允许多个等价路由，只要满足能力和权限约束。

### 2. Handoff

有效交接至少包含：

- 子目标与成功条件；
- 已确认事实及来源；
- 已完成动作和真实结果；
- 未解决问题与风险；
- 允许使用的工具、权限和预算；
- 期望返回的 Artifact Schema。

评分时检查信息是否正确、充分、最小且可追溯，而不是只看消息是否“写得详细”。

### 3. Collaboration

检查：

- 是否共享真正有用的新信息；
- 是否出现重复检索和重复执行；
- Reviewer 是否发现了实际缺陷；
- 并行分支是否独立；
- 合并者是否处理互相冲突的结果。

### 4. State Consistency

验证共享状态的版本、原子更新、冲突检测和回滚。对于文件或数据库任务，应比较每个 Agent 的动作与最终状态，不依赖自述。

### 5. Conflict Resolution

设计故意产生不同答案或修改冲突的任务，检查系统是否：

- 能识别冲突；
- 请求证据或重新验证；
- 按权威来源和适用范围裁决；
- 无法裁决时升级给人；
- 保留被否决方案和原因。

### 6. Efficiency

至少记录：

- 总模型调用、工具调用与消息数；
- 串行关键路径和并行等待时间；
- 输入、输出和缓存 Token；
- 重复工作比例；
- 单个成功任务成本；
- 相比单 Agent 基线的质量增益与额外成本。

## 任务设计

适合 Multi-Agent 评测的任务应具有真实协作需求，例如：

- 可独立并行的研究或实现分支；
- 明确不同权限的角色；
- 需要异质工具或领域知识；
- 需要生成与独立审查；
- 单个 Context 难以容纳、但子任务边界清楚。

不要用一个 Agent 轻松完成的小任务证明多 Agent 有效。

## 基线与消融

至少比较：

1. 单 Agent + 全部工具；
2. 单 Agent + 确定性工作流；
3. Multi-Agent 完整系统；
4. 移除某个角色；
5. 固定路由替代模型路由；
6. 关闭并行或共享记忆；
7. 替换合并/Reviewer 策略。

消融能回答“增益来自角色分工、更多采样、并行，还是仅仅用了更多 Token”。

## 评分结构示例

```yaml
graders:
  hard_gates:
    - final_outcome_correct
    - no_permission_violation
    - shared_state_consistent
  collaboration:
    routing_quality: "rubric-or-labeled-check"
    handoff_completeness: "schema-and-rubric"
    conflict_resolution: "scenario-check"
    duplicate_work: "trace-derived"
  efficiency:
    end_to_end_latency: "metric"
    model_calls: "metric"
    cost_per_success: "metric"
```

字段只是模板，不提供通用权重和阈值。

## 四类系统的关注点

| 系统 | Outcome 验证 | 特有风险 |
| --- | --- | --- |
| 编程 Agent | 测试、构建、Diff、静态检查 | 多 Agent 同改文件、测试互相污染、合并冲突 |
| 研究 Agent | 主张—证据映射、来源质量、覆盖 | 同源重复、引用漂移、错误结论跨角色传播 |
| 对话 Agent | 用户目标、状态更新、升级记录 | 角色切换丢上下文、重复提问、责任循环 |
| Computer Use | 最终 UI/系统状态、截图、事件日志 | 竞态点击、不可逆动作、环境噪声和权限 |

## 可靠性

同一 Task 运行多个 Trial，并区分：

- 路由是否稳定；
- 子任务结果是否稳定；
- 合并是否稳定；
- 并发调度是否引入额外波动；
- 某个共享依赖是否导致相关失败。

`pass@k` 适合允许多个候选后选优的情形；“连续多次都成功”的稳定性指标必须另行定义。详见[统计与可靠性](04-statistics-and-reliability.md)。

## 环境与安全

- 每个 Trial 使用隔离 Fixture；
- 每个 Agent 只获得职责所需权限；
- 高风险副作用通过测试账户、沙箱或批准门禁；
- Agent 间消息视为不可信输入，防止间接注入；
- 并发写入使用锁、版本或事务；
- 评测记录中隐藏密钥、PII 和跨租户数据。

## 最小 Trace

```yaml
run_id: "..."
topology_version: "..."
agents:
  - id: "planner"
    model: "..."
    prompt_version: "..."
events:
  - type: "route"
    from: "supervisor"
    to: "researcher"
    task_ref: "subtask-1"
  - type: "handoff"
    artifact_ref: "artifact-7"
  - type: "state_write"
    version_before: 3
    version_after: 4
outcome: {}
grader_results: []
```

不要求保存隐藏思维链；保留可观察决策、调用、交接和状态即可。

## 上线前检查

- [ ] Multi-Agent 在目标任务上优于简单基线，且增益值得成本。
- [ ] 路由有标注样本、反例和回归任务。
- [ ] Handoff 使用明确 Schema，关键信息可追溯。
- [ ] 共享状态有版本与并发控制。
- [ ] 冲突、超时、Agent 失联和部分成功有处理策略。
- [ ] 每个 Agent 的工具与数据权限最小化。
- [ ] 多 Trial 结果包含分布和失败分类。
- [ ] Judge 已校准，评分器秘密不会泄露给被测 Agent。
- [ ] 可从 Trace 定位第一次错误及传播路径。
- [ ] 线上仍有监控、抽样审查和人工升级渠道。

## 结论

多 Agent 的价值必须由端到端结果、协作质量和成本共同证明。如果移除路由、角色或通信后结果不变，系统很可能只是增加了复杂度，而没有增加能力。

## 来源

- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
