# State 与 Memory

> 状态：seed
> 学习目标：先建立当前任务的权威状态模型，再理解哪些信息值得跨步骤或跨会话保存。

State 与 Memory 放在同一领域，是为了对比边界和串起生命周期，而不是把两者视为同一概念：State 回答“系统现在是什么状态”，Memory 回答“未来可能需要记住什么”。

## 前置知识

- [Agent Core](../03-agent-core/README.md)中的 Goal、Observation、Action 和 Agent Loop。
- [Context Engineering](../04-context-engineering/README.md)中的信息来源、信任、选择和注入。
- [Runtime 与 Harness](../09-runtime-harness-environment/README.md)中的 Run、Step 和执行生命周期，可在本领域之后继续深入。

## 连续学习顺序

1. [概念与边界](01-concepts/README.md)：State、Session、Checkpoint、Memory 与 Context。
2. 先理解 State 的权威性、精确读取和确定性更新。
3. 再理解 Memory 的选择性写入、检索、更新与遗忘。
4. [设计模式](02-patterns/README.md)：Checkpoint/Resume、Memory Write、Retrieval 和 Conflict Resolution。
5. [实验入口](04-labs/README.md)：比较无 Memory、全量历史与检索式 Memory。

## 当前证据边界

- 当前内容用于建立概念边界和后续写作结构，状态仍为 `seed`。
- 尚无可运行的 State Store、Memory Store、Checkpoint 或评测实验。
- 存储选型、召回策略和保留周期必须绑定具体任务、权限与数据验证，不能作为通用默认值。
