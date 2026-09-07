# 学习目标的可运行算例

> 状态：verified · 更新：2026-09-06

[learning.py](learning.py)实现组泄露检查、masked NLL、DPO 数值目标、组内优势与两种奖励。所有输入为教学值，函数不创建/训练语言模型。

```bash
python -m unittest discover -s 10-Knowledge/12-agent-learning/05-code
```

环境：Python 3.12，标准库，无额外运行依赖。2026-09-06 实跑 4 个测试全部通过，覆盖组泄露、上下文掩码、DPO 基点与同分组、伪造成功/越权奖励。

对应[概念文章](../README.md)与[已执行 Notebook](../04-labs/01-trajectories-and-rewards.ipynb)。如果要把教学函数迁移到训练器，必须匹配 tokenization、序列损失归一化与目标实现；不能以通过这些函数测试代替训练验证。
