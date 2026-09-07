# 深度学习实验

> 状态：verified · 范围：标量自动微分与四点XOR训练已执行。

运行[自动微分与训练Notebook](01-autograd-and-training.ipynb)。先验证`w*w+w`的共享参数梯度，再比较tanh链式法则的手推、自动微分和有限差分，最后训练2→4→1网络。

[深度学习正文](../../01-concepts/deep-learning/README.md) · [完整代码](../../05-code/foundations_core.py) · [依赖与运行方法](../README.md) · [结果记录](../run-report.md)。本实验不依赖PyTorch，不代表真实数据泛化评估。
