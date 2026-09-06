# 研究机制的最小算例

> 状态：verified · 更新：2026-09-06

[research_checks.py](research_checks.py)使用 Python 3.12 标准库：

```bash
python 10-Knowledge/16-research-frontiers/05-code/research_checks.py
```

2026-09-06 实跑并通过内置断言：独立假设下 `.98**50≈.36417`；三个独立准确率 .7 的判断多数票准确率 .784，完全相关时仍 .7；教学资源约束保留宽度 8；标量平方损失的一次更新将状态从 0 变成 1。

这些计算只解释假设与机制，没有调用 LLM、训练 TTT/Titans、运行 MuZero 或复现科研 Agent。连接[文章](../README.md)与[固定论文版本](../references.md)阅读，先问清论文验证了什么，再设计自己的任务实验。
