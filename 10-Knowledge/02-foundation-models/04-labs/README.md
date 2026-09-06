# 基础模型实验

> 状态：verified · 范围：2本Notebook共13个代码单元已真实执行，输入/权重/候选均为教学构造。

| 实验 | 检查内容 | 关联正文 |
|---|---|---|
| [01 Tokenization与Attention](01-tokenization-and-attention.ipynb) | 字符BPE、QK/V数值例子、缩放方差、因果mask、RoPE | [Tokenization](../01-concepts/tokenization/README.md)、[Transformer](../01-concepts/transformer/README.md) |
| [02 解码缓存与精度](02-decoding-cache-and-precision.ipynb) | Top-p边界、缓存等价、容量、量化、DPO/LoRA、验证器和Pareto | [推理](../01-concepts/inference/README.md)、[训练](../01-concepts/training/README.md)、[Reasoning](../01-concepts/reasoning/README.md)、[选型](../01-concepts/model-selection/README.md) |

先安装[依赖](../05-code/requirements.txt)，在Jupyter或支持Notebook的编辑器中从头运行。完整函数在[model_mechanics.py](../05-code/model_mechanics.py)，每本Notebook自动定位仓库根目录，无API key、无GPU、无需下载权重。

命令行也可执行：

```bash
python scripts/check_notebooks.py --execute 10-Knowledge/02-foundation-models/04-labs/01-tokenization-and-attention.ipynb
```

本次受执行环境socket限制，使用以下后端真实运行Python单元并保存输出：

```bash
python scripts/check_notebooks.py --execute --backend ipython-fallback 10-Knowledge/02-foundation-models/04-labs/01-tokenization-and-attention.ipynb 10-Knowledge/02-foundation-models/04-labs/02-decoding-cache-and-precision.ipynb
```

[运行记录](run-report.md)说明版本、结果和未验证范围。两本Notebook用于理解数学与实现的对应，不是完整Transformer训练、语言生成服务或真实模型选型工程。
