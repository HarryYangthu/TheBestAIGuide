# 从 token 到训练与生成：一个能跑完的小 Transformer

这个项目把分词、Embedding、多头 Attention、FFN、残差、训练和生成接在一起。模型只有约 3 万参数，用 CPU 学几句构造文本。你可以检查每个张量，也能看到 loss 下降；生成流畅度和真实任务能力不是这个实验的验收目标。

先读[Attention 与 Transformer](../../10-Knowledge/02-foundation-models/01-concepts/transformer/README.md)，再打开 [model.py](src/tiny_transformer/model.py)。训练入口是 [experiment.py](src/tiny_transformer/experiment.py)，保存的实际结果在 [report.json](artifacts/report.json)。

初次学习按这个顺序：先在 [Notebook](01-train-and-inspect.ipynb)看输入 ID 与移位标签，再手动展开第一层 Attention，接着训练并检查参数变化，最后比较缓存与完整计算。需要掌握矩阵乘法、交叉熵和梯度下降；不熟悉时先看[数学与统计](../../10-Knowledge/01-ai-foundations/01-concepts/math-and-statistics/README.md)和[深度学习](../../10-Knowledge/01-ai-foundations/01-concepts/deep-learning/README.md)。

## 运行

在仓库根目录执行，Python 3.12：

```bash
python -m venv .venv
source .venv/bin/activate
pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
python scripts/run_python.py -m tiny_transformer.experiment --output .runs/tiny-transformer
python scripts/run_python.py -m unittest discover -s 20-Projects/tiny-transformer/tests -v
```

Windows PowerShell 的环境激活命令为 `.venv\Scripts\Activate.ps1`；后续 Python 命令相同。若已有仓库虚拟环境，直接使用它，不需要再创建一份。Notebook 的执行依赖见仓库根目录 [requirements-dev.lock](../../requirements-dev.lock)。

输出包括训练记录、预训练权重、SFT/LoRA 权重和一段真实生成。仓库中的两个 `.pt` 文件是本项目在构造语料上训练的小权重，不是下载的大模型。只加载可信的模型文件。

## 1. 先把字符变成向量

`CharacterTokenizer` 给每个字符分配整数 ID。0、1、2、3 分别表示 padding、开始、结束、未知字符。空格和换行也是字符，未知字符变成 3，不会悄悄被删除。

Embedding 是查表。设词表大小为 $V$，向量宽度为 $d$，参数矩阵 $E\in\mathbb R^{V\times d}$；输入 ID 为 5，就取第 5 行。这里还加上可学习的位置向量，否则相同字符出现在不同位置时，输入表示没有顺序区别。

| 阶段 | 张量形状 | 含义 |
| --- | --- | --- |
| 输入 ID | `[B,T]` | B 条序列，每条 T 个 token |
| 查表并加位置 | `[B,T,d]` | 每个位置一个 d 维向量 |
| 拆成 H 个头 | `[B,H,T,d/H]` | 每个头用较小空间计算关联 |
| 注意力分数 | `[B,H,T,T]` | 每个查询位置对每个来源位置的分数 |
| 词表输出 | `[B,T,V]` | 每个位置预测下一个 token 的 logits |

字符分词只是为了看清实现。真实分词器的中文、代码、emoji 与聊天模板开销见[学习工作台](../learning-workbench/README.md)。

## 2. Attention 到底算了什么

当前位置先生成一个查询向量 $q_i$，每个可读取位置生成键 $k_j$ 和值 $v_j$。$q_i^T k_j$ 是可学习的匹配分数：它衡量“当前位置要找的信息”与“那个位置提供的索引”是否匹配。它不是统计学上归一化的相关系数，也不是固定的词语相似度。

$$
A=\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}+M\right),\qquad O=AV.
$$

这里做了三件事：先对每对位置打分，再把同一行的分数变成权重，最后对值向量加权求和。Softmax 沿“被读取的位置”这一维做，每行和为 1；数值相差越大，权重越集中。权重是本层的计算结果，不能直接当作模型的因果解释。

为什么除以 $\sqrt{d_k}$？若 $q$、$k$ 的各维近似独立、均值 0、方差 1，那么点积是 $d_k$ 项的和，方差约为 $d_k$。维度增大时分数幅度变大，Softmax 容易过早集中，梯度变小。除以平方根让量级相对稳定。这是初始化附近的尺度分析，不是保证训练中各维始终独立。

因果 mask $M$ 把未来位置设为负无穷，使其权重为 0。测试会修改输入末尾 token，确认前面位置的 logits 不变。多头随后拼回 `[B,T,d]`，再经过输出投影。

对照源码时注意两个实现约定：`qkv` 用一个线性层同时算三组投影，再由 `chunk(3)` 拆开；PyTorch 的 `Linear` 权重存为 `[out,in]`，所以批量行向量实际计算 `x @ weight.T + bias`，与正文列向量形式 `Wx` 是同一个运算。这个模型有投影偏置，NumPy 算例为了看清机制省略了偏置。

## 3. Attention 后面还有什么

每层采用 pre-norm：先归一化，再做 Attention，结果加回原输入；然后再归一化、通过两层 FFN，加回一次。FFN 在每个位置独立地做非线性变换，Attention 则负责跨位置传信息。残差给信息和梯度保留直接通路。

最后一层把 d 维表示映射到 V 个 logits。训练用交叉熵，生成时本实验用 argmax。argmax 是可复现的贪心解码，不等于质量最优的生成策略。

## 4. 标签为什么要移一位

输入 `BOS a b` 时，监督目标应是 `a b EOS`。当前位置只能看到当前位置及以前的信息，因此要预测的是下一个 token。如果输入和标签不移位，模型可能学会复制当前 token。

