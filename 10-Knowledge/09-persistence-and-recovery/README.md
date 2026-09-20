# 09｜持久化与故障恢复

> 状态：seed｜已建立组件范围与阅读路线；分章正文、代码与实验待补充。

在进程退出或动作结果不明时，恢复进度并避免重复副作用。

## 按这个顺序展开

| 顺序 | 要实现和观察的内容 |
|---|---|
| 01 | 持久保存状态与检查点 |
| 02 | 区分未执行、已执行和结果未知的操作 |
| 03 | 用操作标识和幂等约定恢复任务 |

每一步将用可运行的示例说明输入、中间数据、标准输出和产物，完整教程采用 [Agent 执行循环](../03-agent-loop/README.md) 的逐步展开方式。

## 现有参考资料

以下正文已随原知识库归档，可先用于理解本组件：

- [持久执行](../_archive/09-runtime-harness-environment/01-concepts/02-durable-execution.md)

[组件总览](../README.md) · [上一组件：工具与执行环境](../08-tools-and-environment/README.md) · [下一组件：评估与验收](../10-evaluation-and-acceptance/README.md)
