# 基础模型实验运行记录

> 状态：verified · 执行日期：2026-09-06 · 验证对象：本域2本Notebook，共13个代码单元。

环境：Linux、Python 3.12.13、NumPy 2.5.2、IPython 9.17.1、nbformat 5.11.1、nbclient 0.11.0、ipykernel 7.3.0。每本独立IPython进程顺序运行并保存真实输出与断言结果；本环境Jupyter内核socket不可用，因此未验证内核通信与交互界面。没有调用LLM、GPU或远程API。

```bash
python scripts/check_notebooks.py --execute --backend ipython-fallback 10-Knowledge/02-foundation-models/04-labs/01-tokenization-and-attention.ipynb 10-Knowledge/02-foundation-models/04-labs/02-decoding-cache-and-precision.ipynb
```

| 检查 | 实际观察 | 结论边界 |
|---|---|---|
| [Notebook 01](01-tokenization-and-attention.ipynb) | 6/6代码单元通过 | 字符级机制，不是生产tokenizer |
| BPE | 确定性合并表，测试词均可按本示例规则还原 | 不支持任意输入的特殊标记转义保证 |
| QK与V | 缩放分数[1,0]；权重[0.731059,0.268941]；输出[7.310586,5.378828] | 改V后权重不变，内容汇总变化 |
| 缩放 | dk=4/16/64/256时缩放后方差约0.995/0.983/0.995/0.988 | 独立标准正态模拟，不代表训练后的真实分布 |
| Mask与RoPE | 改未来位置后过去输出差0；无mask差约102.073；RoPE两侧均约6.4305992 | 验证因果隔离和二维旋转等式 |
| [Notebook 02](02-decoding-cache-and-precision.ipynb) | 7/7代码单元通过 | 小矩阵/虚构候选，无真实模型效果 |
| 解码与缓存 | top-p=.8保留前两项；缓存与全因果计算最大误差2.22×10^-15 | 单层无FFN/RoPE的等价验证 |
| KV容量 | 32/8/1个KV头分别2/0.5/0.0625 GiB | B=1、L=32、T=4096、dh=128、2字节；公式估算 |
| 量化 | 8bit最大权重/输出误差约0.00964/0.03144；4bit约0.17239/0.59052 | 均匀对称量化，4bit未位打包，无速度声明 |
| DPO/LoRA | Δ=0/1/-1时loss约0.693/0.313/1.313；合并误差3.55×10^-15 | 验证损失方向和矩阵代数，没有真实微调 |
| 候选与选型 | 精确检查接受17与34/2；Pareto前沿A/B；硬约束组合无可行模型 | 人工候选/虚构配置，不是真实模型排名 |

保存的实验输出均来自本次实际运行。未验证范围包括真实LLM训练与推理、GPU时延、Prefix Cache隔离、推测解码服务、NF4/QLoRA训练、生产模型路由和上线收益。正文保持`draft`，实验`verified`仅表示上表的具体机制已运行。
