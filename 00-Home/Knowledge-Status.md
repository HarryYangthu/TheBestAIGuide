# 知识库建设状态

> 更新日期：2026-09-06；原始基线：`f9729ba319a5cf0911b009c863a4796a888d8306`。

本轮将脚手架补成可以沿“机制 → 公式/算例 → 源码 → 实验”学习的第一版。原有 Context、RAG、Evaluation 的 20 篇正文保留并补充解释和实现链接；基础两域的 13 个概念入口改成教程，其余领域按盘点计划新增 58 篇专题与案例。

新正文保留 `draft`，表示已有实质内容、完成一手来源核对与自动交叉审阅，但没有冒称人工审稿。实验与代码的 `verified` 只覆盖各运行报告注明的条件。

## 按领域进入

下表“正文文件”包括有实质正文的概念、模式及案例 README；长度只用于排除短导航页，不能作为文章质量评分。Notebook 单独计数。

| 领域 | 正文文件 | Notebook | 证据入口 |
| --- | --- | --- | --- |
| [AI 基础](../10-Knowledge/01-ai-foundations/README.md) | 7 | 4 | [来源](../10-Knowledge/01-ai-foundations/references.md) |
| [基础模型](../10-Knowledge/02-foundation-models/README.md) | 6 | 2 | [来源](../10-Knowledge/02-foundation-models/references.md) |
| [Agent Core](../10-Knowledge/03-agent-core/README.md) | 5 | 1 | [来源](../10-Knowledge/03-agent-core/references.md) |
| [Context Engineering](../10-Knowledge/04-context-engineering/README.md) | 6 | 2 | [来源](../10-Knowledge/04-context-engineering/references.md) |
| [Tools / Skills / MCP](../10-Knowledge/05-tools-skills-protocols/README.md) | 6 | 1 | [来源](../10-Knowledge/05-tools-skills-protocols/references.md) |
| [RAG](../10-Knowledge/06-rag-and-knowledge-systems/README.md) | 10 | 1 | [来源](../10-Knowledge/06-rag-and-knowledge-systems/references.md) |
| [State / Memory](../10-Knowledge/07-state-and-memory/README.md) | 5 | 1 | [来源](../10-Knowledge/07-state-and-memory/references.md) |
| [Planning / Workflow / Multi-Agent](../10-Knowledge/08-planning-workflow-multi-agent/README.md) | 6 | 1 | [来源](../10-Knowledge/08-planning-workflow-multi-agent/references.md) |
| [Runtime / Harness](../10-Knowledge/09-runtime-harness-environment/README.md) | 5 | 1 | [来源](../10-Knowledge/09-runtime-harness-environment/references.md) |
| [Evaluation / Observability](../10-Knowledge/10-evaluation-observability/README.md) | 10 | 1 | [来源](../10-Knowledge/10-evaluation-observability/references.md) |
| [Safety / Security / Governance](../10-Knowledge/11-safety-security-governance/README.md) | 4 | 1 | [来源](../10-Knowledge/11-safety-security-governance/references.md) |
| [Agent Learning](../10-Knowledge/12-agent-learning/README.md) | 5 | 1 | [来源](../10-Knowledge/12-agent-learning/references.md) |
| [应用工程](../10-Knowledge/13-application-engineering/README.md) | 9 | 0 | [来源](../10-Knowledge/13-application-engineering/references.md) |
| [生产工程](../10-Knowledge/14-production-engineering/README.md) | 5 | 0 | [来源](../10-Knowledge/14-production-engineering/references.md) |
| [多模态与具身](../10-Knowledge/15-multimodal-and-embodied/README.md) | 4 | 1 | [来源](../10-Knowledge/15-multimodal-and-embodied/references.md) |
| [研究前沿](../10-Knowledge/16-research-frontiers/README.md) | 5 | 0 | [来源](../10-Knowledge/16-research-frontiers/references.md) |

## 本轮执行范围

- 18 本 Notebook 的 86 个代码单元已实际执行并保存输出。原保存输出通过独立 Python 进程中的 IPython 顺序执行；随后提交 `5e5a40c` 的标准 Jupyter CI 已成功，详见下方记录。
- Python 工程覆盖 Agent Loop、RAG、Memory、多任务调度、恢复运行时、Eval、权限、训练数据、文档引用与综合项目。测试总数及最终结果见[统一验证记录](Verification-Report.md)。
- 三个 TypeScript 工程包含工具执行器、固定 SDK 的 MCP stdio 客户端/服务端，以及真实 Chromium 上的本地页面动作与恢复测试。
- [综合项目](../20-Projects/domain-research-agent/README.md)复用五个领域组件：引用、权限、拒答与故障恢复四类任务，各运行两次；均通过预设的状态与输出断言。
- [维护脚本](../scripts/README.md)检查相对文件/目录链接、状态元数据与 Notebook；四个 GitHub Actions 工作流已配置，远端结果以实际提交的 Actions 为准。

逐文件交付见[完成台账](Completion-Report.md)，机器可读执行证据见[verification](verification/)。

## 学习时应知道的限制

离线策略、构造语料和数值小实验用于解释机制，并不证明真实 LLM 的能力、生产吞吐、开放网页稳定性或 GPU 训练效果。RAG 的默认实现是 BM25/完整编号与 RRF，真实 embedding 和 reranker 已在学习工作台中接入并执行，固定模型、小型英文构造集的结果单列。

历史 AgentGuide 走读继续保留原固定快照。八张历史 PNG 的来源尚不能确认，已在[素材登记](../assets/README.md)逐项标注并保留，不用于支持新结论。外部链接已建立月度检查任务；一次来源核对不保证远端永远有效。

## 标准内核验证更新（2026-09-06）

提交 `5e5a40c09e00028c7887fd3bf3bd559d96fc972f` 的 [GitHub Actions 标准 Jupyter 执行](https://github.com/HarryYangthu/TheBestAIGuide/actions/runs/34013521515)已成功。原 Notebook 保存输出的本地 IPython 来源保留；这条更新补充标准内核证据，不代表交互控件或所有前端已验收。本轮新项目与后续结果见仓库 `00-Home/Round2-Completion.md`。

## 第二轮实践扩展

新增学习工作台与 Tiny Transformer，Notebook 总数增至 20。本页上方领域表保留第一轮领域内文件统计；新增项目的 2 本在 Projects 下。38 项对应实现与本轮真实结果见 [Round2-Completion](Round2-Completion.md)，不沿用第一轮的测试数作为当前总数。
