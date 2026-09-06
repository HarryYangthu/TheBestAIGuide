# 综合项目

本目录只保存跨越多个知识领域的完整工程，例如同时包含 Context、Tools、Memory、Runtime、Evaluation 和应用界面的 Agent 系统。

单个领域的学习代码放在 `10-Knowledge/<domain>/05-code/`。只有具备清晰目标、运行说明、依赖、源码、测试和验收记录的端到端工程才进入本目录。

当前项目：[领域资料研究助手](domain-research-agent/README.md)。它复用 Agent Loop、RAG、State/Memory、Runtime 事件存储和 Eval Harness，验证引用、租户隔离、拒答与进程故障恢复。默认使用确定性策略和本地构造资料，无需 API Key。
