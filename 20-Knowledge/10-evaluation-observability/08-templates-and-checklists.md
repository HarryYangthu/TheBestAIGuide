# Evaluation 模板与检查清单

> 状态：draft
> 用法：复制结构后按具体系统填写；示例字段和阈值不是默认配置。

## Task 模板

```yaml
id: "domain-capability-001"
version: "1.0"
suite: "capability"
description: "要完成的真实任务"
source:
  type: "incident | production-sample | expert | synthetic"
  reference: "..."
input: {}
initial_state:
  fixture: "..."
constraints: []
success_criteria:
  - id: "..."
    target: "outcome | trajectory"
    grader: "...@version"
forbidden_outcomes: []
budgets:
  max_turns: null
  max_duration_seconds: null
  max_cost: null
tags: []
```

## Trial Manifest

```yaml
run_id: "..."
task_id: "..."
trial_index: 0
system_under_test:
  app_commit: "..."
  harness_version: "..."
  model: "provider/model/snapshot"
  inference_config: {}
  prompt_version: "..."
  context_builder_version: "..."
  tool_versions: {}
environment:
  image: "..."
  fixture_hash: "..."
  network_policy: "..."
  clock_policy: "..."
limits: {}
```

## Grader 模板

```yaml
id: "groundedness"
version: "2.1"
type: "deterministic | model | human"
target: "outcome | trajectory"
dimension: "..."
rubric:
  pass: "..."
  fail: "..."
  insufficient: "..."
inputs: []
output_schema:
  label: "pass | fail | insufficient"
  evidence: []
  rationale: "..."
calibration_set: "..."
```

## 单次结果模板

```yaml
run_id: "..."
status: "completed | timeout | infrastructure_error"
outcome_snapshot: "artifact-ref"
trajectory_ref: "artifact-ref"
metrics:
  turns: 0
  tool_calls: 0
  input_tokens: null
  output_tokens: null
  cached_tokens: null
  latency_ms: null
  cost: null
grader_results:
  - grader: "...@version"
    label: "..."
    score: null
    evidence: []
failure:
  first_failure_layer: null
  labels: []
```

## 比较报告模板

```markdown
# Eval Report

- Candidate：
- Baseline：
- Suite / Task / Grader 版本：
- 运行时间与环境：
- Task 数 / Trial 数 / 排除项：

## 决策

- 硬门禁：
- 主要指标与区间：
- 关键切片：
- 成本与延迟：
- 最大回归：
- 新失败类型：
- 结论：发布 / 阻断 / 人工审查
```

## Task 检查

- [ ] 目标、初始状态和成功条件明确。
- [ ] 允许多个合法路径，不把参考轨迹写成唯一答案。
- [ ] 约束、禁止结果和副作用已列出。
- [ ] Fixture 可重置且不会跨 Trial 污染。
- [ ] 任务来源、版本和数据权限可追踪。
- [ ] 覆盖真实场景、边界、失败和对抗输入。

## Trial 检查

- [ ] 固定模型、Prompt、工具、Context 和环境版本。
- [ ] 记录预算、缓存、重试和随机配置。
- [ ] 多 Trial 数量有方差或风险依据。
- [ ] 基础设施失败单独记录。
- [ ] 并发运行不会共享可变 Fixture。

## Grader 检查

- [ ] 能用确定性 Outcome 检查的，不只用模型 Judge。
- [ ] 开放式 Rubric 有清晰正例、反例和 `insufficient`。
- [ ] Judge 输出包含证据且 Schema 可校验。
- [ ] 人工校准集、分歧和版本已记录。
- [ ] 被测输出不能注入或覆盖评分指令。
- [ ] 权重、阈值和硬门禁来自明确业务取舍。

## Trace 与隐私检查

- [ ] 能定位第一次偏离预期的事件。
- [ ] Outcome 快照和工具副作用可验证。
- [ ] Trace 记录版本、父子关系、错误和重试。
- [ ] 不依赖不可见的隐藏思维链。
- [ ] Prompt、工具结果、PII 和密钥默认最小化或脱敏。
- [ ] 保留期限、访问控制和删除机制明确。

## 发布检查

- [ ] 与当前生产或已知基线做配对比较。
- [ ] 报告样本量、区间、关键切片和排除项。
- [ ] 核心功能、安全、权限和数据完整性门禁通过。
- [ ] 质量增益与延迟、成本变化一起评估。
- [ ] 失败已归因并加入回归集。
- [ ] 有 Shadow、分阶段发布、监控和人工升级方案。

## Multi-Agent 附加检查

- [ ] 有单 Agent 或确定性工作流基线。
- [ ] 路由、交接、共享状态和冲突分别评分。
- [ ] 每个角色只获得所需工具和数据权限。
- [ ] 能区分首次错误与跨 Agent 传播。
- [ ] 重复工作、并行等待和单次成功成本可见。

完整说明见 [Agent Evaluation](Evaluation.md) 与 [Multi-Agent 评测](Multi-Agent-Evaluation-Guide.md)。
