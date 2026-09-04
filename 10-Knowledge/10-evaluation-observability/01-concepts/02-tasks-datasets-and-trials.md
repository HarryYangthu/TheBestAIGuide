# 任务、数据集与多次试验

> 状态：draft

## Task 不是一句 Prompt

一个可执行任务至少包含：

```yaml
id: "support-refund-001"
version: "1.2"
description: "在满足政策的前提下处理指定订单退款"
input:
  user_request: "..."
initial_state:
  fixture: "fixtures/refund-001"
constraints:
  - "不得修改其他订单"
success_criteria:
  - id: "refund-created"
    check: "database"
  - id: "confirmation-sent"
    check: "event_log"
forbidden_outcomes:
  - "refund_amount_exceeds_paid_amount"
graders:
  - "refund_state_grader@2"
tags: ["refund", "state-change", "permission"]
```

Task 应描述结果和约束，不应把唯一操作路径写死，除非路径本身就是被测要求。

## 任务来源

优先级通常是：

1. 真实失败、投诉和人工接管记录；
2. 高频真实工作流的去敏样本；
3. 产品规范中的关键路径与边界条件；
4. 专家构造的反例和安全任务；
5. 合成任务，用于补齐稀缺组合。

合成任务应标记生成方法，并由规则或专家抽查。它可以扩大覆盖，不能自动代表真实分布。

## 数据集分层

- `dev`：开发时可见，用于快速迭代和调试。
- `validation`：用于选择 Prompt、模型或策略。
- `test`：限制访问，用于最终比较和发布判断。
- `challenge`：高难度或对抗性任务，防止套件饱和。
- `incident`：由线上事故冻结而来的回归任务。

同一用户、文档模板、代码仓或问题变体要按组划分，避免近重复跨集合泄露。

## 覆盖矩阵

任务数不是唯一目标。先按以下维度建立矩阵：

- 典型场景与长尾场景；
- 简单、组合和长程任务；
- 正常输入、歧义输入和恶意输入；
- 成功路径、工具失败、超时和恢复；
- 不同语言、格式、设备或环境；
- 权限、隐私和高影响动作；
- 已知失败类型。

报告每个切片的结果，避免总体均值掩盖关键回归。

## Trial 配置

每次 Trial 应记录：

- 随机种子或供应商可用的采样配置；
- 模型与推理参数；
- 最大轮次、Token、时间和费用预算；
- 工具、网络和文件权限；
- 环境镜像、Fixture 与重置结果；
- 缓存是否启用；
- 重试策略及重试是否计入结果。

Trial 数量不应固定照搬“3/10/100”。它取决于基准波动、最小可接受差异、任务风险和预算。先做小规模方差估计，再决定正式样本量。

## 环境隔离

评测环境需要：

- 每次 Trial 从已知初始状态启动；
- 并行任务不共享可变数据；
- 时间、网络和外部依赖尽量可控；
- 生成代码在沙箱中执行；
- 有副作用操作使用模拟、测试账户或明确授权环境；
- Trial 结束后保存结果并安全清理环境。

如果基础设施自身不稳定，先测量环境噪声，再解释 Agent 波动。

## 防污染与防投机

- 测试集访问最小化并记录读取行为；
- 评分器秘密不进入 Agent 上下文；
- 检查是否通过文件名、Fixture 或错误信息泄露答案；
- 对任务做语义等价变体，检查系统是否只记住模板；
- 定期加入新鲜任务，并保留旧任务用于纵向比较；
- 发现 Agent 找到更好的合法路径时，修正过度约束的 Grader，而不是强制模仿参考轨迹。

## 数据集版本化

每次报告至少记录：

```text
suite_name + suite_version
task_ids + task_versions
fixture_hashes
grader_versions
environment_version
created_at + source_window
```

任务、评分器或 Fixture 变化后，不应与旧结果直接拼成同一时间序列；需要重新跑基线或明确标注断点。

下一步：[评分器与组合计分](03-graders-and-scoring.md)。
