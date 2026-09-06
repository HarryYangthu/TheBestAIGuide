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

## 先跑一次

在仓库根目录、Python 3.11 或更高版本下运行，无需模型 API Key：

```bash
python scripts/run_python.py -m domain_research.cli --query ERR-12003 --run-id first
```

默认是本地构造语料和确定性策略，用来学习系统机制。它会输出原文引用、保存报告和状态。真实 LLM 的回答质量要另外接入、采样和评测。

Notebook 环境、完整测试和 TypeScript 命令见 [运行说明](scripts/README.md)。Notebook 保存真实执行输出，并注明执行后端；正文的 `draft` 与代码的 `verified` 分开记录，避免把实验通过等同于整篇文章经过人工审稿。

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
