# Pattern：Context Builder

> 状态：draft

## 问题

Agent 的信息来自系统策略、用户、状态、检索、工具和环境。如果让每个调用点自行拼接消息，权限、版本、预算和来源规则会逐渐分叉，失败也难以重放。

## 适用条件

- 系统有多种动态信息源；
- 一项任务跨越多轮或多个工具；
- 需要控制 Token、敏感数据和来源；
- 需要对上下文选择做 Trace、回放或评测。

## 方案

在模型入口前建立统一构建层：

```text
Candidate Sources
      ↓
Normalize + Label
      ↓
Policy Gate
      ↓
Select + Transform
      ↓
Pack + Validate
      ↓
Context Envelope + Build Record
```

每个候选项至少带 `id`、`kind`、`source`、`trust`、`scope`、`version/time` 和内容引用。构建结果除模型消息外，还返回选中项、丢弃原因、转换记录、预算和警告。

## 不变量

- 权限过滤先于相关性排序；
- 有损转换保留来源和回读路径；
- 硬约束不被低优先级内容覆盖；
- Builder 不隐式执行有副作用动作；
- 相同输入、配置和版本可以重建或解释结果。

## 代价

- 增加数据建模与 Trace 存储；
- 需要维护版本、失效和敏感字段策略；
- 排序与摘要可能引入新的模型依赖；
- 统一入口若设计不当会成为性能瓶颈。

## 反模式

- 只返回最终 Prompt，不记录选择过程；
- 把权限检查交给语义相关性模型；
- 所有信息只有一个混合分数；
- 超预算时直接从尾部截断；
- 摘要覆盖原文且无法追溯。

## 验证

用固定任务比较启用前后：任务成功、硬约束、证据召回、冲突处理、多次运行稳定性、Token、延迟和每次成功成本。至少加入预算压力、提示注入、过期状态和跨租户隔离测试。

详细设计见：[Context Builder 知识笔记](../../20-Knowledge/04-context-engineering/02-context-builder.md)。
