# State 与 Memory Labs

> 状态：seed；当前没有可运行 Notebook。

计划按以下顺序建立实验：

1. 保存 Session State，并从 Checkpoint 恢复未完成任务。
2. 比较无 Memory、全量历史和检索式 Memory。
3. 构造冲突、过期、撤回和跨用户记忆案例。
4. 对写入、召回、最终任务结果、Token、延迟和隔离分别评测。

实验必须保存输入、状态变化、Memory 命中、Context 注入和最终 Outcome，不能只根据模型回答判断成功。
