# 上下文工程评测

> 状态：draft
> 目标：判断某种 Context 策略是否让 Agent 更正确、更稳定、更高效，而不是只比较输入长度。

## 评测对象

先明确改变了哪一层：

- 候选信息源；
- 检索器或查询改写；
- 选择与排序规则；
- 摘要或结构化转换；
- 工具筛选；
- 记忆读取和写入；
- 上下文隔离或多 Agent 路由；
- Token、缓存和截断策略。

如果同时改变模型、Prompt、工具和数据，就很难归因效果。

## 任务集设计

至少覆盖：

| 任务类型 | 验证目标 |
| --- | --- |
| 必要事实检索 | 能否找到并使用关键证据 |
| 干扰信息 | 能否忽略相似但无关内容 |
| 冲突版本 | 能否按来源、时间和范围处理冲突 |
| 长对话 | 能否保留目标、约束与未完成事项 |
| 工具选择 | 工具较多时能否选对且不越权 |
| 错误恢复 | 失败工具结果是否被正确标记和利用 |
| 注入与泄露 | 不可信内容能否越权，敏感信息是否外泄 |
| 预算压力 | 压缩和截断时是否保留关键内容 |

任务应包含初始状态、成功条件、关键证据、干扰项和允许的动作，而不只是一个问题文本。

## 指标

### 结果质量

- 任务成功率和硬门禁通过率；
- 事实正确性、引用准确性和证据覆盖；
- 最终环境状态是否正确；
- 必要约束是否被遵守。

### 上下文质量

- `evidence_recall`：必要证据进入上下文的比例；
- `evidence_precision`：选中内容中真正有用的比例；
- `conflict_detection_rate`：已知冲突被识别的比例；
- `instruction_survival`：长任务后关键约束仍被遵守的比例；
- `provenance_coverage`：派生内容可追溯到原始来源的比例。

### 可靠性与效率

- 多次 Trial 的成功分布；
- 输入、输出、缓存 Token；
- 端到端延迟与各阶段延迟；
- 工具调用数、重试数和失败恢复成本；
- 单个成功任务的实际成本。

指标定义必须固定统计口径。例如“输入 Token”是否包含缓存读取，要在报告中说明。

## 基线与消融

建议至少比较：

1. **Full-context baseline**：尽可能保留全部候选信息。
2. **Minimal baseline**：只保留请求和必要系统指令。
3. **Current strategy**：当前生产或默认策略。
4. **One-change variant**：每次只改变一个选择、压缩或隔离策略。

使用同一任务版本、模型版本、工具环境和试验配置。对非确定性系统运行多次 Trial，并同时保留均值、分布和逐任务结果。

## Trace 要求

为了定位失败，每次 Trial 至少记录：

```yaml
run_id: "..."
task_version: "..."
model: "provider/model/version"
context_builder_version: "..."
candidate_item_ids: []
selected_item_ids: []
dropped_items:
  - id: "..."
    reason: "..."
transformations: []
token_usage: {}
tool_calls: []
outcome: {}
grader_results: []
```

正文、工具参数和结果可能包含 PII、密钥或业务数据。遥测应默认最小化，必要时脱敏或仅保存哈希与引用。

## 失败归因

将失败分类到具体阶段：

- **Source failure**：正确信息不存在或无法访问。
- **Retrieval failure**：正确信息存在但未召回。
- **Selection failure**：召回后被错误过滤。
- **Transformation failure**：摘要或结构化过程改变了含义。
- **Packing failure**：信息被错误排序、截断或与冲突内容混合。
- **Reasoning failure**：正确上下文已提供，但模型未正确使用。
- **Action failure**：决策正确，但工具或环境执行失败。
- **Grader failure**：成功条件或评分器本身错误。

只有完成归因，才能决定该改 Context、模型、工具还是评测。

## 发布门禁示例

以下是结构示例，不是通用阈值：

```yaml
release_gate:
  hard_requirements:
    - "permission_violations == 0"
    - "secret_leaks == 0"
  compare_with_baseline:
    - "task_success_not_worse"
    - "critical_task_regressions == 0"
  report_only:
    - "input_tokens"
    - "latency"
    - "cost_per_success"
```

阈值应基于业务风险、样本量和历史波动制定，不能从示例直接复制。

相关内容：[Evaluation 与 Observability](../../10-evaluation-observability/README.md)。
