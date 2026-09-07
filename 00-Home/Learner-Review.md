# 从学习者角度走读后的修订

> 日期：2026-09-07。基线提交：`3d917476d0013577e215974facc94a3da8e63037`。本文记录一次阅读、代码对照与运行验收，不把自动审阅称为真实读者的学习效果测试。

原有知识主线可以用于学习，但“文件已有内容”仍不等于“读者能顺着学会”。这次最常见的问题是：后加的项目没有接回旧文章；公式与实现之间漏了一步；实验输出太多却缺少解释；部分示例边界会产生错误结果。

## 具体改了什么

| 学习时遇到的断点 | 本次改动 | 可直接查看的例子 |
| --- | --- | --- |
| 不知道先装什么、运行后看什么 | 首页先跑有证据回答与拒答；环境按入门、Notebook、完整验证、可选模型拆开；学习路线增加检查问题与答案要点 | [首页](../README.md)、[运行说明](../scripts/README.md)、[连续路线](Learning-Paths.md) |
| 能背公式，却对不上代码的位置 | 增加 SFT 的输入/目标/忽略标签逐格表、DPO 对数概率差、PPO 正负优势算例、LoRA 系数约定；Notebook 拆开 Attention 中间张量 | [训练篇](../10-Knowledge/02-foundation-models/01-concepts/training/README.md)、[Tiny 实验](../20-Projects/tiny-transformer/01-train-and-inspect.ipynb) |
| 以为加了复杂组件就一定更好 | 用同一道实际检索题展示融合如何把正确证据排低，再解释重排为何改善；补回完整公式与符号 | [混合检索与重排](../10-Knowledge/06-rag-and-knowledge-systems/01-concepts/02-hybrid-retrieval-and-reranking.md) |
| 记不清相邻概念的边界 | 区分存储与本轮 Context、版本冲突与事实真假、恢复与取消、模型离题与执行层拒绝、说话人归属与声源分离 | [Context](../10-Knowledge/04-context-engineering/README.md)、[Memory](../10-Knowledge/07-state-and-memory/README.md)、[Runtime](../10-Knowledge/09-runtime-harness-environment/README.md) |
| 看到一个高分，无法判断是否真变好 | 补微/宏平均、任务配对重采样、超时与费用分母、Judge 混淆矩阵；讲清格式失败不是正确判断 | [统计与可靠性](../10-Knowledge/10-evaluation-observability/01-concepts/04-statistics-and-reliability.md) |
| 旧文说没有实现，新项目却已经有 | 逐域修正训练、真实模型、PDF、DAG、SSE 等过时描述；将笼统工作台链接改为具体实验/源码/报告 | [项目总表](../20-Projects/README.md)、[工作台](../20-Projects/learning-workbench/README.md) |
| Notebook 从不同目录启动失败，或只有大段 JSON | 修正仓库定位；工作台 Notebook 改为逐题对比、数值重算、错误引用分析、实际重开记忆库与自检 | [工作台 Notebook](../20-Projects/learning-workbench/01-evidence-and-model-results.ipynb) |
| 公式在 GitHub 阅读入口不够稳妥 | 按官方支持的 `$` / `$$` 统一正文数学分隔符，保持代码块；核对表格列数 | [写作规范](Learning-Writing-Guide.md) |

## 一起修复的代码问题

| 问题 | 修复与验证 |
| --- | --- |
| 批量生成中已出现 EOS 的序列继续输出；已满窗口还多生成一个 token | 按序列保存结束状态，结束行补 PAD，按剩余窗口限制步数；真实 Decoder 权重构造测试覆盖不同结束时刻 |
| 丢失一个子任务结果，合并器仍可声称完成 | 合并时传入预期任务 ID，检查缺失、重复和未知结果；空列表不能表示完成 |
| 把否定、转述或歧义格式要求当作正向记忆 | 写入和当前格式请求使用明确支持的语法；不支持的含格式词请求明确拒绝，避免静默套用旧偏好 |
| 原文答案与生成答案的版本范围可能不同 | 生成阶段复用服务的 tenant、product、version，并检验实际传入模型的证据范围 |
| 统计/奖励/金额算例接受非有限数值或不合法计数 | 拒绝 NaN/Inf、非整数计数等输入，对应反例加入回归 |
| 中文 fixture 的读取依赖操作系统默认编码 | 项目文本读写显式采用 UTF-8；在关闭 Python UTF-8 模式的 ASCII locale 下运行 CLI 检查 |

## 验证怎样读

具体记录见 [learner-review.json](verification/learner-review.json)。本地先执行完整 Python 回归，再对后续收口改动执行对应回归；修改过的 Notebook 重新执行并保存输出。TypeScript Runtime 与 MCP 实际测试通过。

本地标准 Jupyter 内核因环境网络接口权限限制无法启动，因此明确使用仓库已有的 `ipython-fallback`；每本 Notebook 仍在新进程中按序执行，输出元数据保留后端。标准 Jupyter 和浏览器的最终检查以本分支对应提交的 GitHub Actions 为准，不能拿之前提交的成功状态替代。

本轮未重新下载/评估全部预训练模型，文中引用的真实模型报告仍注明原实验条件。保留模型失败与教学实现边界，没有把固定规则演示改称自主 Agent，也没有把小数据训练损失下降改称泛化能力提高。

后续人工阅读时，优先记录“哪句话不懂、预期哪个输出、实际看到什么”，而不是只给整篇文章一个好坏评价。正文继续保留 `draft`；这次自动走读不能代替真实学习者反馈或逐篇人工审稿。
