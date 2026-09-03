# Context Engineering 资源索引

> 用途：集中保存 Context Engineering 的学习资料、论文、工程实践、开源仓库和学习路径。正文知识沉淀放在 [Context-Engineering.md](../../20-Knowledge/04-context-engineering/Context-Engineering.md)，这里作为资源导航。

## 一、核心概念入门

### 1. The New Skill in AI is Not Prompting, It's Context Engineering

- 作者：Philipp Schmid
- 链接：https://www.philschmid.de/context-engineering
- 核心价值：入门必读，适合快速建立术语体系和框架认知。
- 内容要点：
  - 上下文工程不是提示工程，而是动态系统。
  - 六层上下文模型：指令/提示、短期记忆、长期记忆、RAG 检索、工具定义、结构化输出。
  - 核心公式：正确信息 + 正确工具 + 正确时机 + 正确格式 = 有效 Agent。

### 2. 上下文工程技术总结（中文叙事版）

- 论文：https://arxiv.org/pdf/2510.26493
- 仓库：https://github.com/GAIR-NLP/Context-Engineering-2.0
- 微信文章：https://mp.weixin.qq.com/s/KbviOJ6q-K4ik_wzsUs2dw
- 核心价值：适合补充理论深度和演进脉络。
- 内容要点：
  - 上下文工程可以从熵减理论理解。
  - RAG、CoT、多模态都可以看作把高熵信息转成更低熵、更可用表示的过程。
  - 2.0 策略包括文本处理和选择策略：时间戳、标签、QA 压缩、层级笔记、语义相关性、逻辑依赖、时效性、去重、用户偏好。

## 二、实战方法论

### 3. Context Engineering for Agents

- 作者：Harrison Chase
- 链接：https://blog.langchain.com/context-engineering-for-agents/
- 配套仓库：https://github.com/langchain-ai/how_to_fix_your_context
- 核心价值：实践框架清晰，有完整代码示例。
- 四大策略：
  - Write Context：Scratchpads、短期/长期记忆、LangMem。
  - Select Context：动态检索、工具筛选、RAG 优化。
  - Compress Context：总结、递归压缩、层级压缩、剪枝。
  - Isolate Context：多 Agent、沙盒环境、状态对象。

### 4. 12-Factor Agents

- 作者：Dex Horthy
- 链接：https://github.com/humanlayer/12-factor-agents
- 核心价值：生产级 Agent 方法论。
- 关键观点：
  - Factor 3：拥有你的上下文窗口。
  - Agent 应该是 80% 确定性代码 + 20% LLM 调用。
  - 不要盲目信任框架，要拥有核心组件。
  - 成本呈二次增长，必须优化。

### 5. phodal/build-agent-context-engineering

- 作者：phodal
- 链接：https://github.com/phodal/build-agent-context-engineering
- 核心价值：中文开发者友好的系统实战资料。
- 四大学习路径：
  - 结构化提示词工程。
  - 上下文工程与 RAG。
  - 工具系统设计。
  - Agent 规划与多 Agent。
- 相关案例：GitHub Copilot 上下文优先级排序、Cursor Rule 设计。

## 三、问题诊断与修复

### 6. How Contexts Fail—and How to Fix Them

- 作者：Drew Breunig
- 链接：https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html
- 核心价值：反面案例和修复策略。
- 四种失败模式：
  - Context Poisoning：幻觉错误被反复引用。
  - Context Distraction：长上下文导致重复历史动作。
  - Context Confusion：无关工具或信息干扰响应。
  - Context Clash：多轮对话中信息矛盾。

### 7. Practical Tips on Building LLM Agents

- 作者：Paras Chopra
- 链接：https://letters.lossfunk.com/p/practical-tips-on-building-llm-agents
- 核心价值：一线工程经验和成本考量。
- 关键洞察：
  - 任务切分到 10-15 分钟粒度。
  - 每步明确成功/失败标准，防止错误累积。
  - 定期重复待办列表，对抗长任务健忘。
  - 让 LLM 通过工具读写自主构建上下文。
  - 通过 KV 缓存降低多轮 Agent 成本。

## 四、企业实战案例

### 8. Context Engineering for AI Agents: Lessons from Building Manus

- 作者：季逸超
- 链接：https://manus.im/zh-cn/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
- 核心价值：长任务 Agent 的企业级优化经验。
- 核心经验：
  - KV 缓存优化：只追加不修改，提升缓存命中。
  - 工具遮蔽：动态显示或隐藏工具，避免上下文混淆。
  - 文件系统作为上下文：让 Agent 读写 Memory 文件。
  - 复述操控注意力：把关键信息重复到上下文末尾。
  - 保留错误信息：让 LLM 利用失败上下文自我纠正。
  - 避免少样本陷阱：Few-Shot 过多可能偏离当前任务。

### 9. Effective Context Engineering for AI Agents

- 来源：Anthropic 官方
- 链接：https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- 核心价值：Claude 团队实践经验。
- 三大维度：
  - 有效上下文：提示词、工具定义、Few-Shot 示例。
  - 即时检索：动态工具调用、RAG 增强。
  - 长任务管理：上下文压缩、笔记系统、子 Agent 隔离。

### 10. Brainwash Your Agent: How We Keep the Memory Clean

- 作者：CAMEL-AI 团队
- 链接：https://www.camel-ai.org/blogs/brainwash-your-agent-how-we-keep-the-memory-clean
- 核心价值：记忆清理和长工作流管理。
- 三大技术：
  - 上下文总结。
  - 工作流内存。
  - 工具输出缓存。
