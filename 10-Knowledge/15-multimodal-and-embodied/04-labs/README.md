# 文档证据实验

> 状态：draft · 更新：2026-09-06

[01-document-evidence.ipynb](01-document-evidence.ipynb)使用同一张教学表，比较丢失行列关系的数字基线与结构查询，再拒绝错误数值、单位、页码与版本。先看[视觉与文档](../01-concepts/01-vision-and-document-ai.md)。

环境 Python 3.12；核心计算为标准库，Notebook 执行需要 IPython/Jupyter。2026-09-06 用独立进程 IPython 逐格实际执行 5 个代码单元并保存输出。该环境的 Jupyter kernel 通道被拒绝，所以未验证 kernel 协议；可复现实跑命令：

```bash
python scripts/check_notebooks.py --execute --backend ipython-fallback 10-Knowledge/15-multimodal-and-embodied/04-labs/01-document-evidence.ipynb
```

结构查询在 3 个已知人工问题上返回 3 个正确值，故意弱化的扁平基线返回 2 个。这个差异只演示结构作用，不能作为 OCR/VLM 真实准确率。实现与 4 个独立测试见[代码目录](../05-code/README.md)。
