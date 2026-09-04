# 评测对象与系统模型

> 状态：draft

## 核心组件

| 组件 | 定义 |
| --- | --- |
| Task | 一项包含输入、初始状态、成功条件和评分配置的测试任务 |
| Trial | 某个固定 Task 的一次完整运行 |
| Trajectory | Trial 中可观测的消息、工具调用、路由、中间结果和错误时间线 |
| Outcome | Trial 结束后的真实环境状态与交付物 |
| Grader | 对 Outcome 或 Trajectory 的一个维度进行检查和计分的逻辑 |
| Agent Harness | 让模型循环调用工具、维护状态和终止任务的脚手架 |
| Evaluation Harness | 调度任务、隔离环境、采集数据、评分和汇总的基础设施 |
| Evaluation Suite | 围绕一组能力、场景或风险组织的 Task 集合 |

## 真正评测的是什么

一个结果必须绑定完整系统身份：

```yaml
system_under_test:
  application_version: "git-sha-or-release"
  agent_harness_version: "..."
  model_provider: "..."
  model_id: "..."
  model_snapshot: "..."
  inference_config: {}
  prompt_or_policy_version: "..."
  tool_versions: {}
  context_builder_version: "..."
  environment_image: "..."
```

只记录“用了某模型”无法复现实验，也无法判断回归来自模型、Prompt、工具还是 Harness。

## Outcome 优先，Trajectory 用于解释与约束

如果任务要求修改文件、写数据库或操作 UI，首先验证最终状态，而不是相信 Agent 的自述。

Trajectory 仍然重要，因为它可以判断：

- 是否使用了禁止工具；
- 是否访问不必要的敏感数据；
- 是否发生无效循环和重复调用；
- 错误从哪一步开始传播；
- 最终结果是否通过不可接受的路径得到。

不要要求记录模型不可见或供应商不提供的隐藏推理过程。可观测 Trace 应聚焦消息、工具调用、结构化决策、状态变化和错误。

## 能力、回归与风险不是同一个套件

| 套件 | 目的 | 数据特点 |
| --- | --- | --- |
| Capability | 系统能达到什么上限 | 较难任务，允许低初始通过率 |
| Regression | 已有能力是否退化 | 稳定、快速、版本固定 |
| Safety | 是否触发不可接受行为 | 对抗输入、权限和数据边界 |
| Reliability | 多次运行是否稳定 | 同任务多 Trial、环境重复初始化 |
| Production monitoring | 线上分布和失败是否变化 | 真实流量抽样，受隐私和偏差约束 |

不要用一个总分同时回答所有问题。

## 评测层次

```text
组件测试：解析器、工具、检索器、权限检查
  -> 节点测试：单个 Agent 或工作流步骤
  -> 工作流测试：路由、交接、恢复和状态
  -> 端到端测试：从请求到最终环境状态
  -> 线上观测：真实分布、反馈、漂移和事故
```

越靠下越接近真实价值，也越慢、越贵、越难归因。合理体系会组合各层，而不是只保留端到端分数。

## 好评测的属性

- **Valid**：测到的是实际关心的能力或风险。
- **Reliable**：重复评测的波动可解释。
- **Discriminative**：能区分不同系统版本，而不是全部满分或全部失败。
- **Actionable**：失败能定位到可修复的组件或行为。
- **Reproducible**：任务、数据、环境和配置可追踪。
- **Robust**：不会因为合法替代路径或格式差异误判。
- **Safe**：执行环境隔离，生成代码和外部动作受控。

下一步：[任务、数据集与 Trial](02-tasks-datasets-and-trials.md)。