- 适用场景：长工作流 Agent、开源贡献者、需要减少侧任务干扰的系统。

## 五、学术综述与前沿研究

### 11. A Survey of Context Engineering for Large Language Models

- 论文：https://arxiv.org/pdf/2507.13334
- 仓库：https://github.com/Meirtz/Awesome-Context-Engineering
- 核心价值：全景综述，适合研究者和架构师。
- 内容框架：
  - 检索增强。
  - 上下文处理。
  - 记忆管理。
  - RAG、长上下文、结构化数据、自生成上下文、Agent 通信、评估。

### 12. Context Engineering 2.0: The Context of Context Engineering

- 论文：https://arxiv.org/pdf/2510.26493
- 仓库：https://github.com/GAIR-NLP/Context-Engineering-2.0
- 核心价值：上下文工程 2.0 与熵减理论框架。
- 核心贡献：
  - Agent 中心智能。
  - 将上下文工程定位为熵减过程。
  - 策略分类：文本处理 + 选择策略。

## 六、开源工具与代码仓库

### 13. davidkimai/Context-Engineering

- 链接：https://github.com/davidkimai/Context-Engineering
- 核心价值：完整学习路径和上下文协议参考。
- 内容模块：
  - 基础学习路径。
  - RAG 架构。
  - 记忆设计。
  - 工具集成。
  - 上下文修剪。
  - Agent 系统。

### 14. WakeUp-Jin/Practical-Guide-to-Context-Engineering

- 链接：https://github.com/WakeUp-Jin/Practical-Guide-to-Context-Engineering
- 核心价值：实践指南和结构化导航。
- 七类上下文分解：
  - 系统提示。
  - 用户输入。
  - 短期记忆。
  - 长期记忆。
  - RAG。
  - 工具输出。
  - 结构化输出。

### 15. ginobefun/agentic-design-patterns-cn

- 链接：https://github.com/ginobefun/agentic-design-patterns-cn/tree/main
- 核心价值：Agentic Design Patterns 中英对照译本。
- 模式库：
  - 提示链。
  - 反思。
  - 工具使用。
  - 多 Agent。
  - 记忆管理。
  - 协议设计。
  - 异常处理。
  - RAG 集成。
  - 生产模式。

## 七、视频与多媒体资源

### 16. Context Engineering: The Outer Loop

- 作者：Hammad Bashir
- 平台：YouTube
- 时长：30 分钟
- 核心价值：用向量数据库构建外循环动态上下文的可视化演示。
- 技术栈：Chroma + 向量检索 + 动态上下文构建。

### 17. AI Engineer World's Fair Talk: 12-Factor Agents

- 演讲者：Dex Horthy
- 链接：https://www.youtube.com/watch?v=8kMaTybvDUw
- 核心价值：12-Factor Agents 方法论现场讲解。

## 八、电子书与完整指南

### 18. The Context Engineering Guide

- 出版方：Weaviate
- 链接：https://weaviate.io/ebooks/the-context-engineering-guide
- 核心价值：完整 eBook，适合系统学习。
- 章节覆盖：
  - Agent 架构设计。
  - 查询增强技术。
  - 检索策略优化。
  - 内存系统构建。
  - 工具集成方案。
  - 生产级模式。

## 学习路径推荐

### 入门路径（1-2 周）

1. 阅读 Philipp Schmid 的概念文章，建立框架。
2. 学习 Drew Breunig 的失败模式，先知道坑在哪里。
3. 浏览 LangChain 的四大策略，建立方法论。

### 进阶路径（2-4 周）

1. 深入 phodal 的中文实战仓库。
2. 研读 12-Factor Agents。
3. 学习 Manus / Anthropic 的企业案例。

### 专家路径（1-3 个月）

1. 研读 1400+ 论文综述，建立全景视野。
2. 实践 davidkimai 的完整学习路径。
3. 参与或贡献开源项目。

## 核心技术要点速查

### 上下文工程三大支柱

- 信息检索：RAG、混合检索、Agentic 检索。
- 记忆管理：短期 / 长期记忆、反思机制。
- 工具编排：MCP 协议、工具路由、并行调用。

### 生产环境最佳实践

- 任务原子化：10-15 分钟粒度。
- 使用 KV 缓存：只追加不修改。
- 建立验证系统：每步明确成功 / 失败。
- 工具单一职责：原子性 + 语义清晰。
- 上下文压缩与隔离：总结 + 剪枝 + 沙盒。
- 避免上下文中毒和冲突。
- 防止过度依赖长上下文。

### 成本优化关键指标

- 多轮 Agent 成本可能呈二次增长。
- KV 缓存命中可降低大量成本。
- 上下文总结可减少 60-80% 令牌。

## 资源价值矩阵

| 资源 | 理论深度 | 实践性 | 代码质量 | 适合人群 |
| --- | --- | --- | --- | --- |
| Philipp Schmid 文章 | 中 | 高 | - | 所有人 |
| LangChain 博客 | 中 | 高 | 高 | 开发者 |
| 12-Factor Agents | 高 | 高 | 高 | 工程师 |
| phodal 仓库 | 高 | 高 | 高 | 中文开发者 |
| Drew Breunig 文章 | 高 | 高 | - | 调试者 |
| 1400+ 论文综述 | 很高 | 中 | - | 研究者 |
| davidkimai 仓库 | 高 | 高 | 高 | 深度学习者 |
| Manus 案例 | 中 | 高 | 中 | 企业团队 |
