# 图片与图表登记

本目录保存文章引用的图片、SVG 和图表。图片应补充正文难以表达的结构或关系；公式推导和关键实现仍放在可检索的 Markdown 与源码中，不能只给截图。

## 既有素材状态

登记基于仓库原始盘点；本轮未下载或逐图核验下面 8 张历史 PNG，不删除它们，也不把“文件存在”写成来源或内容已通过审查。

| 文件 | 用途与当前状态 | 来源／验证边界 |
| --- | --- | --- |
| `context-engineering-core.svg` | 上下文工程正文引用的可编辑示意图 | 已确认源码有 `title`、`desc`；该确认不等于完成字体、裁切和可读性视觉验收 |
| `context-engineering-core.png` | 同主题历史位图，当前未引用 | 原始来源、作者及复用条件待核验 |
| `context-clash-sharded-instruction.png` | 历史素材，当前未引用 | 原始来源、作者及复用条件待核验 |
| `tool-calling-irrelevance-score-gemma.png` | 历史素材，当前未引用 | 原始来源、作者及复用条件待核验 |
| `evaluation-code-based-graders.png` | 旧 Evaluation 素材，当前未引用 | 原始来源、作者及复用条件待核验 |
| `evaluation-components-for-agents.png` | 旧 Evaluation 素材，当前未引用 | 原始来源、作者及复用条件待核验 |
| `evaluation-human-graders.png` | 旧 Evaluation 素材，当前未引用 | 原始来源、作者及复用条件待核验 |
| `evaluation-model-based-graders.png` | 旧 Evaluation 素材，当前未引用 | 原始来源、作者及复用条件待核验 |
| `evaluation-single-turn-vs-agent.png` | 旧 Evaluation 素材，当前未引用 | 原始来源、作者及复用条件待核验 |

## 新增与恢复引用

文件名描述内容，例如 `attention-mask-example.svg`。正文引用给出有效替代文本，图中符号与文章一致。自制图保留可编辑源文件；由数据生成的图保留数据、脚本、坐标单位与实验条件，教学数据明确标注。

外部素材在此登记文件名、作者、原始 URL、原文图号、版本／日期、许可和修改内容。来源不明的历史图继续保留登记，确认出处和复用条件后才恢复正文引用；需要重画时重新制作并注明依据，不把改色或裁切当原创。

发布前在实际渲染结果中检查中文字体、文字重叠、裁切、对比度与移动端可读性。SVG 含有 `title`、`desc` 是无障碍信息的一部分，仍需核对其文字是否准确描述图中关系。视觉验收和来源核验分别记录，不能相互替代。

## 2026-09-06 本轮处置

上述 8 张来源未明的历史 PNG 继续归档，不恢复正文引用；当前学习补齐无需依赖它们。未获得作者/许可证据，因此没有将其标成已授权。新媒体实验使用代码生成的原创教学 PDF，源代码、页码和哈希保存在 learning-workbench。此项完成的是归档处置，不是补造历史来源。

`context-engineering-core.svg` 是机制简图；其中列举的失败模式只表示常见子集。完整八类定义以 Context Engineering 的失败模式文章为准。
