# 结构化证据检索与验证

> 状态：verified · 更新：2026-09-06

[evidence.py](evidence.py)定义带版本、页码、行列、单位和区域框的 `Cell`，并实现精确结构查询、扁平基线与引用核验。

```bash
python 10-Knowledge/15-multimodal-and-embodied/05-code/evidence.py
python -m unittest discover -s 10-Knowledge/15-multimodal-and-embodied/05-code
```

Python 3.12 标准库，无模型下载和 API key。2026-09-06 实跑 4 个测试通过，覆盖正确证据、错误数值/单位/位置/版本、缺失与重复证据。详细中间输出见[Notebook](../04-labs/01-document-evidence.ipynb)。

输入是人工标注的教学表，代码没有做 PDF 解析、OCR 或向量计算。自然语言支持关系也不在这个验证器范围内；不能把格式有效当作任意回答被证据支持。返回[概念导航](../README.md)。
