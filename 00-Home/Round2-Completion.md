# 第二轮补齐与验收记录

> 日期：2026-09-06；从远端提交 `5e5a40c09e00028c7887fd3bf3bd559d96fc972f` 继续。

本轮按审核清单处理 5 项确定问题、28 项实践扩展和 5 项一致性/学习路径事项。新增学习工作台与 Tiny Transformer 两个工程；保留原有目录，通过 Projects 总表统一导航。这里的完成表示交付了表中注明范围的实现和证据，不表示每个小模型任务都成功，也不表示完成生产系统。

## 38 项对应表

| 编号 | 补齐内容 | 文件/实际证据 | 验收与范围 |
| --- | --- | --- | --- |
| A1 | 完整 ToolCall 外壳校验 | [查看](../10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/test/runtime.test.ts) | 10 项 TS 测试含异常输入；畸形调用不执行 handler |
| A2 | 引用 JSON 往返 | [查看](../10-Knowledge/15-multimodal-and-embodied/05-code/test_evidence.py) | JSON 规范化；有效往返通过，篡改拒绝 |
| A3 | Schema 变更触发 CI | [查看](../.github/workflows/python.yml) | Python/TS/Notebook 均监听共享 Schema |
| A4 | 搜索启发式违例边 | [查看](../10-Knowledge/01-ai-foundations/04-labs/search-and-rl/01-search-and-value-learning.ipynb) | 改为 S→A、B→A，并重新执行 |
| A5 | 世界模型实现表述 | [查看](../10-Knowledge/16-research-frontiers/01-concepts/03-world-models-and-neuro-symbolic.md) | 更正为资源过滤；不再声称已有状态转移代码 |
| B1 | 真实语义检索与重排 | [查看](../20-Projects/learning-workbench/artifacts/real-models/retrieval.json) | 固定 2 个模型；6 题×4 模式；另附 Notebook |
| B2 | 生成式 RAG 与审阅 | [查看](../20-Projects/learning-workbench/artifacts/real-models/generation-review.json) | 真实输出、拒答、引用身份与语义支持分开；本次小模型质量未通过 |
| B3 | 跨会话记忆闭环 | [查看](../20-Projects/learning-workbench/artifacts/offline/memory.json) | 8 个独立任务；固定概念回答的格式偏好，不是通用聊天 |
| B4 | Run API/SSE/审批与模型接口 | [查看](../20-Projects/learning-workbench/src/learning_workbench/server.py) | HTTP 与浏览器流程实测；持久状态、租户隔离、可替换 provider |
| B5 | 统一虚拟项目入口 | [查看](../20-Projects/README.md) | 12 个独立工程，加章节局部算例导航 |
| B6 | 真实 Agent 模型接口 | [查看](../20-Projects/learning-workbench/src/learning_workbench/providers.py) | 自由循环/格式示例/受限单工具流程分开；保留真实用量与失败 |
| B7 | 完整小 Transformer | [查看](../20-Projects/tiny-transformer/artifacts/report.json) | 真实 CPU 训练、生成、缓存与保存重载 |
| B8 | SFT/LoRA 更新 | [查看](../20-Projects/tiny-transformer/src/tiny_transformer/experiment.py) | 移位、mask、冻结、可训练参数与前后预测；真实更新 |
| B9 | token→ID→Embedding | [查看](../20-Projects/learning-workbench/artifacts/real-models/tokenizer.json) | 固定真实分词器；中文、代码、emoji、聊天模板 |
| B10 | 完整证据比较 Skill | [查看](../20-Projects/learning-workbench/artifacts/offline/skill-cases.json) | 主说明、脚本、模板、四类案例；宿主自动路由未冒称实测 |
| B11 | Context 故障练习 | [查看](../20-Projects/learning-workbench/fixtures/context-faults.jsonl) | 8 类索引；真实模板计数、冲突/过期/去重；位置探针单列 |
| B12 | A2A 本地交接 | [查看](../20-Projects/learning-workbench/artifacts/offline/a2a.json) | 两个 HTTP 端点，固定 0.3.0 text 子集，非完整协议认证 |
| B13 | 跨语言边界矩阵 | [查看](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/boundaries.json) | Python/Ajv 读取同一缺字段、错类型、范围、互斥样本 |
| B14 | 结构切分与 PDF | [查看](../20-Projects/learning-workbench/artifacts/offline/documents.json) | 原文偏移、完整代码/表格、父段落、原始 PDF 解析 |
| B15 | 多版本证据查询 | [查看](../20-Projects/learning-workbench/artifacts/offline/versions.json) | 逐版本查询；缺少一侧时停止比较 |
| B16 | 独立记忆评测集 | [查看](../20-Projects/learning-workbench/fixtures/memory-tasks.jsonl) | JSONL 输入/标签与执行器分离；有/无记忆对照 |
| B17 | 动态 DAG | [查看](../20-Projects/learning-workbench/artifacts/offline/planning.json) | 证据更新仅重算受影响节点；输入输出与版本可查 |
| B18 | CPU 学习与 PPO clipping | [查看](../20-Projects/tiny-transformer/artifacts/report.json) | 实际 DPO 与两动作梯度更新；正负优势算例；不是完整 PPO 训练器 |
| B19 | Judge 评分与位置交换 | [查看](../20-Projects/learning-workbench/artifacts/real-models/judge.json) | 6 个教学标签、混淆矩阵、独立 A/B 对调结果；质量不足保留 |
| B20 | Task 配对统计 | [查看](../20-Projects/learning-workbench/artifacts/offline/statistics.json) | 固定种子；Task 区间对照错误的 Trial iid 区间 |
| B21 | 真实模型注入链路 | [查看](../20-Projects/learning-workbench/artifacts/real-models/injection.json) | 外部文本→真实候选→策略→本地状态；畸形输出不算成功防御 |
| B22 | Coding 修复闭环 | [查看](../20-Projects/learning-workbench/artifacts/repair/report.json) | 临时 Git 仓库、失败基线、哈希检查、补丁与重测；固定策略 |
| B23 | 局部案例与综合任务区分 | [查看](../20-Projects/README.md) | 旧企业/运维算例标清；科研扩为完整 CPU 数据/训练/报告任务 |
| B24 | 真实队列负载 | [查看](../20-Projects/learning-workbench/artifacts/offline/queue.json) | 相同到达流，实际 worker；无限/有界队列、重试、等待与 p95 |
| B25 | 原始媒体到证据 | [查看](../20-Projects/learning-workbench/artifacts/media/report.json) | 原创 PDF、页码/文字起点；错行/单位拒答，无文字页转 OCR 待办；未实现 ASR |
| B26 | CPU 科研实验 | [查看](../20-Projects/learning-workbench/artifacts/science/report.json) | 固定训练/验证划分、基线、候选、配置、数据哈希和训练日志 |
| B27 | 多角色研究比较 | [查看](../20-Projects/learning-workbench/artifacts/real-models/research-multi.json) | 单流程/多角色同输入；真实模型读取与合并，固定拆解；未声称多角色更优 |
| B28 | 标题锚点检查 | [查看](../scripts/check_links.py) | 中文、重复标题、跨文档缺失标题测试 |
| C1 | 标准 Jupyter 证据同步 | [查看](Knowledge-Status.md) | 追加原提交标准 Jupyter CI 成功链接；保留本地输出来源 |
| C2 | 状态与 Context 分类 | [查看](Knowledge-Map.md) | 八类模式、draft 定义、旧映射同步 |
| C3 | 历史图片处置 | [查看](../assets/README.md) | 8 张来源未明 PNG 继续归档，不恢复引用、不虚构许可 |
| C4 | Lab 0 两工具与任务集 | [查看](../20-Projects/learning-workbench/fixtures/agent-tasks.jsonl) | 12 条任务；加法/搜索，规则基线与真实模型 trace 分开 |
| C5 | Lab 2 多源文献比较 | [查看](../20-Projects/learning-workbench/artifacts/research/multi.json) | 2 份固定公开论文 PDF；哈希/页码/短引文、比较与审阅，可联网下载 |

