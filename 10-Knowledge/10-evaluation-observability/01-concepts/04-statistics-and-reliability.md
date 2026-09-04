# 统计与可靠性

> 状态：draft
> 目的：让结果带有样本量、波动和比较口径，避免把一次成功或一个平均分当成稳定能力。

## 基础统计单元

对二元成功任务，设第 `i` 次 Trial 结果为 `x_i ∈ {0, 1}`：

```text
observed_success_rate = sum(x_i) / n
```

报告这个比例时同时给出：

- Task 数和每个 Task 的 Trial 数；
- 置信区间或重采样区间；
- 各任务切片结果；
- 超时、基础设施失败和重试的处理方式；
- 是否允许 best-of-N、人工选择或自动重试。

小样本或成功率接近 0/1 时，不要只用简单正态近似。可使用 Wilson 区间、精确二项区间或按 Task 分层的 bootstrap，并记录所用方法。

## 平均值会隐藏什么

相同总体成功率可能来自两种完全不同的系统：

- 所有任务都偶尔成功；
- 一半任务始终成功，另一半始终失败。

所以还要报告：

- 每个 Task 的成功分布；
- 最差切片和关键任务；
- 多次运行的方差；
- 延迟和成本的中位数、尾部分位数；
- 失败类型构成。

## pass@k

`pass@k` 回答：“允许生成或尝试 `k` 个候选时，至少一个成功的概率是多少？”它适合确实允许 best-of-k 的场景，不等于单次用户请求的可靠性。

若单次成功概率为 `p` 且各次独立同分布，理论值为：

```text
pass@k = 1 - (1 - p)^k
```

真实 Agent Trial 往往共享模型、Prompt、环境和失败模式，并不独立。不要仅用该公式从 `pass@1` 外推生产表现。

在 HumanEval 的采样设定中，对某道题生成 `n` 个样本，其中 `c` 个通过测试，论文使用的无偏估计形式为：

```text
1 - C(n - c, k) / C(n, k),  n >= k
```

这个估计器有明确采样前提，不能无条件套用到带状态、重试和自适应行动的长程 Agent。

## pass^k

一些 Agent 评测使用 `pass^k` 表达“连续 `k` 次都成功”的稳定性目标。若单次成功概率为 `p` 且各次独立同分布：

```text
pass^k = p^k
```

该记号不像 HumanEval 的 `pass@k` 那样有单一标准化估计流程。使用时必须自行定义：

- 连续运行还是无序重复；
- 环境是否每次重置；
- 任意一次超时是否视为失败；
- 重试是否属于同一次 Trial；
- 如何处理相关性和共享故障。

更直接的做法是按固定大小分组，报告“组内全部成功”的经验比例，并同时报告原始 Trial 序列。

## 比较两个系统

优先采用配对设计：版本 A 和 B 运行相同 Task、Fixture 和尽量一致的环境。比较：

- 每个 Task 的差值，而不只是两个总体均值；
- A 成功 B 失败与 B 成功 A 失败的数量；
- 关键切片是否回归；
- 成功任务的成本和延迟是否变化；
- 新增失败类型。

可根据指标使用配对 bootstrap、McNemar 检验或适合连续指标的配对方法。选择方法前检查独立性、分布和分层结构；不要只汇报 `p < 0.05`，还要汇报效果量和区间。

## 样本量

正式 Trial 数应由以下因素决定：

- 当前方差与基线成功率；
- 想检测的最小实际差异；
- 可接受的一类、二类错误；
- Task 和切片数量；
- 单次运行成本；
- 决策风险。

流程可以是：小规模 pilot → 估计方差 → 做功效或精度计算 → 冻结正式计划。不要在看到结果后不断追加 Trial，直到得到想要的结论。

## 多指标决策

Agent 系统通常同时优化质量、可靠性、延迟、成本和安全。建议：

1. 先定义不可违反的硬门禁。
2. 对主要目标给出非劣或改善区间。
3. 将次要指标保留为分项，不急于合并成总分。
4. 预先写出发布决策规则。
5. 对大量切片和指标控制多重比较与“挑好看结果”的风险。

## 报告最小项

```yaml
sample:
  tasks: 120
  trials_per_task: 5
estimate:
  metric: "task_success"
  value: "..."
  interval_method: "stratified bootstrap"
comparison:
  design: "paired"
  baseline_version: "..."
exclusions:
  infrastructure_failures: "count and rule"
```

数值只是报告格式示例。

## 来源

- [Chen et al.: Evaluating Large Language Models Trained on Code](https://arxiv.org/abs/2107.03374)
- [OpenAI HumanEval reference implementation](https://github.com/openai/human-eval)

下一步：[Trace 与失败归因](05-traces-and-failure-analysis.md)。
