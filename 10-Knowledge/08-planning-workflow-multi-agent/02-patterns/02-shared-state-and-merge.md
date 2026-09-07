# 共享状态与合并：让冲突暴露出来

> 状态：draft；来源核验：2026-09-06；配套实现已进行本地 fixture 验证，非真实模型性能评测。


两个 Worker 都写 `decision`：先返回的写 A，后返回的写 B。如果协调器直接 `state.update(result)`，最终答案只取决于谁最后完成。这是时间竞争，不是综合判断。

合并策略应由字段含义决定。证据集合可以去重追加，互不重叠的候选评分可以按 ID 合并，最终选择则只能有一个明确的决策所有者。不能给所有字段统一套一个“覆盖旧值”的规则。

| 字段 | 合并方式 | 必要条件 |
|---|---|---|
| 文献证据列表 | 按 source_id + version 去重 | 不同版本保留区别 |
| 候选测量结果 | 按候选、指标、实验配置分组 | 单位和实验条件一致 |
| 子任务状态 | 按 task_id 汇总 | ID 唯一，明确最终状态 |
| 最终 decision | 单一协调器基于完整证据计算 | 必需评审均成功 |
| 同一参数的新值 | 版本比较或人工/程序解决冲突 | 不能靠完成先后决定 |

## 本例为什么先拒绝冲突

[merge.py](../05-code/multi-agent-runtime-python/src/multi_agent/merge.py)采用一个保守规则：同名字段的值相同就合并来源，值不同就抛出 `MergeConflict`。

```python
if key in values and values[key] != value:
    raise MergeConflict(f"{key}: conflicting results")
values[key] = value
owners.setdefault(key, []).append(result.task_id)
```

这样不会静默损失任何一份不同结论。`owners` 记录哪些任务返回了这个值，供后续追查。“值相同”只是避免无意义冲突，不证明这两个 Worker 有独立证据。

实际系统可以进一步分解冲突：A=18 ms、B=0.018 s 是单位差异；同一模型在两种硬件测得 18/28 ms 是条件差异；同一条件同一版本却给 18/28 ms 才需要检查测量错误。让模型投票之前，应先做这些确定性检查。

## 私有状态、共享事实、最终决策分开

Worker 的草稿、搜索历史和尝试错误属于私有状态；经过校验的证据是可提交的共享事实；最终决策由协调器拥有。本文代码不让 Worker 写共享对象，而是返回一个结果，等全部结果收集后统一合并。

这种设计的好处是过程容易重放，代价是长任务的中间进展不能实时改变别人。如果业务确实需要实时协作，采用版本化提交：读取版本 $v$，提交时要求当前版本仍为 $v$，否则重新读取并合并。这叫乐观并发控制。它适合冲突不频繁的场景；冲突密集时需要更细的状态分区或单写者队列。

## 部分成功不是最终成功

合并器返回三个对象：`values`、`missing_tasks` 和 `owners`。调用时应提供 `expected_task_ids`，这样不仅失败任务，连完全没返回的任务也会进入 `missing_tasks`；重复结果和未知任务结果会直接报错。若省略这个清单，`complete` 只表示传入的这些结果都成功，无法证明调用方没有遗漏任务。候选选择函数首先检查它：约束评审超时，即使质量分数齐全，也不能按最高分直接输出 B，因为 B 可能违反硬约束。

```python
from multi_agent import WorkerResult, merge_results

partial = merge_results(
    [WorkerResult("quality", "ok", {"quality": {"A": 0.91}})],
    expected_task_ids=["quality", "constraints"],
)
assert not partial.complete
assert partial.missing_tasks == ["constraints"]
```

这里约束任务连错误结果都没返回，完整任务清单仍然能发现缺口。这是一条可测试的业务不变量。Notebook 故意让一个 Worker 超时，展示剩余结果仍在，同时拒绝最终选择。继续读[单与多 Worker 对照案例](../03-cases/01-single-vs-multi-agent.md)。并发结果收集所依据的 API 语义见[Python 官方说明](https://docs.python.org/3/library/asyncio-task.html)。
