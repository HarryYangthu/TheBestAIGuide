# 数据来源与固定子集

本目录提供 HotpotQA distractor 的 120 条真实记录：源 train 的前 20 条作为教学开发集，源 validation 的前 100 条作为固定教学验收集。按源顺序选择，不按系统得分筛题。开发集与验收集问题 ID 不重叠；它们可能共享百科主题，这不是跨主题泛化评测。

数据通过 Hugging Face datasets-server 的 rows API 获取：

- https://datasets-server.huggingface.co/rows?dataset=hotpotqa/hotpot_qa&config=distractor&split=train&offset=0&length=20
- https://datasets-server.huggingface.co/rows?dataset=hotpotqa/hotpot_qa&config=distractor&split=validation&offset=0&length=100

获取时观察到的源 revision 为 `1908d6afbbead072334abe2965f91bd2709910ab`。rows API 并未绑定 revision，所以本项目以仓库内各 JSONL 的 SHA256 为可复现快照；不能声称 API 响应已与该 revision 的 Parquet 逐字比对。哈希在 [manifest.json](manifest.json)，运行时会校验。

每条记录保留问题、标准答案、context 和 supporting_facts。检索器只接收问题与文档；生成请求只接收问题与实际选中片段。标准答案和支持事实仅供评分、报告展示使用。证据句 ID 从 0 开始；不能把分块后的序号当原句号。

## 归属与许可

来源：[HotpotQA](https://hotpotqa.github.io/)，作者 Zhilin Yang、Peng Qi、Saizheng Zhang、Yoshua Bengio、William W. Cohen、Ruslan Salakhutdinov、Christopher D. Manning，EMNLP 2018。

[数据卡](https://huggingface.co/datasets/hotpotqa/hotpot_qa) 标注 **CC-BY-SA-4.0**。本目录中的数据及参考报告中再现的数据文本按同一许可证使用：https://creativecommons.org/licenses/by-sa/4.0/ 。文档文本来源于 Wikipedia；文档 title 保留了文章名称，可在 Wikipedia 查询原条目。这里做了子集选择、分文件和 JSON 序列化，没有人工更改答案或原文。数据许可不因本仓库其他代码许可而改变。

论文：HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering，https://aclanthology.org/D18-1259/ 。
