# 基础模型：来源与核验范围

> 状态：draft · 核验日期：2026-09-06

以下条目均来自原论文或出版方页面，已实际浏览核验。标有v号的条目记录具体arXiv版本；仅列年份与arXiv号的条目表示核验日条目快照，未冻结其HTML渲染。已读取摘要不等于复现论文实验，核心公式的核验范围另列。本文不使用论文中的商用模型排名推断当前排名。

## 输入与结构

| 编号 | 来源、版本 | 支持的具体主张 | 已核验范围与限制 |
|---|---|---|---|
| M1 | Sennrich et al.，[Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909v5)，2016 | 用子词缓解固定词表的稀有词问题，BPE作为分割方法 | 原论文条目与摘要；本库字符BPE不等于目标模型的byte tokenizer |
| M2 | Wu et al.，[Google's Neural Machine Translation System](https://arxiv.org/abs/1609.08144v2)，2016 | WordPiece用于子词输入/输出 | 原论文条目；不宣称所有WordPiece训练器同一种打分实现 |
| M3 | Kudo，[Subword Regularization](https://aclanthology.org/P18-1007/)，ACL 2018 | Unigram子词模型、分割采样与多分割训练 | ACL出版页；本库概率例子独立构造 |
| M4 | Vaswani et al.，[Attention Is All You Need](https://arxiv.org/html/1706.03762v7)，2017论文，v7为2023修订 | Q/K/V、缩放假设、softmax、mask、多头、FFN与位置编码 | 实际读取第3节正文及缩放脚注；原创矩阵算例和代码另行运行 |
| M5 | Su et al.，[RoFormer](https://arxiv.org/html/2104.09864v5)，2021论文 | RoPE通过旋转让Q/K匹配含相对位置 | 读取HTML；本库仅验证二维旋转等式，没有长上下文质量实验 |
| M6 | Shazeer，[Fast Transformer Decoding: One Write-Head is All You Need](https://arxiv.org/abs/1911.02150)，2019 | MQA共享K/V以减少解码读写 | 原论文条目；无硬件速度复现 |
| M7 | Ainslie et al.，[GQA](https://arxiv.org/html/2305.13245v3)，2023 | 多组查询头共享KV头与MHA/MQA之间的取舍 | 读取HTML；不保证任意checkpoint直接合头后质量不变 |
| M8 | Fedus et al.，[Switch Transformers](https://arxiv.org/abs/2101.03961)，2021 | 稀疏专家路由、总参数和激活计算的区别 | 原论文条目；MoE不是多Agent，未运行专家训练 |
| M9 | Touvron et al.，[LLaMA](https://arxiv.org/abs/2302.13971)，2023 | 现代decoder模型的架构实例 | 原论文条目；不把单一架构细节写成所有Transformer统一定义 |
| M10 | Dao et al.，[FlashAttention](https://arxiv.org/abs/2205.14135)，2022 | 基于IO意识的精确注意力实现 | 原论文条目；不声称成对注意力运算变成线性复杂度 |

## 训练、对齐与推理

| 编号 | 来源、版本 | 支持的具体主张 | 已核验范围与限制 |
|---|---|---|---|
| M11 | Hoffmann et al.，[Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556)，2022 | 固定训练计算预算下数据与参数的分配 | 摘要与条目；不作为所有场景固定比例定律 |
| M12 | Ouyang et al.，[Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155)，2022 | 指令示范、偏好与RLHF训练流程 | 摘要与条目；未复现人类标注或PPO训练 |
| M13 | Bai et al.，[Constitutional AI](https://arxiv.org/abs/2212.08073)，2022 | 用AI反馈参与训练的具体研究实例 | 摘要与条目；AI反馈不代表无偏真值 |
| M14 | Schulman et al.，[Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347)，2017 | PPO是策略优化算法，区别于完整RLHF流程 | 原论文条目；本域没有PPO训练器 |
| M15 | Rafailov et al.，[Direct Preference Optimization](https://arxiv.org/html/2305.18290v3)，2023论文，v3为2024修订 | 偏好对、参考模型相对对数概率差、DPO损失 | 读取HTML正文；只运行标量损失计算，没有模型训练 |
| M16 | Shao et al.，[DeepSeekMath](https://arxiv.org/html/2402.03300v3)，2024 | GRPO组相对优势与策略更新的提出 | 读取HTML；只讲原始方法的核心，不混用后续训练器变体 |
| M17 | Hu et al.，[LoRA](https://arxiv.org/html/2106.09685v2)，2021 | 冻结基座，训练低秩更新；合并权重 | 读取HTML；本库验证矩阵等价与零初始化梯度，不复现微调效果 |
| M18 | Dettmers et al.，[QLoRA](https://arxiv.org/html/2305.14314v1)，2023 | 量化冻结基座＋LoRA、NF4等设计 | 读取HTML；均匀INT4教学例不冒充NF4实现 |
| M19 | Holtzman et al.，[The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751v2)，ICLR 2020 | Nucleus/top-p采样与解码分布 | 原论文条目；本库验证阈值边界，不复现生成文本质量 |
| M20 | Chen et al.，[Accelerating Large Language Model Decoding with Speculative Sampling](https://arxiv.org/html/2302.01318v1)，2023 | 草拟、验证、接受/残差采样保持目标分布 | 读取算法2与第4节；本库用p表示目标、q表示草稿，符号与论文相反但定义明确；未实现推测服务 |
| M21 | Kwon et al.，[PagedAttention](https://arxiv.org/abs/2309.06180v1)，SOSP 2023 | KV内存碎片、分页管理与共享 | 原论文摘要与条目；不借用论文吞吐倍数为本库结果 |
| M22 | Hinton et al.，[Distilling the Knowledge in a Neural Network](https://arxiv.org/abs/1503.02531v1)，2015 | 教师信息用于训练较小模型 | 摘要与条目；没有蒸馏训练实验 |

## 推理能力与选型

| 编号 | 来源、版本 | 支持的具体主张 | 已核验范围与限制 |
|---|---|---|---|
| M23 | Wei et al.，[Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903)，2022 | 中间步骤提示这一方法及研究范围 | 摘要与条目；不保证对所有模型/任务有收益 |
| M24 | Wang et al.，[Self-Consistency](https://arxiv.org/abs/2203.11171)，2022 | 多路径生成与答案聚合 | 摘要与条目；独立候选成功概率公式为本库概率推导，现实可能相关 |
| M25 | Lightman et al.，[Let's Verify Step by Step](https://arxiv.org/abs/2305.20050)，2023 | 过程监督与结果监督的区分 | 摘要与条目；不把步骤评分当严格证明 |
| M26 | Liang et al.，[Holistic Evaluation of Language Models](https://arxiv.org/abs/2211.09110v2)，2022论文，v2为2023修订 | 多场景、多指标、统一条件下比较 | 原论文摘要与条目；本文Pareto示例数据为虚构，不是真实模型成绩 |

## 文章与证据连接

[Tokenizer](01-concepts/tokenization/README.md)对应M1–M3；[Transformer](01-concepts/transformer/README.md)对应M4–M10；[训练](01-concepts/training/README.md)对应M11–M18；[推理](01-concepts/inference/README.md)对应M6/M7/M19–M22；[Reasoning](01-concepts/reasoning/README.md)对应M23–M25；[选型](01-concepts/model-selection/README.md)对应M26。

实际运行证据位于[实验入口](04-labs/README.md)和[运行记录](04-labs/run-report.md)。无API key、无GPU、不下载权重的数值实验只能证明实现的具体机制，不能证明语言模型在真实任务上的表现。

[回到领域入口](README.md)。
