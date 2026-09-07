# 模型训练：预训练、微调、偏好优化到底分别改变什么

> 状态：draft · 来源核验：2026-09-06 · 本文先讲训练机制，配套 tiny-transformer 已执行构造语料上的预训练、LoRA/SFT 和 DPO；未运行完整 RLHF 或大规模 LLM 微调。

训练要先回答“当前缺的是知识、行为格式，还是选择偏好”。预训练从大量数据中学习预测规律；监督微调用示范告诉模型怎样回答；偏好优化让它在多个可能答案中倾向某一类。三者可组合，但不是任何问题都应先微调。

## 1. 下一个 token 预测为何能作为训练目标

自回归模型把序列概率分解为 $P_\theta(x_{1:T})=\prod_{t=1}^TP_\theta(x_t\mid x_{<t})$。给定真实序列，最小化：

$$L_{PT}=-\frac1N\sum_{\text{有效位置 }t}\log P_\theta(x_t\mid x_{<t}).$$

$N$ 是有效 token 总数。训练输入和目标错开一位，并用因果 mask 保证每个位置只能看过去。多个位置的损失可以并行计算，因为所有真实前缀都已知；推理时下一个 token 尚未生成，因此通常逐步进行。这叫 teacher forcing，训练时看到的正确前缀与推理时自己的错误前缀不同。

Encoder 的 masked language modeling 根据部分遮挡输入预测被遮挡 token；encoder-decoder 的去噪目标从损坏文本重建原文。不同目标对应不同可见性，不能把所有基础模型都写成同一种因果训练。

数据质量包括去重、格式清理、语言与领域配比、授权/敏感信息处理和评测集隔离。更多 token 可能带来重复、污染和噪声，不等于更多有效知识。Scaling law 是特定数据、模型和训练范围内拟合的规律；Chinchilla 类结果讨论固定训练计算预算下参数量与数据量的分配，不是任意任务的通用比例保证。

## 2. Continued Pre-training 与 SFT 如何选择

| 现象 | 更直接的训练方向 | 先检查什么 |
|---|---|---|
| 领域语言/结构陌生 | 持续预训练：继续预测领域文本 | 是否有足量高质量语料，通用能力是否回退 |
| 会答但格式与任务步骤不稳定 | SFT：训练输入到高质量示范 | 示范是否一致，输入格式是否与部署一致 |
| 多种答案都像样，但选择偏好不符 | 偏好数据与优化 | 标注标准是否明确、差异是否真实 |
| 事实需要频繁更新与引用 | 先考虑检索/工具 | 权重更新并不提供逐条可追溯来源 |

SFT 仍常用 token 交叉熵，但需要 loss mask。设 $m_t\in\{0,1\}$ 表示这个位置是否参与训练，$L=-\sum_tm_t\log p_\theta(y_t\mid x,y_{<t})/\sum_tm_t$。只监督 assistant 回复时，用户和系统 token 的 $m_t=0$，但它们仍参与前向作为上下文。多轮工具轨迹是否训练工具消息、角色标记等，必须明确。分母为零的样本应排除或报错。

```python
# log_probs 和 mask 都为 (T,)；已选取每个位置真实目标token的log概率
if mask.sum() == 0:
    raise ValueError('样本没有受监督位置')
loss = -(log_probs * mask).sum() / mask.sum()
```

先用三个字符检查“哪个位置不计损失”。prompt 为 `Q`、answer 为 `xy` 时：

| 位置 j | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 输入 | BOS | Q | x | y |
| 移位后的目标 | Q | x | y | EOS |
| SFT 标签 | 忽略 | x | y | EOS |

