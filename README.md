# TheBestAIGuide

面向学习和工程实践的 AI 知识库。每个主题先解释机制，再给公式、算例和实现，最后用实验观察它何时有效、何时失败。

## 从这里开始

| 你的目标 | 阅读入口 | 动手做什么 |
| --- | --- | --- |
| 补齐数学与机器学习 | [AI 基础](10-Knowledge/01-ai-foundations/README.md) | 算梯度、观察过拟合、更新价值函数 |
| 搞懂模型内部 | [基础模型](10-Knowledge/02-foundation-models/README.md) | 手算并运行 Attention，比较缩放、Mask 和 KV Cache |
| 做出最小 Agent | [Agent Core](10-Knowledge/03-agent-core/README.md) | 观察工具调用、失败与停止原因 |
| 设计信息链路 | [Context](10-Knowledge/04-context-engineering/README.md)、[RAG](10-Knowledge/06-rag-and-knowledge-systems/README.md)、[Memory](10-Knowledge/07-state-and-memory/README.md) | 改预算、查询、权限和过期时间，比较输出 |
| 理解可靠执行 | [Tools](10-Knowledge/05-tools-skills-protocols/README.md)、[Workflow](10-Knowledge/08-planning-workflow-multi-agent/README.md)、[Runtime](10-Knowledge/09-runtime-harness-environment/README.md) | 故意制造超时、冲突和中断，再恢复 |
| 判断系统是否改善 | [Evaluation](10-Knowledge/10-evaluation-observability/README.md) | 隔离任务、检查状态、跑回归门禁 |
| 看各组件如何协作 | [领域资料研究助手](20-Projects/domain-research-agent/README.md) | 运行引用、拒答、权限和故障恢复案例 |

完整顺序见 [连续学习路线](00-Home/Learning-Paths.md)，按主题查找见 [知识领域](10-Knowledge/README.md)，理论覆盖范围见 [知识地图](00-Home/Knowledge-Map.md)。

## 先完成一次有证据的回答，再看一次拒答

从仓库根目录运行，Python 3.11 或更高即可，无需安装依赖或配置模型：

```bash
python scripts/run_python.py -m domain_research.cli --query ERR-12003 --run-id found --output .runs/first-lesson
python scripts/run_python.py -m domain_research.cli --query UNKNOWN-999 --run-id missing --output .runs/first-lesson
```

第一条查询命中仓库里的教学资料，第二条没有匹配证据。对照终端中的 JSON：

| 观察什么 | 第一条 | 第二条 | 由此理解什么 |
| --- | --- | --- | --- |
| `abstained` | `false` | `true` | 系统需要有“证据不足就停止回答”的分支 |
| `citations` | 包含 `doc_id`、`version`、`quote` | 空数组 | 回答必须能回到特定版本的原文；有引用还需检查它是否支持结论 |
| `text` | 引用 ERR-12003 对应段落 | 提示授权范围内未找到证据 | 本例复制检索到的原文，错误码也是教学构造 |
| `decision_policy` / `answer_mode` | `deterministic-v1` / `extractive-v1` | 相同 | 这里的选择由固定代码完成，尚未调用语言模型 |

报告与可恢复状态保存在 `.runs/first-lesson/`。同一个 `run-id` 表示同一次任务；要修改问题或比较新方案，请使用新的 `run-id` 或输出目录。源码怎样组合检索、状态和恢复，继续读[领域资料研究助手](20-Projects/domain-research-agent/README.md)；想让真实模型选工具，再进入[学习工作台](20-Projects/learning-workbench/README.md)。

试着解释：如果回答里出现一个真实存在的引用，为什么仍可能答错？检查引用对应的版本、对象，以及原文是否真的支持这句话。随后去 [RAG 引用章节](10-Knowledge/06-rag-and-knowledge-systems/01-concepts/07-citations-and-grounding.md)读具体例子。

Notebook 环境、完整测试和 TypeScript 命令见[运行说明](scripts/README.md)。正文的 `draft` 表示尚未完成人工审稿；实验的 `verified` 只表示注明条件下已经执行，两者不是同一条完成度刻度。

## 仓库怎么组织

| 目录 | 内容 |
| --- | --- |
| [00-Home](00-Home/README.md) | 学习路线、写作规范、建设状态和维护记录 |
| [10-Knowledge](10-Knowledge/README.md) | 16 个领域的知识、模式、案例、Notebook 与源码 |
| [20-Projects](20-Projects/README.md) | 复用多个领域组件的综合项目 |
| [90-Sources](90-Sources/README.md) | 论文、教材、官方文档、协议和数据来源 |
| [99-Inbox](99-Inbox/README.md) | 待消化材料 |
| [assets](assets/README.md) | 图像来源与使用记录 |
| [scripts](scripts/README.md) | 链接、元数据、Notebook 和测试工具 |

先读 Markdown 中的关键代码，再进入链接指向的完整源码；Notebook 用来改参数、看中间量并回答练习题。写作要求见 [学习型写作规范](00-Home/Learning-Writing-Guide.md)，交付与验证范围见 [建设状态](00-Home/Knowledge-Status.md)。
