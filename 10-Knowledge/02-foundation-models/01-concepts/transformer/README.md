# Transformer：Attention 如何匹配信息，再把信息读回来

> 状态：draft · 来源核验：2026-09-06 · 配套实验验证数值机制，没有训练语言模型。

Attention 做了两步：先计算当前位置与各候选位置的匹配程度，再按匹配程度汇总候选位置携带的内容。$QK^T$ 负责算“该关注谁”，乘 $V$ 负责算“从它那里拿到什么”。只说“关注重要信息”太宽泛，必须把这两步的对象和数值对应起来。

## 1. Q、K、V 不是三份原始文本

设当前层输入 $X\in\mathbb R^{T\times D}$，每行是一个 token 的当前表示。单头中：

$$Q=XW_Q,\qquad K=XW_K,\qquad V=XW_V.$$

$W_Q,W_K:(D,d_k)$，$W_V:(D,d_v)$ 都是训练得到的参数。因而 $Q,K:(T,d_k)$，$V:(T,d_v)$。同一个输入被投影到不同功能的空间：Query 表示当前位置如何查询，Key 表示候选如何参与匹配，Value 表示被读取的内容。这是功能上的区分，不是人为给每维预先贴好语义标签。

对第 $i$ 个查询与第 $j$ 个候选，$s_{ij}=q_i^Tk_j=\sum_rq_{ir}k_{jr}$。矩阵 $QK^T$ 就是一次性算出所有 $(i,j)$ 的点积分数，形状 $(T,T)$，行是查询位置，列是候选位置。也可写为 $x_iW_QW_K^Tx_j^T$，可见匹配规则由训练改变。

可以把它直观理解为“相关程度计算”，但它不是 Pearson 相关系数：没有减去样本均值，也没有除以两个向量的标准差；分数受方向与长度共同影响，没有固定在 $[-1,1]$。它也不是天生对称的，因为 $W_Q$ 与 $W_K$ 通常不同。高注意力权重不自动代表对最终答案有高因果重要性。

## 2. 为什么要除以根号 $d_k$

假设初始化附近 $q_r,k_r$ 相互独立、均值为 0、方差为 1，不同维乘积也独立，则：

$$E[q_rk_r]=0,\quad \operatorname{Var}(q_rk_r)=E[q_r^2]E[k_r^2]=1,$$
$$\operatorname{Var}\left(\sum_{r=1}^{d_k}q_rk_r\right)=d_k.$$

所以未缩放点积的典型幅度随 $\sqrt{d_k}$ 增大，除以 $\sqrt{d_k}$ 后方差约为 1。训练后的 Q/K 不一定满足独立、单位方差假设；这个推导说明设计动机，不是声称每层每步方差都严格等于 1。

这一步尤其关乎 softmax：分数差很大时，一个候选权重逼近 1，其他逼近 0，令 softmax 的实际输入为 $z=s/\sqrt{d_k}$，梯度 $\partial a_j/\partial z_k=a_j(\mathbf1_{j=k}-a_k)$ 很容易变小；若对未缩放的 $s_k$ 求导，还要乘 $1/\sqrt{d_k}$。缩放降低维度增大带来的过早饱和风险，但无法保证权重永远均匀，也不应该让它永远均匀。

例如分数 `[0,2]` 的 softmax 约为 `[0.119,0.881]`，而 `[0,20]` 已几乎是 `[0,1]`。二者排序相同，对分数微小变化的敏感度却大不相同。配套 Notebook 用随机 Q/K 展示不同 $d_k$ 的点积方差，再比较缩放后的方差。

## 3. Softmax、Mask 与 V 怎样接起来

每个查询位置只在候选位置轴归一化：

$$a_{ij}=\frac{\exp(s_{ij}/\sqrt{d_k}+M_{ij})}{\sum_\ell\exp(s_{i\ell}/\sqrt{d_k}+M_{i\ell})},\qquad o_i=\sum_ja_{ij}v_j.$$

$M_{ij}=0$ 表示可见，$-\infty$ 表示不可见。Softmax 后每行权重非负、和为1，因此单头输出是 Value 向量的加权平均。它把任意分数变成可比较的权重；候选之间会竞争，一个候选权重变化会影响其他候选。这里的 softmax 是对“位置”的分布，最终语言模型输出层的 softmax 是对“词表 token”的分布，二者不要混淆。

取一个可手算的例子：$q=[\sqrt2,0]$，$k_1=[1,0],k_2=[0,1]$，$d_k=2$。缩放分数是 `[1,0]`，权重约 `[0.731,0.269]`。若 $v_1=[10,0],v_2=[0,20]$，输出约为 `[7.311,5.379]`。如果保持 Q/K 不变，只把第二个 Value 改成 `[0,200]`，权重完全不变，但输出第二维变成约 53.788。这正是“匹配”和“内容”两步的区别。

因果掩码令位置 $i$ 只能看 $j\le i$。训练语言模型时，第 $i$ 个位置预测下一个 token，不能偷看未来答案。Padding mask 另行排除补齐位置；打包多个样本时还可能需要块状 mask 隔离样本。掩码在 softmax **之前**添加，不能先 softmax 再随便清零而不重新归一化。

