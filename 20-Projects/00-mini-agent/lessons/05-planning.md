# 05：计划是可修改的工作记录

```bash
python 20-Projects/00-mini-agent/run.py run --stage 5 --mode demo --output .runs/mini-plan
```

在 `trace.jsonl` 中搜索 `update_plan`。第一次计划先查找资料；随后 `release-notes.md` 不存在；第二次计划改用目录中存在的两份正式说明；报告写出后更新为 done。每次修改有 `reason`，最终计划也保存在 `run.json` 的 `plan`。

[planning.py](../mini_agent/planning.py) 检查步骤结构和状态值。模型调用的是一个普通工具，宿主没有另写“必须按这三步执行”的控制循环。live 模式下是否需要修改、修改为什么样由模型决定；demo 为了复现写好了这条轨迹，不能把它解释为模型自主重规划的证据。

计划能暴露执行意图，却不能证明任务完成。一个模型完全可能把所有步骤改成 done，但报告内容仍错误。因此计划字段不参与替代 [evaluate.py](../mini_agent/evaluate.py) 的内容验收。

**练习：** 把 demo 的最终计划状态改成 pending 再运行：事实清单仍可能通过。然后把报告的 `after` 改错再验收：即使计划全是 done，也应失败。分别说明计划状态、运行状态和任务验收结果的含义。

关联知识：[规划与多 Agent](../../../10-Knowledge/08-planning-workflow-multi-agent/README.md)。