SFT 的输入是 `BOS + prompt + answer + EOS`。我们保留 prompt 作为上下文，但把对应的目标标签设为 `-100`，让交叉熵忽略它们。注意：prompt 不直接计入 loss，不代表 prompt 的隐藏状态完全不参与反向传播；答案的 Attention 仍会读取它。

例如 prompt=`Q`、answer=`xy`，实际张量如下：

| 位置 | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 输入 x | BOS | Q | x | y |
| 下一个 token | Q | x | y | EOS |
| 训练标签 y | -100 | x | y | EOS |

所以第一个答案标签位于 `len(prefix)-1`。若把 prompt 的最后一个输入位置也屏蔽，就会漏学答案的开头。

`supervised_batch` 只在右侧补 PAD，并把相应标签设为 `-100`。本模型虽然没有单独的 padding attention mask，有效位置也看不到未来的右侧 PAD，所以有效 logits 与逐条计算一致，测试会检查这一点。这不能推广到左 padding、双向注意力或多个样本打包：那些情况必须另加可见性与位置处理。生成入口拒绝带 PAD 的输入，长度不同的 prompt 请分别生成。

[测试](tests/test_decoder.py)明确检查第一个答案字符落在正确预测位置，并验证被忽略位置的 logits 梯度为 0。

## 5. LoRA 的参数在哪里更新

本例只对词表输出层增加低秩更新：

$$W'=W_0+\frac{\alpha}{r}BA.$$

$W_0$ 冻结，$A$ 和 $B$ 可训练。初始化 B 为零，所以起初输出与原模型一致；第一次更新时 A 的梯度可能为零，B 先发生变化，之后 A 才得到梯度。每次参数遍历都可以检查 `requires_grad`。

这里 $W_0:(V,d)$、$A:(r,d)$、$B:(V,r)$，本实现固定 $\alpha=r$，因此 `LoRAHead.forward` 中缩放系数为 1，没有漏乘一个可配置的系数。它只改词表输出层，Attention 和 FFN 都冻结；这与在多层 Q/V 上加适配器是不同实验，不能由这两条 SFT 样本推断哪种挂载方式更好。

实验比较训练前后冻结权重、合并前后输出、保存重载后输出。只验证 loss 下降是不够的：误把全模型解冻也可能下降，但那不是 LoRA。

接着用偏好对跑 12 步 DPO：比较当前模型对 chosen/rejected 的序列对数概率，并减去冻结参考模型对应的差值。这里的 reference 是真实模型快照，不是手填常数。最后给一个两动作策略做一次真实梯度更新，展示 PPO 正、负优势的 clipping；它不包含 value model、GAE 或完整 rollout，不能称为完整 PPO 训练器。

## 6. KV Cache 最容易错在位置

生成下一个 token 时，旧位置的 K/V 可以复用。新 query 仍然要读取全部旧 K/V。缓存长度为 P、新输入长度为 T 时，mask 应允许新位置 i 读取到 P+i，而不是只到 i；位置 Embedding 也必须从 P 开始。

本例对同一前缀分别整段计算和带缓存计算，在浮点容差内对比 logits。测试还覆盖一次追加两个 token，能发现只适用于单 token 追加的错误 mask。

例如 P=3、一次追加 T=2：第一个新 query 位于绝对位置 3，可读 key 0…3；第二个位于 4，可读 0…4。两行不能都只读新块内的位置 0…i。`generate` 将输入和输出总长度限制在 `max_length` 内；批内一条序列遇到 EOS 后只补 PAD，其他序列继续，避免“先结束的回答又长出后文”。

## 怎么读训练产物

| 文件或报告字段 | 保存的阶段 | 如何解释 |
|---|---|---|
| `pretrained.pt`、`sample` | 预训练之后、SFT 之前 | `sample` 是预训练模型的贪心输出，不是 DPO 后的答案 |
| `sft-lora.pt`、`sft_prediction_ids_after` | SFT 之后、DPO 之前 | 保存适配器及基座；预测 ID 来自 teacher forcing，不等于自由生成正确率 |
| `dpo_loss` | SFT 后再更新 12 步 DPO | 本例记录训练损失，不保存独立 DPO checkpoint |
| `policy_probabilities_*` | 独立两动作策略的一次 PPO 更新 | 与字符模型不是同一组参数，不代表字符模型已完成 PPO 对齐 |

`pretraining_loss` 和 `sft_loss` 记录首轮与末轮**更新前**的 batch loss；checkpoint 在该轮更新后保存，重新测量 checkpoint 的 loss 可能略有不同。SFT 对有效回答 token 求平均，DPO 对回答（含 EOS）的 log 概率求和，两个 loss 数字不能横向比较大小来判断哪个训练阶段更好。

## 已运行的结果与边界

固定 seed=7、CPU、PyTorch 2.8.0，预训练 loss 从约 3.253 降到 0.00118；SFT 从约 3.995 降到 0.00359。缓存最大差约 $1.67\times10^{-6}$，LoRA 合并最大差约 $3.81\times10^{-6}$。原始数值以报告为准。

这些都是训练语料上的结果，主要说明实现能够学习并正确保存。需要区分训练改善和独立任务效果时，运行工作台的 [CPU 对照实验](../learning-workbench/artifacts/science/report.json)：它固定训练/验证划分，分别保存数据、配置和逐步 loss。

原理出处：[Transformer](https://arxiv.org/abs/1706.03762)、[LoRA](https://arxiv.org/html/2106.09685v2)、[DPO](https://arxiv.org/html/2305.18290v3)、[PPO](https://arxiv.org/pdf/1707.06347v2)。DPO 差值、PPO 正负优势的逐项算例见[训练章节](../../10-Knowledge/02-foundation-models/01-concepts/training/README.md)。本项目是简化教学实现，未复现论文完整架构、训练规模或论文指标。