第 1 个位置虽然输入是 prompt 的最后一个字符 Q，但它预测的是答案第一个字符 x，必须参与损失。不能按“输入属于 prompt”直接屏蔽整段。对应实现是 [supervised_batch](../../../../20-Projects/tiny-transformer/src/tiny_transformer/model.py)；PyTorch 使用目标值 `-100` 表示忽略，并在有效目标上求平均，见 [2.8 版 CrossEntropyLoss](https://docs.pytorch.org/docs/2.8/generated/torch.nn.CrossEntropyLoss.html)。

## 3. 偏好训练的共同目标与不同做法

RLHF 常先收集偏好对，用它训练奖励模型，再通过强化学习优化策略，并约束偏离参考模型的程度。RLAIF 使用 AI 提供部分反馈或偏好，不能自动消除偏差；反馈模型和原则会影响训练方向。PPO 是可用于策略优化的一种算法，RLHF 是数据与训练流程，两者不是同义词。

DPO 可直接使用偏好对 $(x,y_w,y_l)$。定义相对参考模型的对数概率差：

$$\Delta=\left[\log\pi_\theta(y_w\mid x)-\log\pi_{ref}(y_w\mid x)\right]-
\left[\log\pi_\theta(y_l\mid x)-\log\pi_{ref}(y_l\mid x)\right],$$
$$L_{DPO}=-\log\sigma(\beta\Delta).$$

$y_w$ 是偏好答案，$y_l$ 是较差答案，$\beta>0$ 控制目标中的参考约束尺度。序列对数概率通常是回答 token 的对数概率之和，不能随便替换成平均而仍声称是同一损失。若 $\Delta=0$，损失为 $\log2\approx0.693$；$\beta\Delta=1$ 时降到约 0.313。它鼓励偏好答案相对于参考模型提升得更多，不要求每个单独概率都绝对上升。DPO 不显式训练一个独立奖励模型，但仍依赖偏好质量和建模假设。

例如 reference 对好、差答案的 log 概率分别为 -4、-5，当前模型为 -3、-5。reference 的差值是 1，当前差值是 2，所以 $\Delta=2-1=1$。两边必须使用同一个 prompt、分词与回答边界；prompt 不纳入序列分数，回答结束标记是否纳入要一致。本项目包含 EOS。实际损失用 `-logsigmoid(beta * delta)`，避免先算 sigmoid 再取对数带来的下溢。

GRPO 的原始动机是用同一问题的一组采样答案形成奖励基线，减少单独 value model 的需求。简化的结果奖励优势为 $\hat A_i=(r_i-\bar r)/(\operatorname{std}(r)+\epsilon)$，随后用带概率比与裁剪的策略目标更新，并可加入 KL 约束。它不等于“奖励标准化后反传”；采样策略版本、token mask、裁剪方式和 KL 估计都影响实现。组内奖励全相同，优势几乎为零，无法凭空产生学习信号。具体完整目标应查对应版本论文和训练器，不能混合不同实现的公式。

### PPO 的 clip 到底限制了什么

优势 $A_t$ 表示这次动作比基线好多少；正值希望提高它的概率，负值希望降低。令 $\rho_t=\pi_\theta(a_t\mid s_t)/\pi_{old}(a_t\mid s_t)$，旧策略固定。PPO 最大化的一个代理目标为：

$$J_{clip}=\mathbb E_t[\min(\rho_t A_t,\operatorname{clip}(\rho_t,1-\epsilon,1+\epsilon)A_t)].$$

取 $\epsilon=0.2$：

| 优势与概率比 | 未裁剪项 | 裁剪项 | 取较小项 | 为什么 |
|---|---|---|---|---|
| $A=1,\rho=1.5$ | 1.5 | 1.2 | 1.2 | 好动作已涨太多，不再奖励继续涨 |
| $A=-1,\rho=0.5$ | -0.5 | -0.8 | -0.8 | 坏动作已降太多，不再奖励继续降 |
| $A=-1,\rho=1.5$ | -1.5 | -1.2 | -1.5 | 坏动作反而更常发生，保留惩罚 |

代码做梯度下降，所以最小化的是 $-J_{clip}$。clip 不是硬保证概率比永远在区间内，也不是对最终 loss 随便截断。公式来源为 [PPO 论文 v2 第 3 节](https://arxiv.org/pdf/1707.06347v2)；[tiny 项目](../../../../20-Projects/tiny-transformer/README.md)只演示两动作的一步更新，完整训练还需采样轨迹、优势估计和多轮策略更新。

## 4. LoRA 省在哪里，QLoRA 又改了什么

把线性层写为列向量形式 $y=Wx$，其中 $W:(d_{out},d_{in})$。LoRA 冻结 $W$，学习低秩更新：

$$y=Wx+\frac\alpha r BAx,\quad A:(r,d_{in}),\ B:(d_{out},r).$$

可训练参数从 $d_{out}d_{in}$ 变成 $r(d_{in}+d_{out})$。例如两边都是4096、$r=8$，矩阵本体约1678万参数，两个低秩矩阵共65,536参数。这里省的是适配器梯度与优化器状态等，不是把完整基座权重变没；反向仍可能需要中间激活。

常见初始化为 A 随机、B 为零，使初始增量为零；若二者都为零，则彼此梯度都被另一方乘成零。训练后可在兼容精度下合并 $W'=W+\alpha BA/r$，但多适配器、量化权重和动态切换的部署路径需单独处理。

QLoRA 在冻结的低比特基座上训练 LoRA，并包含特定量化和内存管理设计。不能把任意 INT4 推理权重配上 LoRA 就宣称完整复现 QLoRA，也不能把 NF4 当成普通均匀四比特整数。NumPy Notebook 先验证矩阵与标量损失；[tiny-transformer](../../../../20-Projects/tiny-transformer/README.md) 再用可训练模型检查冻结参数、LoRA 合并和 DPO 更新。它没有实现 QLoRA。

## 5. 训练前后如何验收

首先在小数据上验证 label shift、loss mask、可训练参数和梯度确实正确。再固定开发集和保留测试集，记录任务成功、格式合法、通用能力、拒答/越权、成本与延迟。增加训练轮次可能强化坏样本和记忆，不应把训练损失越低当作唯一目标。更新后的模型、tokenizer、模板、数据版本和适配器必须一起登记。

[实验：DPO 数值、LoRA 零初始化与矩阵等价](../../04-labs/02-decoding-cache-and-precision.ipynb) · [基础反向传播与训练](../../../01-ai-foundations/04-labs/deep-learning/01-autograd-and-training.ipynb) · [一手来源](../../references.md)。更完整的轨迹训练见 [Agent Learning](../../../12-agent-learning/README.md)。

## 沿着一个真正更新的参数读代码

先打开 [tiny-transformer 训练入口](../../../../20-Projects/tiny-transformer/src/tiny_transformer/experiment.py)：预训练更新全模型；SFT 冻结基座、只更新 `head.a/head.b`；DPO 沿用适配器并另存冻结 reference。查看[项目的标签表与产物说明](../../../../20-Projects/tiny-transformer/README.md)，再运行其 Notebook。

自检：prompt 的标签被忽略后，prompt 是否还影响答案？仍影响前向和答案的梯度路径。B 初始化为零时，第一步 A 为什么没动？A 的局部梯度乘了 B。参考模型为什么要冻结？否则 DPO 比较的基准会跟着当前模型一起移动。
