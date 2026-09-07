# RAG Labs

> 状态：verified
> 执行日期：2026-09-06；Python 3.12.13；5 个代码单元真实执行并保存输出。

打开 [01-hybrid-retrieval-evaluation.ipynb](01-hybrid-retrieval-evaluation.ipynb)，依次观察文档替换、查询排名、无答案、三通道消融、RRF/nDCG 手算与删除后引用失效。配套[源码工程](../05-code/rag-pipeline-python/README.md)可单独运行。

本次使用每本独立 Python 进程中的 IPython 顺序执行。环境禁止 Jupyter TCP/IPC socket，因此尚未验证本环境中的 Jupyter 内核通信；代码单元和断言已执行，输出未模拟。可从仓库根目录用 `python scripts/check_notebooks.py --help` 查看统一执行方式；正常本地 Jupyter 环境可直接 Run All。

实验包参考版本：nbformat 5.11.1、IPython 9.17.1；Jupyter nbclient 0.11.0、ipykernel 7.3.0 可用于有内核通信能力的环境。核心 Pipeline 无第三方依赖。

数据为人工教学语料，5 个可回答查询中 4 个成功召回；BM25/Hybrid 的平均 Recall@3 均为 0.8，Exact 为 0.4。3 个空答案边界均正确返回空。本 Notebook 不运行真实向量、Reranker 或生成模型，详见[运行报告](../05-code/rag-pipeline-python/run-report.json)。

## 标准内核验证更新（2026-09-06）

提交 `5e5a40c09e00028c7887fd3bf3bd559d96fc972f` 的 [GitHub Actions 标准 Jupyter 执行](https://github.com/HarryYangthu/TheBestAIGuide/actions/runs/34013521515)已成功。原 Notebook 保存输出的本地 IPython 来源保留；这条更新补充标准内核证据，不代表交互控件或所有前端已验收。进一步可读[真实检索结果](../../../20-Projects/learning-workbench/artifacts/real-models/retrieval.json)和[生成审阅](../../../20-Projects/learning-workbench/artifacts/real-models/generation-review.json)，二者使用另一组数据；本 Notebook 的 0.8 不能与那里的分数直接比较。
