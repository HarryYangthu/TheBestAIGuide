# 基础模型：可运行源码

> 状态：verified · 范围：2个NumPy教学Notebook验证的函数；没有真实LLM或GPU路径。

[model_mechanics.py](model_mechanics.py)提供小而完整的机制实现。只依赖NumPy，输入形状和掩码语义写在函数docstring中。

| 函数 | 计算内容 | 关键边界 |
|---|---|---|
| `train_bpe` / `bpe_encode` | 字符对子频次合并与固定规则编码 | 非byte-level；教学词尾标记不保证任意输入的生产转义 |
| `stable_softmax` / `attention` | 缩放匹配、可见性mask、V汇总 | mask True=可见；整行无合法候选时抛错 |
| `decode_distribution` | 正温度、top-k与top-p过滤 | greedy应使用argmax；保留跨过top-p阈值的token |
| `cached_attention` | 单层因果注意力逐token复用K/V | 不含FFN、RoPE或真实token生成 |
| `symmetric_quantize` | 2…8位对称均匀量化及重构 | int8是容器，低于8位没有实际位打包 |
| `kv_cache_bytes` | 标准K/V缓存容量公式 | 不包含allocator碎片、临时工作区和其他结构 |

在仓库根目录执行：

```bash
python -m pip install -r 10-Knowledge/02-foundation-models/05-code/requirements.txt
```

[实验入口](../04-labs/README.md)包含逐单元解释与真实输出；[Transformer正文](../01-concepts/transformer/README.md)与[推理正文](../01-concepts/inference/README.md)解释公式。DPO、LoRA和Pareto的短小演示在Notebook内完整实现，没有伪装成训练库。