```python
# Q:(T,dk), K:(T,dk), V:(T,dv)；当前为不含batch的教学实现
scores = Q @ K.T / np.sqrt(Q.shape[-1])
allowed = np.tril(np.ones((len(Q), len(K)), dtype=bool))
scores = np.where(allowed, scores, -np.inf)
if not np.isfinite(scores.max(axis=-1)).all():
    raise ValueError('每个query至少需要一个合法key')
scores = scores - scores.max(axis=-1, keepdims=True)
weights = np.exp(scores)
weights /= weights.sum(axis=-1, keepdims=True)
output = weights @ V
```

减去行最大值不会改变 softmax，因为分子分母同时乘同一个常数，但可以避免指数溢出。一整行都被屏蔽时，`-inf - (-inf)` 会产生 NaN；应在输入/掩码层处理空行，不能期待 softmax 自动理解“没有信息”。

## 4. 从单头到多头，再到 GQA/MQA

多头为同一输入学习多组投影，并行汇总不同表示子空间的信息，拼接后通过 $W_O$ 混合。它不是简单把同一个结果复制 $H$ 次。常见形状为：

| 张量 | 形状 | 每个轴的含义 |
|---|---|---|
| 输入 | $(B,T,D)$ | 批次、位置、通道 |
| Q | $(B,H_Q,T,d_h)$ | 每个查询头的向量 |
| K/V | $(B,H_{KV},T,d_h)$ | 用于匹配和读取的头 |
| 分数/权重 | $(B,H_Q,T_q,T_k)$ | 每个头内查询到候选的关系 |
| 合并输出 | $(B,T,H_Qd_h)$ | 先转置再合并头维 |

标准 MHA 中 $H_Q=H_{KV}$；MQA 让全部查询头共享一组 K/V；GQA 让一组查询头共享一组 K/V，$1<H_{KV}<H_Q$。它们减少 KV Cache 和读缓存流量，但改变了容量与训练行为，不能事后随意复制/平均头就保证原模型质量。分组映射要匹配 checkpoint，头维转置也要严格检查。

## 5. 位置编码让相同内容在不同位置有不同关系

没有位置表示和其他位置信息时，双向 self-attention 对输入排列是等变的，难以区分“甲追乙”和“乙追甲”的顺序。绝对位置编码把位置向量加到输入；原始 Transformer 用不同频率的正余弦。

RoPE 将 Q/K 的成对维度按位置旋转。二维旋转为 $R(\theta)=\begin{bmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{bmatrix}$，位置 $m,n$ 的点积满足：

$$(R(m\theta)q)^T(R(n\theta)k)=q^TR((n-m)\theta)k.$$

由于 $R(m\theta)^TR(n\theta)=R((n-m)\theta)$，点积自然含相对位移。实际不同维度对使用不同频率。RoPE 一般作用于 Q/K，不等于“把位置加到 V”。缓存解码时新 token 的绝对位置偏移必须连续；长上下文扩展还涉及频率缩放与训练分布，不能从公式直接推出任意长度外推能力。

## 6. Transformer 不只有 Attention

注意力在位置间交换信息；逐位置 FFN 在特征维做非线性变换，例如 $\mathrm{FFN}(x)=\phi(xW_1+b_1)W_2+b_2$。Residual 保留原表示，Normalization 稳定尺度。常见 pre-norm 块可写为 $u=x+\mathrm{Attn}(\mathrm{Norm}(x))$、$y=u+\mathrm{FFN}(\mathrm{Norm}(u))$；原始论文采用 post-norm，读代码应以具体架构为准。RMSNorm 按均方根缩放，通常不减均值，不能与 LayerNorm 混为一谈。

MoE 常替换 FFN：路由器给各专家打分，只激活选中的少数专家，再按路由权重合并输出。总参数量大不代表每 token 全部参与计算；但专家仍需存储/分发，路由负载不均和跨设备通信会造成瓶颈。其效果取决于专家训练、路由与容量控制，不能把“多专家”直接等同于“多个 Agent”。

Encoder 通常使用双向 self-attention，适合构建输入表示；decoder-only 用因果 self-attention 逐 token 生成；encoder-decoder 还通过 cross-attention 让解码端 Q 读取编码端 K/V。Cross-attention 中 $T_q$ 与 $T_k$ 可以不同，因此掩码不能机械假设正方形。

## 7. 改代码前的四个检查

先检查张量轴，再检查 mask 中 True 究竟代表可见还是屏蔽；不同 API 可能不同。随后检查 softmax 的轴和精度，最后用“改变未来输入不影响过去输出”验证因果性。缓存版本应与全前缀重算逐步对比，关闭 Dropout 后在浮点容差内一致。

标准注意力显式存储分数需要 $O(T^2)$ 空间，长序列会昂贵。FlashAttention 用分块与融合减少高带宽内存读写，并保持同一注意力数学目标；它不是把所有成对交互都变成线性复杂度，也不保证不同内核逐位相等。

[动手：矩阵算例、缩放方差、Mask 与 RoPE](../../04-labs/01-tokenization-and-attention.ipynb) · [源码](../../05-code/model_mechanics.py) · [继续：解码与缓存](../inference/README.md) · [来源及各主张范围](../../references.md)。
