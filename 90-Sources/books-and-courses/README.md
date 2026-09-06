# 教材与课程：补足推导所需的基础

这里按学习目的选材料。无需从第一章通读到最后一章：先在本库跑一个小实验，再回教材补上不理解的推导，最后修改实验验证理解。

核验日期：2026-09-06；范围为作者或出版社的目录、版本与介绍页面，未逐章复核全书。

| 材料与版本 | 适合补什么 | 推荐阅读路径 | 本库连接与边界 |
| --- | --- | --- | --- |
| [Dive into Deep Learning](https://d2l.ai/)，网页标识 1.0.3 | 把数学、张量运算和训练代码连起来 | 第 2 章先补线性代数与自动微分；第 3–5 章看损失与训练；第 11 章看 Q/K/V、注意力评分、多头与 Transformer；第 12 章看优化 | 配合 [AI 基础](../../10-Knowledge/01-ai-foundations/README.md) 和 [基础模型](../../10-Knowledge/02-foundation-models/README.md)。官方提供多框架实现，运行时固定书中框架和依赖，不混抄不同后端代码 |
| [Deep Learning](https://www.deeplearningbook.org/)，Goodfellow、Bengio、Courville，2016 | 概率、数值稳定性、反向传播与泛化的系统解释 | 第 2–5 章补数学与机器学习；第 6–8 章补前馈网络、正则化、优化；第 11 章读实验方法 | 用于核对基础推导；出版时间早于 Transformer，不能据此确认现代 LLM 的具体架构或 API。作者提供在线阅读，免费阅读不等于可复制整章进仓库 |
| [Reinforcement Learning: An Introduction](https://mitpress.mit.edu/9780262039246/reinforcement-learning/)，Sutton、Barto，第 2 版，2018 | 奖励、价值函数、探索、离策略学习与策略梯度 | 先读 Part I 的表格型问题，再进入 Part II 的函数逼近；先能手算一次价值更新，再看神经网络版本 | 配合 [强化学习入口](../../10-Knowledge/01-ai-foundations/01-concepts/reinforcement-learning/README.md) 和 [Agent 学习](../../10-Knowledge/12-agent-learning/README.md)。这里已核验出版社书目和内容介绍；本轮作者站访问失败，没有声称已下载或读完电子书 |

学完一个小节，用三个动作检查：给公式中的量填一组数、修改一个条件预测输出、运行代码看预测是否成立。只记住算法名称无法完成这三个动作，需要回到相应推导。

课程与教材有多个语言或框架版本时，以实际使用的版本为准。引用书中图表前还要单独核对复用条件；本索引只提供链接和阅读建议。
