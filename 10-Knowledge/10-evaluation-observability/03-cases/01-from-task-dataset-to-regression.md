# 从任务数据到回归：给“查资料”建立一个能发现错误的评测

> 状态：draft
> 核验日期：2026-09-06；配套代码、四条教学任务与 Notebook 已实际执行。
> 数据属性：人工构造的公开教学 fixture；没有真实业务日志，没有独立专家标注，也没有 LLM Judge。

假设一个知识查询服务很容易演示成功：输入问题，返回资料。但它还有两条必要约束：只能返回当前租户的知识；版本不匹配时不能拿别的版本充数。只有正常请求测试通过，看不出它会不会在这些边界上犯错。本例从四条任务出发，把问题写进数据，再用状态和输出定位到具体代码。

## 1. 先定义系统要做什么

输入是 `tenant + version`，测试环境存一条带所属租户和版本的记录。被测函数可以读取环境中的记录，但对外输出必须服从访问范围。这里为了展示失败，fixture 含“受限记录”；真实服务应把读取权限放在独立存储/API 层，不能把所有秘密都交给模型再要求它不说。

成功条件不是“语气谨慎”，而是如下结果：

| Task | 请求与记录的关系 | 预期输出 | 为什么必要 |
| --- | --- | --- | --- |
| valid | 租户、版本都相同 | 返回记录、来源 ID、不拒答 | 合法请求不能被一律拒答 |
| wrong-tenant | 租户不相同 | 不返回记录、不带来源 ID、拒答 | 检测跨主体数据泄漏 |
| old-version | 请求 v1，只有 v2 | 拒答并说明没有匹配资料 | 检测版本适用性 |
| missing-version | 请求不存在版本 | 拒答 | 检测兜底逻辑是否偷偷返回默认版本 |

每个任务还要求最终 `lookups=1`，证明这一次 Trial 使用了独立初始化的状态。标记 wrong-tenant 与 old-version 为关键任务，是本教学案例的规则，不是通用行业阈值。

## 2. 数据文件和标签如何组织

[fixtures/tasks.jsonl](../05-code/eval-harness-python/fixtures/tasks.jsonl)每行是一项完整 Task。简化其中一条：

```json
{
  "id": "wrong-tenant",
  "version": "1",
  "input": {"tenant": "beta", "version": "2"},
  "fixture": {
    "record": {"id": "doc-001", "tenant": "alpha", "version": "2", "value": "教学值：读取日志"},
    "lookups": 0
  },
  "expected": {
    "output": {"answer": "no accessible evidence", "source_id": null, "abstained": true},
    "state": {"lookups": 1}
  },
  "tags": ["permission"],
  "critical": true
}
```

`expected` 不传给被测函数。公开输入与评分标签分开，是为了避免系统直接读出标准答案。但它们仍位于同一 Python 进程，无法对抗恶意代码窥探；安全评测应使用隔离进程与独立评分服务。

这四条不是从生产数据抽样，不能声称代表真实查询分布。若迁移到业务：先从已获准使用的失败记录抽取请求、初始状态和真正结果；去敏后由熟悉业务的人确认标签；按客户/文档族划分开发和测试，避免相同模板泄漏；再补版本、权限、无答案等稀缺边界。写上来源窗口、标签依据和审核人，而不只留一句问题。

## 3. 评分代码具体检查什么

[graders.py](../05-code/eval-harness-python/src/eval_harness/graders.py)对 output 与最终 state 分别检查。字典允许未要求的额外字段，给定字段必须值和类型都一致；这避免把 Python 中的 `1 == True` 误当正确布尔结果。

```python
# 这是解释性片段；完整实现负责缺字段和递归类型检查。
checks = {
    "output:abstained": output["abstained"] is True,
    "output:source_id": output["source_id"] is None,
    "state:lookups": fixture["lookups"] == 1,
}
passed = all(checks.values())
```

该规则适合明确字段协议；回答的自由措辞不应被硬性规定为唯一字符串。案例里 `answer` 使用固定输出，是为了演示一个可完全确定的基线。如果产品允许多种等价措辞，可把协议改为 `reason_code="NO_ACCESSIBLE_EVIDENCE"`，将自然语言展示与任务判定分开。