## 本地验收

Python 14 组共 83 项测试与 2 个断言算例已通过；见[机器记录](verification/round2-local.json)。TypeScript 工具 Runtime 10 项、MCP 2 项、浏览器工程 3 项通过。新增工作台的浏览器检查实际点击创建、批准、完成、取消，事件可见，390 px 下没有横向溢出。容器未配置中文字库，因此没有把本地截图当作中文字体视觉验收。

本地 Jupyter/ZeroMQ 启动因环境通信限制失败。新增 2 本和修正的搜索 Notebook 已通过明确标记的 IPython fallback 执行，保存实际输出；远端标准 Jupyter 验收在推送后记录。原 18 本对应提交 `5e5a40c` 的[标准 Jupyter CI](https://github.com/HarryYangthu/TheBestAIGuide/actions/runs/34013521515)已成功，不覆盖本轮新增代码。

## 真实模型结果不能被“代码通过”掩盖

Qwen2.5-0.5B-Instruct 固定 revision，CPU 贪心生成。初版自由循环 12/12 动作契约失败；加固定格式示例后 12/12 选到了预期工具，但都因重复调用/限步停止，没有成功回答。另行运行受限单工具→回答流程；其结果独立保存，不计为自由循环能力。

生成式 RAG 的 4 题中，3 题 JSON 无法接受，1 题引用身份有效但主张不受该引文支持，因此 4 题均未通过完整回答质量审阅。Judge 在 6 个构造样本上正确 3 个，两个 A/B 位置交换案例也未双向正确。这些报告用于学习失败诊断，不能包装成可靠系统。

真实 Embedding 与 Cross-Encoder 使用固定模型版本，在同一英文小集合完成 24 条检索实验。多源研究单流程和分工流程分别调用模型 3 次，输出与位置校验可查看；没有据此断言多角色收益。

## 保留的边界

- 远端付费 API 未调用；本机 HTTP 适配器契约与本地真实模型分别验收。模型权重下载不纳入仓库。
- 8 张历史 PNG 的作者与复用许可仍未知；完成归档处置，未恢复引用。
- PDF 解析已实现；无文字页明确需要 OCR。语音仅有人工转写的 WER 练习，没有声称实现 ASR/VLA。
- Skill 的完整包与数据案例可重放；宿主自动触发率需要在具体宿主上另测。
- A2A 是固定版本的文本子集；Run 服务、规则角色、合成队列、CPU 小语料均有明确教学边界。

相关入口：[所有项目](../20-Projects/README.md)、[学习工作台](../20-Projects/learning-workbench/README.md)、[Transformer 教程](../20-Projects/tiny-transformer/README.md)。

## 同一任务集的最终对照

| 流程 | 任务数 | 完成 | 选到预期工具 | 完成且答案匹配 |
| --- | --- | --- | --- | --- |
| deterministic | 12 | 12 | 12 | 12 |
| free_initial | 12 | 0 | 0 | 0 |
| free_format_examples | 12 | 0 | 12 | 0 |
| bounded_one_tool | 12 | 11 | 12 | 10 |

受限流程仍有失败，全部保留在 [Agent 对照](../20-Projects/learning-workbench/artifacts/real-models/agent-comparison.json)。两个文献流程均未通过完整模型输出质量检查，见[研究对照](../20-Projects/learning-workbench/artifacts/real-models/research-comparison.json)。

## 发布前脱敏

自动发布审查发现一份模型输出含疑似凭据字段，因此第一次树对象上传被拒绝，分支未更新。已对受影响的模型原文和 trace 做脱敏，保留错误状态与评分；没有判定该值是否为真实凭据。位置见[脱敏登记](../20-Projects/learning-workbench/artifacts/redactions.json)。CLI 在评分后清理公开产物中的类似字段；此规则不是通用敏感信息检测系统。
