# ReAct 与先计划后执行：控制粒度怎样选

> 状态：draft | 来源核验：2026-09-06

问题不是“哪个名字更先进”，而是下一步行动依赖多少尚未取得的信息。搜索资料时，读到第一篇文章才知道还缺少实验条件，适合边读边决定。若要对十个固定文件做相同统计，先确定步骤再执行能减少反复规划。

ReAct 原论文把推理与环境动作交替组织，使观察影响后续选择。工程中可以保留“提出动作—取得观察—调整动作”的结构，而不要求输出或记录完整隐藏思维。Plan-and-Execute 则把计划作为独立对象，由执行器完成可检验的子任务，再决定是否重规划。Plan-and-Solve 是先规划再求解的提示方法，不能直接等同于已经具备调度器、持久状态和故障恢复的工程架构。

| 任务条件 | 合适选择 | 需要补的控制 |
| --- | --- | --- |
| 下一步取决于新证据 | ReAct式循环 | 步数预算、重复检测、证据检查 |
| 步骤稳定且可以验收 | 先计划后执行 | 依赖关系、每步完成条件 |
| 大任务方向稳定，局部需探索 | 上层计划＋局部循环 | 子任务预算、汇总与重规划条件 |

## 用同一个问题对照

“查找上下文预算建议”只需搜索一次，计划对象可能增加无意义调用。扩展成“比较预算分配和压缩策略，并各给一个失败例子”，可以先建立两个子任务：找到预算资料，找到压缩资料；两者完成后检查每个结论是否有文档ID。执行器发现压缩资料不存在时，应返回 `missing_evidence`，让规划器决定补检索或明确缺失，而不是自写一段看似完整的内容。

最小计划应包含 `id、输入、依赖、验收条件、状态`。不要只写“深入分析”“全面整理”，因为执行器无法判断完成。例如 `budget_docs` 的验收条件可以是“至少一条命中预算主题的文档，含ID与原文”。

```python
from agent_loop import EvidenceModel, default_tools, run_agent
plan = [("budget_docs", "预算"), ("compression_docs", "压缩")]
artifacts = {}
for task_id, query in plan:
    result = run_agent(EvidenceModel(), default_tools(), query, max_steps=3)
    artifacts[task_id] = result.observations[0] if result.observations else None
print({key: item["ok"] if item else False for key, item in artifacts.items()})
```

这段固定计划组合了同一个最小Loop，没有伪装成模型自主规划。实际计划更新应保留已完成产物，取消尚未开始且不再需要的步骤；不要遇到一个失败就从头跑整条链。

## 重规划什么时候触发

触发条件应是可观察差异：缺前置资料、工具永久不可用、需求改变或预计成本超预算。每轮都“反思并重新制定全面计划”会重复消耗上下文；完全不重规划又会沿错误假设继续执行。可以给计划设置版本，只在触发条件成立时修改，记录旧子任务被保留、替换还是取消。

源码从 [Loop](../05-code/agent-loop-python/src/agent_loop/loop.py) 进入；更完整的依赖与协作见 [规划与多Agent](../../08-planning-workflow-multi-agent/README.md)。原始资料：[ReAct](https://arxiv.org/abs/2210.03629)、[Plan-and-Solve](https://arxiv.org/abs/2305.04091)。
