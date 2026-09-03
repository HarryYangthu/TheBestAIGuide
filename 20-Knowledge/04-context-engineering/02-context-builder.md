# Context Builder：把候选信息变成模型输入

> 状态：draft
> 目标：给出不依赖特定框架的构建流程和最小数据契约。

## 职责

Context Builder 位于信息源和模型调用之间，负责：

1. 收集候选信息。
2. 标注来源、信任、版本、时效和敏感度。
3. 应用硬性权限与安全规则。
4. 按当前子任务选择、去重和排序。
5. 在预算内转换为模型可消费的形式。
6. 输出构建记录，支持 Trace、回放和评测。

它不负责决定工具是否真的执行，也不负责把所有历史永久保存；这分别属于 Runtime 和 Memory/State。

## 输入契约

一个最小输入可以表示为：

```yaml
request:
  goal: "定位并修复支付回调重复入账"
  constraints:
    - "不得修改生产数据"
  acceptance:
    - "失败测试先复现，修复后通过"
state:
  current_step: "分析幂等键写入路径"
  open_items: []
candidates:
  - id: "repo:payment/webhook.py"
    kind: "workspace_file"
    trust: "workspace"
    version: "git:abc123"
    content: "..."
  - id: "trace:run-042"
    kind: "tool_result"
    trust: "runtime"
    observed_at: "2026-09-03T10:20:00+08:00"
    content: "..."
tools:
  - name: "run_tests"
    permission: "read_execute"
budget:
  max_input_tokens: 32000
```

数值只是 Schema 示例，不是推荐预算。

## 构建流水线

```python
def build_context(request, state, candidates, tools, budget):
    items = normalize(candidates)
    items = enforce_access_policy(items)
    items = mark_untrusted_instructions(items)
    items = drop_expired_or_wrong_scope(items)
    items = resolve_exact_duplicates(items)
    items = rank_for_current_step(items, request, state)
    items = transform_with_provenance(items, budget)
    envelope = pack(request, state, items, tools, budget)
    validate_invariants(envelope)
    return envelope
```

这里的顺序不是唯一实现，但有两个关键要求：安全门禁要早于语义排序；有损压缩后仍要保留来源和回读能力。

## 选择规则

### 先做硬过滤

- 当前主体无权读取的内容；
- 其他用户或租户的数据；
- 明确过期且不应作为历史证据的状态；
- 与当前环境版本不匹配的配置；
- 已标记为撤销、失败或污染的记忆。

### 再做软排序

排序可以综合当前步骤相关性、来源权威性、时间、具体程度和覆盖增益。不要只按向量相似度排序，因为高度相似的片段可能重复、过期或不可信。

### 最后做覆盖检查

在预算耗尽前，确认这些信息是否存在：

- 目标与验收条件；
- 不可违反的约束；
- 当前状态与未完成事项；
- 做出本轮决策所需的最小证据；
- 可用工具及其限制；
- 输出格式和停止条件。

## 预算分配

不要把固定百分比当作普适答案。更稳妥的做法是：

1. 为硬约束、当前请求和输出契约预留不可挤占空间。
2. 为模型输出和工具往返预留余量。
3. 候选证据按边际价值逐步加入。
4. 超出预算时，优先去重和删除无关项，再考虑摘要。
5. 记录被删除或压缩的内容，以便失败分析。

对于长任务，还要控制“下一轮会新增多少内容”，避免本轮刚好装满后无法继续工作。

## 输出契约

Builder 不应只返回最终消息，还应返回构建元数据：

```json
{
  "messages": [],
  "selected_item_ids": ["repo:payment/webhook.py", "trace:run-042"],
  "dropped": [
    {"id": "trace:run-001", "reason": "superseded"}
  ],
  "transformations": [
    {
      "output_id": "summary:trace-042",
      "source_ids": ["trace:run-042"],
      "method": "structured_extract",
      "lossy": true
    }
  ],
  "budget": {
    "estimated_input_tokens": 18200,
    "max_input_tokens": 32000
  },
  "warnings": []
}
```

这些数字同样只是格式示例。

## 确定性代码与模型的分工

优先使用确定性逻辑完成：

- 权限过滤；
- 版本、时间和作用域判断；
- 精确去重和固定格式解析；
- Token 估算和硬预算；
- Schema 校验；
- 敏感字段遮蔽。

模型更适合：

- 语义相关性判断；
- 查询改写；
- 开放文本摘要；
- 冲突线索提取；
- 在复杂目标下判断信息覆盖。

模型产出的排序或摘要仍需记录版本、输入和不确定性。

## 缓存与可变前缀

缓存优化不能只看命中率。应把上下文分为：

- 稳定前缀：系统策略、稳定工具 Schema、长期不变的示例；
- 任务级部分：本次目标、仓库状态、检索证据；
- 轮次级尾部：最新观察、工具结果和下一步计划。

稳定内容尽量保持字节级一致，可变内容追加在后；但当策略或工具版本改变时必须失效缓存，不能为了命中率继续使用旧约束。

## 最小测试集

Context Builder 至少需要覆盖：

- 预算不足时仍保留硬约束；
- 不可信文档中的命令不会覆盖系统策略；
- 过期状态被替换而非同时注入；
- 工具失败不会被转换成成功事实；
- 摘要带有原始来源和 `lossy` 标记；
- 相同输入和配置可重放构建结果；
- 跨用户数据不会混入；
- 关键冲突会产生警告或中止，而不是静默消解。

相关模式：[Context Builder 模式](../../30-Patterns/context/context-builder.md)。
