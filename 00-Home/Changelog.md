# 更新记录

## 2026-09-07：按学习路径复核

补公式与实现之间的步骤、重排实践入口、解释实验反例，修复生成结束、任务合并、记忆解析和生成证据范围问题。详细内容见[学习者走读记录](Learner-Review.md)。

## 2026-09-06

- 根据原始 138 文件盘点补齐基础 13 个教程入口和 58 篇专题，保留并加强原有 20 篇 Context/RAG/Evaluation 正文。
- 实现各领域教学代码、18 本可执行 Notebook、共享 Schema 与综合研究助手，加入成功和失败对照。
- 新增学习型写作规范、来源版本记录、模板、检查脚本与四类 CI。
- 交叉审阅修正公式链式缩放、错误码查询约束、工具输入竞态及其他可复现边界；验证细节见统一记录。
- Notebook 实际执行使用 IPython 独立进程回退后端，明确区分代码执行与标准 Jupyter 内核启动。

## 2026-09-04

- 将 `07-memory-and-state` 调整为 `07-state-and-memory`，按 State → Checkpoint → Memory → Context 注入重写学习顺序，并补充概念、模式和实验入口。
- 改为按知识领域聚合内容，形成 `00-Home / 10-Knowledge / 20-Projects / 90-Sources / 99-Inbox` 顶层结构。
- 合并重复的 Home 与 Maps 导航，新增一份全局连续学习路线，由各领域 README 承担局部导航。
- 将 Context、RAG、Evaluation 的模式、案例、Notebook、代码骨架和来源移动到对应知识领域。
- 将其余 Labs、代码骨架和案例占位归入所属领域；综合项目只保留准入说明，不制造空项目。
- 清理两份与 Git 历史完全一致的 Finder 重复副本；原内容仍可从提交 `f4cf976` 恢复。
- 将 Context Engineering 长文重构为总览、上下文模型、Builder、失败模式、优化策略和评测六个入口。
- 将 Evaluation 与 Multi-Agent 长文重构为系统模型、任务、评分器、统计、Trace、协作评测、运营和模板。
- 从运维 RAG 案例提炼端到端流程、混合检索知识和 Hybrid Retrieval 模式。
- 重写 AgentGuide 走读，删除求职细节，保留固定提交下的结构、构建证据和方法论。
- 删除重复段落、口语化表达、虚构案例、无来源成本表和未经限定的效果数字。
- 更新首页、知识地图、状态、来源索引和 Inbox，保留原专题文件名作为兼容入口。

## 2026-09-03

- 去除仓库最外层 `knowledge-tree/` 目录。
- 建立 Home、Maps、Knowledge、Patterns、Cases、Labs、Code、Sources 和 Inbox 的目标结构。
- 将已有正文迁移到对应知识、案例和来源目录。
- 增加 AI 基础模块及待补充计划。

## 2026-09-02

- 创建初始知识库与 Markdown/Jupyter/源码工程分层骨架。

## 2026-09-06：第二轮实践补齐

修复完整工具契约、JSON 引用往返、CI 触发与两处教学表述。新增学习工作台、小 Transformer、真实模型对照、Run 服务、文献/PDF/队列/科研/修复实验，并统一 Projects 导航。逐项结果见 [第二轮记录](Round2-Completion.md)。
