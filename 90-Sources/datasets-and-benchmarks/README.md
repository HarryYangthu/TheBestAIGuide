# 数据集与评测基准：先选任务，再选分数

不同基准测量的能力不同。检索命中、函数测试通过、网页最终状态正确、仓库问题修复，不能都叫成同一种“Agent 成功率”。先明确系统要交付什么，再选相应判分器。

核验日期：2026-09-06。下表已读取官方仓库 README，并解析、核对固定提交。仅进行来源与任务定义核验，未下载数据全集、构建环境或运行外部基准。完整代码提交记录见 [代码仓索引](../repositories/README.md)。

| 基准与读取快照 | 输入、输出与判分 | 适合本库哪条学习路径 | 使用时必须固定什么／不能推出什么 |
| --- | --- | --- | --- |
| [HumanEval](https://github.com/openai/human-eval/blob/6d43fb980f9fee3c892a914eda09951f772ad10d/README.md)，代码快照 `6d43fb9` | 输入函数提示，输出补全代码，执行测试后统计 `pass@k`；保留通过、失败、超时的逐样本结果 | [评测与可观测性](../../10-Knowledge/10-evaluation-observability/README.md)：学习代码结果判分与多样本统计 | 固定题目文件、补全格式、每题样本数、采样设置、超时和隔离环境。函数测试通过不能直接代表大型仓库修改能力；公开题目还需考虑训练污染 |
| [BEIR](https://github.com/beir-cellar/beir/blob/ef83d29307061c65d04b035b4f4e7c18bd8374af/README.md)，代码快照 `ef83d29` | 输入语料、query 和相关性标注 qrels，输出排序结果；提供 nDCG、Recall、MAP 等检索指标 | [RAG](../../10-Knowledge/06-rag-and-knowledge-systems/README.md)：先比较检索器，再测最终回答 | 固定子数据集、split、下载文件校验值、query 提示、截断与 top-k。BEIR 汇集多个任务；跨任务平均值会掩盖薄弱领域。检索好不等于答案有依据 |
| [WebArena](https://github.com/web-arena-x/webarena/blob/dce04686a56253aefba7b18a4fa0937cf1dc987b/README.md)，代码快照 `dce0468` | 输入网页任务和环境，Agent 逐步操作浏览器，由任务配置与评测器检查结果 | [应用工程](../../10-Knowledge/13-application-engineering/README.md)：学习环境重置、轨迹保存和终态验证 | 固定任务配置、网页镜像、初始数据、浏览器、模型和步数预算。官方区分展示站与可复现实验环境，不能在共享展示站取得分数后当成基准结果 |
| [SWE-bench](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/README.md)，代码快照 `02e7a74` | 输入仓库与 issue，输出补丁，通过指定环境内的测试评估修复；需区分 Full、Lite、Verified 等集合 | [代码 Agent 案例](../../10-Knowledge/13-application-engineering/03-cases/coding-agents/README.md)：学习补丁、测试和环境之间的证据链 | 固定数据 revision、基础提交、任务环境、预测补丁和评测器。该快照 README 使用 v5 CLI；更换补丁应使用新 `run_id`，避免复用旧缓存。不同集合与预算的分数不可直接混比 |

## 数据许可与实验记录

| 对象 | 本轮确认范围 | 引入实验前的动作 |
| --- | --- | --- |
| HumanEval | 官方代码仓标识 MIT | 检查题目、补全与测试文件的来源；把评测代码和模型生成代码分开管理 |
| BEIR | 官方代码仓标识 Apache-2.0；README 明确说明各数据集须自行确认使用许可 | 逐个记录子数据集的原始所有者和许可；代码仓许可不覆盖所有语料 |
| WebArena | 官方 README 提供自托管环境与任务运行说明；本轮未逐项核对网站镜像许可 | 分别核对基准代码、镜像、网页素材与任务数据的许可；未核对不打包分发 |
| SWE-bench | 官方 README 标明仓库 MIT | 另外记录任务数据与被测原仓的许可；MIT 的评测器不改变原仓许可 |

每次实际实验至少保存：基准名称、数据 revision 或校验值、split、样本 ID、模型与采样设置、预算、评测器提交、逐样本输出、失败类型、汇总指标和执行日期。仅记录一个总分，无法判断变化来自模型、样本还是运行环境。

本库的小型实验若使用人工构造输入，应明确标为教学数据，不称为 HumanEval、BEIR 或 SWE-bench 的复现。学习如何构造自己的任务集，进入 [评测章节](../../10-Knowledge/10-evaluation-observability/README.md)。