[测试文件](../05-code/eval-harness-python/tests/test_harness.py)包括“自述成功但状态不变”“禁止字符串出现在额外字段”“输入类型偷换”等反例。没有独立人工标签和真实 Judge 运行，本例不报告“Judge 校准准确率”。

## 4. 每次 Trial 如何运行

Harness 对 input 和 fixture 分别深拷贝，运行函数，记录显式事件，读取最后状态，评分并保存结果。函数异常计为 `system_error`，仍进入总体分母，没有悄悄把失败样本删掉。当前实现不根据异常类型猜测是模型失败还是基础设施故障，需在接入实际环境时更细分类。

```python
from eval_harness import run_suite, summarize, compare
from eval_harness.cli import baseline, candidate, load_tasks

tasks = load_tasks("fixtures/tasks.jsonl")
old = run_suite(tasks, baseline, trials=2)
new = run_suite(tasks, candidate, trials=2)
print(summarize(old))
print(summarize(new))
print(compare(old, new))
```

完整运行入口：[工程说明](../05-code/eval-harness-python/README.md)。每项重复两次是用于确认状态重置；确定性代码不会因此产生两个独立的真实业务样本。

## 5. 读实际结果，定位首次差异

2026-09-06 本地运行，基线仅正常任务成功：2/8 Trial；候选版 8/8。按四项 Task 统计是 1/4 与 4/4，结果来自同一任务各重复两次。

| 观察 | 基线 | 候选版 | 应得结论 |
| --- | --- | --- | --- |
| 正常路径 | 2/2 | 2/2 | 修复没有用“全部拒答”骗过边界测试 |
| 错租户 | 0/2 | 2/2 | 明确的租户分支已补齐 |
| 两类版本不匹配 | 0/4 | 4/4 | 明确版本检查已补齐 |
| Fixture 状态 | 每次 lookups=1 | 每次 lookups=1 | 本组可变对象没有跨 Trial 污染 |

基线错租户的第一条业务事件是 `lookup(scope_checked=False)`；候选版先记录 `filter(authorized=False,current=True)` 后拒答。差异发生在访问范围判断，所以修复落在逻辑层。更换提示词或提高模型温度与这个故障没有关系。

注意这些 emit 事件由示例函数产生，尚不是不可伪造审计日志；真正读数据的权限事件应由独立 Runtime 记录。

## 6. 修复后为什么还要故意回退一次

回归门禁要求任务版本、Trial 编号、关键标记和切片都一致。候选版不得让已通过的配对 Trial 退化；关键任务必须全过。`compare(old,new)` 通过，而 `compare(new,old)` 阻断，并指出 wrong-tenant、old-version、missing-version 三项退化。

这是明确逻辑门禁，不是统计非劣检验。对于随机模型，可在预先定义容忍度与样本量后使用按 Task 配对的统计方法；不要看到分数下降才修改门禁。

## 7. 迁移到真正的 RAG/Agent

将 candidate 换成真实系统适配器，接口仍保持 `system(request, fixture, emit) -> dict`。fixture 可以提供受控语料和工具状态；输出保存答案及引用；独立 grader 验证来源可读、版本一致、主张支持和最终副作用。需要 API 或费用时显式配置，不在测试中隐式联网。

接入 [RAG Pipeline](../../06-rag-and-knowledge-systems/05-code/rag-pipeline-python/README.md)后，至少把失败分成：没有召回、召回错范围、引用失效、证据不充分、生成不支持、工具未完成。每种失败对应具体组件，优化才有方向。

运行记录：[Notebook](../04-labs/01-evaluation-and-regression.ipynb)、[基线汇总](../05-code/eval-harness-python/reports/baseline/summary.json)、[候选汇总](../05-code/eval-harness-python/reports/candidate/summary.json)、[比较结果](../05-code/eval-harness-python/reports/comparison.json)。Task/Trial/Outcome 分工参考 [Anthropic 一手说明](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)，具体 fixture、函数与结果为本库原创教学实验。

## 评分配置错误也不能算成系统能力失败

审阅中发现一个实际反例：`expected.output` 若误写为数组，评分器访问 `.items()` 会异常。加载阶段现在要求 output/state 为字典、禁止词为非空字符串数组，错误任务在运行前被拒绝，避免把评分配置缺陷计成被测系统失败。对应回归见测试中的 `test_bad_grader_configuration_rejected_before_run`。
