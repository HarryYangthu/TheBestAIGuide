# 逐文件完成台账

> 盘点基线：`f9729ba319a5cf0911b009c863a4796a888d8306`；本轮日期：2026-09-06。

原始 138 个文件全部登记；本轮更新 113 个、保留 21 个、以真实源码替代 4 个空目录标记；新增 275 个文件（含代码、依赖、实验输出和本台账）。

完成范围：13 个原基础入口改为教程；58 篇计划新增专题/案例全部存在；原有 20 篇 Context/RAG/Evaluation 正文保留并加强；16 个领域均有来源索引；18 本 Notebook 已实跑。目录数量和文件存在只证明交付结构，质量与实际运行证据另见[统一验证记录](Verification-Report.md)。

保留项包括已有规范、历史来源走读和 8 张尚未核验来源的图片；这不表示这些图片获得了新增事实或授权背书。新正文保持 draft，实际运行的教学实现另记限定范围 verified。

## 原始文件的处理

| 文件 | 原盘点状态 | 本轮处理 |
| --- | --- | --- |
| [.editorconfig](../.editorconfig) | 基础配置可用 | 保留现有内容；不制造无必要修改 |
| [.github/workflows/README.md](../.github/workflows/README.md) | CI 占位 | 补全或更新；导航、规范或记录 |
| [.gitignore](../.gitignore) | 基础配置可用 | 补全或更新；维护配置 |
| [00-Home/Changelog.md](../00-Home/Changelog.md) | 维护记录可用 | 补全或更新；导航、规范或记录 |
| [00-Home/Conventions.md](../00-Home/Conventions.md) | 规范可用·需对齐 | 补全或更新；导航、规范或记录 |
| [00-Home/Glossary.md](../00-Home/Glossary.md) | 已有正文·待核验 | 保留现有内容；不制造无必要修改 |
| [00-Home/Knowledge-Map.md](../00-Home/Knowledge-Map.md) | 总纲可用·待落地 | 补全或更新；导航、规范或记录 |
| [00-Home/Knowledge-Status.md](../00-Home/Knowledge-Status.md) | 状态表可用·需更新 | 补全或更新；导航、规范或记录 |
| [00-Home/Learning-Paths.md](../00-Home/Learning-Paths.md) | 学习路线可用·待同步 | 补全或更新；draft |
| [00-Home/README.md](../00-Home/README.md) | 导航可用·待同步 | 补全或更新；导航、规范或记录 |
| [00-Home/Repository-Structure.md](../00-Home/Repository-Structure.md) | 规范可用 | 保留现有内容；不制造无必要修改 |
| [00-Home/Roadmap.md](../00-Home/Roadmap.md) | 高层计划可用·待细化 | 补全或更新；导航、规范或记录 |
| [00-Home/Scope.md](../00-Home/Scope.md) | 规范可用 | 保留现有内容；不制造无必要修改 |
| [00-Home/reference-cases/AgentGuide/README.md](../00-Home/reference-cases/AgentGuide/README.md) | 导航可用 | 保留现有内容；不制造无必要修改 |
| [00-Home/reference-cases/AgentGuide/repository-walkthrough.md](../00-Home/reference-cases/AgentGuide/repository-walkthrough.md) | 历史成稿·保留证据边界 | 保留现有内容；不制造无必要修改 |
| [00-Home/templates/README.md](../00-Home/templates/README.md) | 模板说明可用·待增强 | 补全或更新；导航、规范或记录 |
| [00-Home/待补充计划.md](../00-Home/待补充计划.md) | 任务清单可用·待细化 | 补全或更新；导航、规范或记录 |
| [10-Knowledge/01-ai-foundations/01-concepts/classical-ai/README.md](../10-Knowledge/01-ai-foundations/01-concepts/classical-ai/README.md) | 概念主题占位 | 补全或更新；draft |
| [10-Knowledge/01-ai-foundations/01-concepts/compute-foundations/README.md](../10-Knowledge/01-ai-foundations/01-concepts/compute-foundations/README.md) | 概念主题占位 | 补全或更新；draft |
| [10-Knowledge/01-ai-foundations/01-concepts/deep-learning/README.md](../10-Knowledge/01-ai-foundations/01-concepts/deep-learning/README.md) | 概念主题占位 | 补全或更新；draft |
| [10-Knowledge/01-ai-foundations/01-concepts/machine-learning/README.md](../10-Knowledge/01-ai-foundations/01-concepts/machine-learning/README.md) | 概念主题占位 | 补全或更新；draft |
| [10-Knowledge/01-ai-foundations/01-concepts/math-and-statistics/README.md](../10-Knowledge/01-ai-foundations/01-concepts/math-and-statistics/README.md) | 概念主题占位 | 补全或更新；draft |
| [10-Knowledge/01-ai-foundations/01-concepts/reinforcement-learning/README.md](../10-Knowledge/01-ai-foundations/01-concepts/reinforcement-learning/README.md) | 概念主题占位 | 补全或更新；draft |
| [10-Knowledge/01-ai-foundations/01-concepts/trustworthy-ai/README.md](../10-Knowledge/01-ai-foundations/01-concepts/trustworthy-ai/README.md) | 概念主题占位 | 补全或更新；draft |
| [10-Knowledge/01-ai-foundations/04-labs/README.md](../10-Knowledge/01-ai-foundations/04-labs/README.md) | 实验入口占位 | 补全或更新；verified |
| [10-Knowledge/01-ai-foundations/04-labs/deep-learning/README.md](../10-Knowledge/01-ai-foundations/04-labs/deep-learning/README.md) | 实验入口占位 | 补全或更新；verified |
| [10-Knowledge/01-ai-foundations/04-labs/search-and-rl/README.md](../10-Knowledge/01-ai-foundations/04-labs/search-and-rl/README.md) | 实验入口占位 | 补全或更新；verified |
| [10-Knowledge/01-ai-foundations/README.md](../10-Knowledge/01-ai-foundations/README.md) | 领域提纲·待补全 | 补全或更新；draft |
| [10-Knowledge/02-foundation-models/01-concepts/inference/README.md](../10-Knowledge/02-foundation-models/01-concepts/inference/README.md) | 概念主题占位 | 补全或更新；draft |
| [10-Knowledge/02-foundation-models/01-concepts/model-selection/README.md](../10-Knowledge/02-foundation-models/01-concepts/model-selection/README.md) | 概念主题占位 | 补全或更新；draft |
| [10-Knowledge/02-foundation-models/01-concepts/reasoning/README.md](../10-Knowledge/02-foundation-models/01-concepts/reasoning/README.md) | 概念主题占位 | 补全或更新；draft |
| [10-Knowledge/02-foundation-models/01-concepts/tokenization/README.md](../10-Knowledge/02-foundation-models/01-concepts/tokenization/README.md) | 概念主题占位 | 补全或更新；draft |
| [10-Knowledge/02-foundation-models/01-concepts/training/README.md](../10-Knowledge/02-foundation-models/01-concepts/training/README.md) | 概念主题占位 | 补全或更新；draft |
| [10-Knowledge/02-foundation-models/01-concepts/transformer/README.md](../10-Knowledge/02-foundation-models/01-concepts/transformer/README.md) | 概念主题占位 | 补全或更新；draft |
| [10-Knowledge/02-foundation-models/04-labs/README.md](../10-Knowledge/02-foundation-models/04-labs/README.md) | 实验入口占位 | 补全或更新；verified |
| [10-Knowledge/02-foundation-models/README.md](../10-Knowledge/02-foundation-models/README.md) | 领域提纲·待补全 | 补全或更新；draft |
| [10-Knowledge/03-agent-core/04-labs/README.md](../10-Knowledge/03-agent-core/04-labs/README.md) | 实验入口占位 | 补全或更新；verified |
| [10-Knowledge/03-agent-core/05-code/agent-loop-python/README.md](../10-Knowledge/03-agent-core/05-code/agent-loop-python/README.md) | 工程说明占位 | 补全或更新；verified |
| [10-Knowledge/03-agent-core/05-code/agent-loop-python/pyproject.toml](../10-Knowledge/03-agent-core/05-code/agent-loop-python/pyproject.toml) | 工程配置初稿 | 补全或更新；实现、配置、样例或运行证据 |
| `10-Knowledge/03-agent-core/05-code/agent-loop-python/src/.gitkeep` | 源码/测试目录占位 | 移除空目录标记；同目录已由源码/测试替代 |
| `10-Knowledge/03-agent-core/05-code/agent-loop-python/tests/.gitkeep` | 源码/测试目录占位 | 移除空目录标记；同目录已由源码/测试替代 |
| [10-Knowledge/03-agent-core/README.md](../10-Knowledge/03-agent-core/README.md) | 领域提纲·待补全 | 补全或更新；draft |
| [10-Knowledge/04-context-engineering/01-concepts/00-overview.md](../10-Knowledge/04-context-engineering/01-concepts/00-overview.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/04-context-engineering/01-concepts/01-context-model.md](../10-Knowledge/04-context-engineering/01-concepts/01-context-model.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/04-context-engineering/01-concepts/02-failure-modes.md](../10-Knowledge/04-context-engineering/01-concepts/02-failure-modes.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/04-context-engineering/01-concepts/03-context-evaluation.md](../10-Knowledge/04-context-engineering/01-concepts/03-context-evaluation.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/04-context-engineering/02-patterns/01-context-builder.md](../10-Knowledge/04-context-engineering/02-patterns/01-context-builder.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/04-context-engineering/02-patterns/02-optimization-strategies.md](../10-Knowledge/04-context-engineering/02-patterns/02-optimization-strategies.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/04-context-engineering/04-labs/01-token-budget.ipynb](../10-Knowledge/04-context-engineering/04-labs/01-token-budget.ipynb) | Notebook 空代码占位 | 补全或更新；已实际执行 4 个代码单元 |
| [10-Knowledge/04-context-engineering/04-labs/02-context-compaction.ipynb](../10-Knowledge/04-context-engineering/04-labs/02-context-compaction.ipynb) | Notebook 空代码占位 | 补全或更新；已实际执行 3 个代码单元 |
| [10-Knowledge/04-context-engineering/04-labs/README.md](../10-Knowledge/04-context-engineering/04-labs/README.md) | 实验入口占位 | 补全或更新；verified |
| [10-Knowledge/04-context-engineering/README.md](../10-Knowledge/04-context-engineering/README.md) | 领域导航已有·待同步 | 补全或更新；draft |
| [10-Knowledge/04-context-engineering/references.md](../10-Knowledge/04-context-engineering/references.md) | 来源表已有·待复核 | 补全或更新；draft |
| [10-Knowledge/05-tools-skills-protocols/04-labs/README.md](../10-Knowledge/05-tools-skills-protocols/04-labs/README.md) | 实验入口占位 | 补全或更新；verified |
| [10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript/README.md](../10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript/README.md) | 工程说明占位 | 补全或更新；verified |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/README.md](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/README.md) | 工程说明占位 | 补全或更新；verified |
| [10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/README.md](../10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/README.md) | 工程说明占位 | 补全或更新；verified |
| [10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/package.json](../10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/package.json) | 工程配置初稿 | 补全或更新；实现、配置、样例或运行证据 |
| `10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/src/.gitkeep` | 源码/测试目录占位 | 移除空目录标记；同目录已由源码/测试替代 |
| `10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/test/.gitkeep` | 源码/测试目录占位 | 移除空目录标记；同目录已由源码/测试替代 |
| [10-Knowledge/05-tools-skills-protocols/README.md](../10-Knowledge/05-tools-skills-protocols/README.md) | 领域提纲·待补全 | 补全或更新；draft |
| [10-Knowledge/06-rag-and-knowledge-systems/01-concepts/01-rag-pipeline.md](../10-Knowledge/06-rag-and-knowledge-systems/01-concepts/01-rag-pipeline.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/06-rag-and-knowledge-systems/01-concepts/02-hybrid-retrieval-and-reranking.md](../10-Knowledge/06-rag-and-knowledge-systems/01-concepts/02-hybrid-retrieval-and-reranking.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/06-rag-and-knowledge-systems/02-patterns/hybrid-retrieval.md](../10-Knowledge/06-rag-and-knowledge-systems/02-patterns/hybrid-retrieval.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/06-rag-and-knowledge-systems/03-cases/运维RAG-双索引检索设计.md](../10-Knowledge/06-rag-and-knowledge-systems/03-cases/运维RAG-双索引检索设计.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/06-rag-and-knowledge-systems/03-cases/运维领域-RAG-问答系统.md](../10-Knowledge/06-rag-and-knowledge-systems/03-cases/运维领域-RAG-问答系统.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/06-rag-and-knowledge-systems/04-labs/README.md](../10-Knowledge/06-rag-and-knowledge-systems/04-labs/README.md) | 实验入口占位 | 补全或更新；verified |
| [10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/README.md](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/README.md) | 工程说明占位 | 补全或更新；verified |
| [10-Knowledge/06-rag-and-knowledge-systems/README.md](../10-Knowledge/06-rag-and-knowledge-systems/README.md) | 领域导航已有·待同步 | 补全或更新；draft |
| [10-Knowledge/07-state-and-memory/01-concepts/README.md](../10-Knowledge/07-state-and-memory/01-concepts/README.md) | 已有种子短稿·待扩写 | 补全或更新；draft |
| [10-Knowledge/07-state-and-memory/02-patterns/README.md](../10-Knowledge/07-state-and-memory/02-patterns/README.md) | 已有种子短稿·待扩写 | 补全或更新；draft |
| [10-Knowledge/07-state-and-memory/04-labs/README.md](../10-Knowledge/07-state-and-memory/04-labs/README.md) | 实验入口占位 | 补全或更新；verified |
| [10-Knowledge/07-state-and-memory/README.md](../10-Knowledge/07-state-and-memory/README.md) | 领域提纲·待补全 | 补全或更新；draft |
| [10-Knowledge/08-planning-workflow-multi-agent/03-cases/README.md](../10-Knowledge/08-planning-workflow-multi-agent/03-cases/README.md) | 案例入口占位 | 补全或更新；draft |
| [10-Knowledge/08-planning-workflow-multi-agent/04-labs/README.md](../10-Knowledge/08-planning-workflow-multi-agent/04-labs/README.md) | 实验入口占位 | 补全或更新；verified |
| [10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/README.md](../10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/README.md) | 工程说明占位 | 补全或更新；verified |
| [10-Knowledge/08-planning-workflow-multi-agent/README.md](../10-Knowledge/08-planning-workflow-multi-agent/README.md) | 领域提纲·待补全 | 补全或更新；draft |
| [10-Knowledge/09-runtime-harness-environment/04-labs/README.md](../10-Knowledge/09-runtime-harness-environment/04-labs/README.md) | 实验入口占位 | 补全或更新；verified |
| [10-Knowledge/09-runtime-harness-environment/README.md](../10-Knowledge/09-runtime-harness-environment/README.md) | 领域提纲·待补全 | 补全或更新；draft |
| [10-Knowledge/10-evaluation-observability/01-concepts/00-overview.md](../10-Knowledge/10-evaluation-observability/01-concepts/00-overview.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/10-evaluation-observability/01-concepts/01-evaluation-model.md](../10-Knowledge/10-evaluation-observability/01-concepts/01-evaluation-model.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/10-evaluation-observability/01-concepts/02-tasks-datasets-and-trials.md](../10-Knowledge/10-evaluation-observability/01-concepts/02-tasks-datasets-and-trials.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/10-evaluation-observability/01-concepts/03-graders-and-scoring.md](../10-Knowledge/10-evaluation-observability/01-concepts/03-graders-and-scoring.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/10-evaluation-observability/01-concepts/04-statistics-and-reliability.md](../10-Knowledge/10-evaluation-observability/01-concepts/04-statistics-and-reliability.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/10-evaluation-observability/01-concepts/05-traces-and-failure-analysis.md](../10-Knowledge/10-evaluation-observability/01-concepts/05-traces-and-failure-analysis.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/10-evaluation-observability/01-concepts/06-multi-agent-evaluation.md](../10-Knowledge/10-evaluation-observability/01-concepts/06-multi-agent-evaluation.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/10-evaluation-observability/02-patterns/01-evaluation-operations.md](../10-Knowledge/10-evaluation-observability/02-patterns/01-evaluation-operations.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/10-evaluation-observability/02-patterns/02-templates-and-checklists.md](../10-Knowledge/10-evaluation-observability/02-patterns/02-templates-and-checklists.md) | 技术正文已有·待核验补强 | 补全或更新；draft |
| [10-Knowledge/10-evaluation-observability/04-labs/README.md](../10-Knowledge/10-evaluation-observability/04-labs/README.md) | 实验入口占位 | 补全或更新；verified |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/README.md](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/README.md) | 工程说明占位 | 补全或更新；verified |
| [10-Knowledge/10-evaluation-observability/README.md](../10-Knowledge/10-evaluation-observability/README.md) | 领域导航已有·待同步 | 补全或更新；draft |
| [10-Knowledge/10-evaluation-observability/references.md](../10-Knowledge/10-evaluation-observability/references.md) | 来源表已有·待复核 | 补全或更新；reviewed |
| [10-Knowledge/11-safety-security-governance/04-labs/README.md](../10-Knowledge/11-safety-security-governance/04-labs/README.md) | 实验入口占位 | 补全或更新；verified |
| [10-Knowledge/11-safety-security-governance/README.md](../10-Knowledge/11-safety-security-governance/README.md) | 领域提纲·待补全 | 补全或更新；draft |
| [10-Knowledge/12-agent-learning/README.md](../10-Knowledge/12-agent-learning/README.md) | 领域提纲·待补全 | 补全或更新；draft |
| [10-Knowledge/13-application-engineering/03-cases/browser-agents/README.md](../10-Knowledge/13-application-engineering/03-cases/browser-agents/README.md) | 案例入口占位 | 补全或更新；draft |
| [10-Knowledge/13-application-engineering/03-cases/coding-agents/README.md](../10-Knowledge/13-application-engineering/03-cases/coding-agents/README.md) | 案例入口占位 | 补全或更新；draft |
| [10-Knowledge/13-application-engineering/03-cases/domain-agents/README.md](../10-Knowledge/13-application-engineering/03-cases/domain-agents/README.md) | 案例入口占位 | 补全或更新；draft |
| [10-Knowledge/13-application-engineering/03-cases/domain-agents/enterprise/README.md](../10-Knowledge/13-application-engineering/03-cases/domain-agents/enterprise/README.md) | 案例入口占位 | 补全或更新；draft |
| [10-Knowledge/13-application-engineering/03-cases/domain-agents/operations/README.md](../10-Knowledge/13-application-engineering/03-cases/domain-agents/operations/README.md) | 案例入口占位 | 补全或更新；draft |
| [10-Knowledge/13-application-engineering/03-cases/domain-agents/science/README.md](../10-Knowledge/13-application-engineering/03-cases/domain-agents/science/README.md) | 案例入口占位 | 补全或更新；draft |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/README.md](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/README.md) | 工程说明占位 | 补全或更新；verified |
| [10-Knowledge/13-application-engineering/README.md](../10-Knowledge/13-application-engineering/README.md) | 领域提纲·待补全 | 补全或更新；draft |
| [10-Knowledge/14-production-engineering/03-cases/failure-postmortems/README.md](../10-Knowledge/14-production-engineering/03-cases/failure-postmortems/README.md) | 案例入口占位 | 补全或更新；draft |
| [10-Knowledge/14-production-engineering/03-cases/production-systems/README.md](../10-Knowledge/14-production-engineering/03-cases/production-systems/README.md) | 案例入口占位 | 补全或更新；draft |
| [10-Knowledge/14-production-engineering/README.md](../10-Knowledge/14-production-engineering/README.md) | 领域提纲·待补全 | 补全或更新；draft |
| [10-Knowledge/15-multimodal-and-embodied/04-labs/README.md](../10-Knowledge/15-multimodal-and-embodied/04-labs/README.md) | 实验入口占位 | 补全或更新；draft |
| [10-Knowledge/15-multimodal-and-embodied/README.md](../10-Knowledge/15-multimodal-and-embodied/README.md) | 领域提纲·待补全 | 补全或更新；draft |
| [10-Knowledge/16-research-frontiers/03-cases/README.md](../10-Knowledge/16-research-frontiers/03-cases/README.md) | 案例入口占位 | 补全或更新；draft |
| [10-Knowledge/16-research-frontiers/README.md](../10-Knowledge/16-research-frontiers/README.md) | 领域提纲·待补全 | 补全或更新；draft |
| [10-Knowledge/README.md](../10-Knowledge/README.md) | 导航可用·待同步 | 补全或更新；导航、规范或记录 |
| [20-Projects/README.md](../20-Projects/README.md) | 项目准入说明可用·项目为空 | 补全或更新；导航、规范或记录 |
| [90-Sources/README.md](../90-Sources/README.md) | 来源导航可用·待完善 | 补全或更新；导航、规范或记录 |
| [90-Sources/books-and-courses/README.md](../90-Sources/books-and-courses/README.md) | 来源索引占位 | 补全或更新；导航、规范或记录 |
| [90-Sources/datasets-and-benchmarks/README.md](../90-Sources/datasets-and-benchmarks/README.md) | 来源索引占位 | 补全或更新；导航、规范或记录 |
| [90-Sources/official-docs/README.md](../90-Sources/official-docs/README.md) | 来源索引占位 | 补全或更新；导航、规范或记录 |
| [90-Sources/papers/README.md](../90-Sources/papers/README.md) | 来源索引占位 | 补全或更新；导航、规范或记录 |
| [90-Sources/repositories/README.md](../90-Sources/repositories/README.md) | 来源索引占位 | 补全或更新；导航、规范或记录 |
| [90-Sources/source-notes/README.md](../90-Sources/source-notes/README.md) | 导航可用·待同步 | 补全或更新；导航、规范或记录 |
| [90-Sources/standards/README.md](../90-Sources/standards/README.md) | 来源索引占位 | 补全或更新；导航、规范或记录 |
| [99-Inbox/README.md](../99-Inbox/README.md) | 收件箱说明可用 | 保留现有内容；不制造无必要修改 |
| [99-Inbox/experiment-ideas/README.md](../99-Inbox/experiment-ideas/README.md) | 队列说明可用·无待办正文 | 保留现有内容；不制造无必要修改 |
| [99-Inbox/quick-notes/素材收集箱.md](../99-Inbox/quick-notes/素材收集箱.md) | 模板与历史归档可用 | 保留现有内容；不制造无必要修改 |
| [99-Inbox/reading-queue/README.md](../99-Inbox/reading-queue/README.md) | 队列说明可用·无待办正文 | 保留现有内容；不制造无必要修改 |
| [99-Inbox/repository-queue/README.md](../99-Inbox/repository-queue/README.md) | 队列说明可用·无待办正文 | 保留现有内容；不制造无必要修改 |
| [99-Inbox/to-classify/README.md](../99-Inbox/to-classify/README.md) | 队列说明可用·无待办正文 | 保留现有内容；不制造无必要修改 |
| [README.md](../README.md) | 导航可用·待同步 | 补全或更新；导航、规范或记录 |
| [assets/README.md](../assets/README.md) | 素材清单可用·历史来源待查 | 补全或更新；导航、规范或记录 |
| `assets/context-clash-sharded-instruction.png` | 历史位图·未引用/待核验 | 保留历史图片；来源未确认，见素材登记 |
| `assets/context-engineering-core.png` | 历史位图·未引用/待核验 | 保留历史图片；来源未确认，见素材登记 |
| [assets/context-engineering-core.svg](../assets/context-engineering-core.svg) | 已引用图示·源文件可解析 | 保留现有内容；不制造无必要修改 |
| `assets/evaluation-code-based-graders.png` | 历史位图·未引用/待核验 | 保留历史图片；来源未确认，见素材登记 |
| `assets/evaluation-components-for-agents.png` | 历史位图·未引用/待核验 | 保留历史图片；来源未确认，见素材登记 |
| `assets/evaluation-human-graders.png` | 历史位图·未引用/待核验 | 保留历史图片；来源未确认，见素材登记 |
| `assets/evaluation-model-based-graders.png` | 历史位图·未引用/待核验 | 保留历史图片；来源未确认，见素材登记 |
| `assets/evaluation-single-turn-vs-agent.png` | 历史位图·未引用/待核验 | 保留历史图片；来源未确认，见素材登记 |
| `assets/tool-calling-irrelevance-score-gemma.png` | 历史位图·未引用/待核验 | 保留历史图片；来源未确认，见素材登记 |
| [scripts/README.md](../scripts/README.md) | 维护工具占位 | 补全或更新；导航、规范或记录 |

## 新增文件

| 文件 | 内容与状态 |
| --- | --- |
| [.github/workflows/docs.yml](../.github/workflows/docs.yml) | 新增；实现、配置、样例或运行证据 |
| [.github/workflows/notebooks.yml](../.github/workflows/notebooks.yml) | 新增；实现、配置、样例或运行证据 |
| [.github/workflows/python.yml](../.github/workflows/python.yml) | 新增；实现、配置、样例或运行证据 |
| [.github/workflows/typescript.yml](../.github/workflows/typescript.yml) | 新增；实现、配置、样例或运行证据 |
| [00-Home/Completion-Report.md](../00-Home/Completion-Report.md) | 新增；导航、规范或记录 |
| [00-Home/Learning-Writing-Guide.md](../00-Home/Learning-Writing-Guide.md) | 新增；导航、规范或记录 |
| [00-Home/Verification-Report.md](../00-Home/Verification-Report.md) | 新增；导航、规范或记录 |
| [00-Home/templates/case.md](../00-Home/templates/case.md) | 新增；导航、规范或记录 |
| [00-Home/templates/concept.md](../00-Home/templates/concept.md) | 新增；导航、规范或记录 |
| [00-Home/templates/lab.md](../00-Home/templates/lab.md) | 新增；导航、规范或记录 |
| [00-Home/templates/pattern.md](../00-Home/templates/pattern.md) | 新增；导航、规范或记录 |
| [00-Home/templates/source.md](../00-Home/templates/source.md) | 新增；导航、规范或记录 |
| [00-Home/verification/browser-tests.txt](../00-Home/verification/browser-tests.txt) | 新增；实现、配置、样例或运行证据 |
| [00-Home/verification/inventory.json](../00-Home/verification/inventory.json) | 新增；实现、配置、样例或运行证据 |
| [00-Home/verification/links.json](../00-Home/verification/links.json) | 新增；实现、配置、样例或运行证据 |
| [00-Home/verification/mcp-tests.txt](../00-Home/verification/mcp-tests.txt) | 新增；实现、配置、样例或运行证据 |
| [00-Home/verification/metadata.json](../00-Home/verification/metadata.json) | 新增；实现、配置、样例或运行证据 |
| [00-Home/verification/notebooks.jsonl](../00-Home/verification/notebooks.jsonl) | 新增；实现、配置、样例或运行证据 |
| [00-Home/verification/python-tests.txt](../00-Home/verification/python-tests.txt) | 新增；实现、配置、样例或运行证据 |
| [00-Home/verification/tool-runtime-tests.txt](../00-Home/verification/tool-runtime-tests.txt) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/01-ai-foundations/04-labs/01-math-and-optimization.ipynb](../10-Knowledge/01-ai-foundations/04-labs/01-math-and-optimization.ipynb) | 新增；已实际执行 5 个代码单元 |
| [10-Knowledge/01-ai-foundations/04-labs/02-generalization-and-calibration.ipynb](../10-Knowledge/01-ai-foundations/04-labs/02-generalization-and-calibration.ipynb) | 新增；已实际执行 4 个代码单元 |
| [10-Knowledge/01-ai-foundations/04-labs/deep-learning/01-autograd-and-training.ipynb](../10-Knowledge/01-ai-foundations/04-labs/deep-learning/01-autograd-and-training.ipynb) | 新增；已实际执行 5 个代码单元 |
| [10-Knowledge/01-ai-foundations/04-labs/run-report.md](../10-Knowledge/01-ai-foundations/04-labs/run-report.md) | 新增；verified |
| [10-Knowledge/01-ai-foundations/04-labs/search-and-rl/01-search-and-value-learning.ipynb](../10-Knowledge/01-ai-foundations/04-labs/search-and-rl/01-search-and-value-learning.ipynb) | 新增；已实际执行 5 个代码单元 |
| [10-Knowledge/01-ai-foundations/05-code/README.md](../10-Knowledge/01-ai-foundations/05-code/README.md) | 新增；verified |
| [10-Knowledge/01-ai-foundations/05-code/foundations_core.py](../10-Knowledge/01-ai-foundations/05-code/foundations_core.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/01-ai-foundations/05-code/requirements.txt](../10-Knowledge/01-ai-foundations/05-code/requirements.txt) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/01-ai-foundations/references.md](../10-Knowledge/01-ai-foundations/references.md) | 新增；draft |
| [10-Knowledge/02-foundation-models/04-labs/01-tokenization-and-attention.ipynb](../10-Knowledge/02-foundation-models/04-labs/01-tokenization-and-attention.ipynb) | 新增；已实际执行 6 个代码单元 |
| [10-Knowledge/02-foundation-models/04-labs/02-decoding-cache-and-precision.ipynb](../10-Knowledge/02-foundation-models/04-labs/02-decoding-cache-and-precision.ipynb) | 新增；已实际执行 7 个代码单元 |
| [10-Knowledge/02-foundation-models/04-labs/run-report.md](../10-Knowledge/02-foundation-models/04-labs/run-report.md) | 新增；verified |
| [10-Knowledge/02-foundation-models/05-code/README.md](../10-Knowledge/02-foundation-models/05-code/README.md) | 新增；verified |
| [10-Knowledge/02-foundation-models/05-code/model_mechanics.py](../10-Knowledge/02-foundation-models/05-code/model_mechanics.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/02-foundation-models/05-code/requirements.txt](../10-Knowledge/02-foundation-models/05-code/requirements.txt) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/02-foundation-models/references.md](../10-Knowledge/02-foundation-models/references.md) | 新增；draft |
| [10-Knowledge/03-agent-core/01-concepts/01-agent-boundaries.md](../10-Knowledge/03-agent-core/01-concepts/01-agent-boundaries.md) | 新增；draft |
| [10-Knowledge/03-agent-core/01-concepts/02-agent-loop.md](../10-Knowledge/03-agent-core/01-concepts/02-agent-loop.md) | 新增；draft |
| [10-Knowledge/03-agent-core/01-concepts/03-model-adapters.md](../10-Knowledge/03-agent-core/01-concepts/03-model-adapters.md) | 新增；draft |
| [10-Knowledge/03-agent-core/02-patterns/01-react-and-plan-execute.md](../10-Knowledge/03-agent-core/02-patterns/01-react-and-plan-execute.md) | 新增；draft |
| [10-Knowledge/03-agent-core/02-patterns/02-reflection-verification-human-loop.md](../10-Knowledge/03-agent-core/02-patterns/02-reflection-verification-human-loop.md) | 新增；draft |
| [10-Knowledge/03-agent-core/04-labs/01-agent-loop.ipynb](../10-Knowledge/03-agent-core/04-labs/01-agent-loop.ipynb) | 新增；已实际执行 5 个代码单元 |
| [10-Knowledge/03-agent-core/05-code/agent-loop-python/fixtures/teaching-tasks.json](../10-Knowledge/03-agent-core/05-code/agent-loop-python/fixtures/teaching-tasks.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/03-agent-core/05-code/agent-loop-python/requirements.lock](../10-Knowledge/03-agent-core/05-code/agent-loop-python/requirements.lock) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/03-agent-core/05-code/agent-loop-python/src/agent_loop/__init__.py](../10-Knowledge/03-agent-core/05-code/agent-loop-python/src/agent_loop/__init__.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/03-agent-core/05-code/agent-loop-python/src/agent_loop/cli.py](../10-Knowledge/03-agent-core/05-code/agent-loop-python/src/agent_loop/cli.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/03-agent-core/05-code/agent-loop-python/src/agent_loop/loop.py](../10-Knowledge/03-agent-core/05-code/agent-loop-python/src/agent_loop/loop.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/03-agent-core/05-code/agent-loop-python/src/agent_loop/models.py](../10-Knowledge/03-agent-core/05-code/agent-loop-python/src/agent_loop/models.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/03-agent-core/05-code/agent-loop-python/src/agent_loop/tools.py](../10-Knowledge/03-agent-core/05-code/agent-loop-python/src/agent_loop/tools.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/03-agent-core/05-code/agent-loop-python/src/agent_loop/trace.py](../10-Knowledge/03-agent-core/05-code/agent-loop-python/src/agent_loop/trace.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/03-agent-core/05-code/agent-loop-python/tests/test_loop.py](../10-Knowledge/03-agent-core/05-code/agent-loop-python/tests/test_loop.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/03-agent-core/references.md](../10-Knowledge/03-agent-core/references.md) | 新增；draft |
| [10-Knowledge/04-context-engineering/04-labs/context_lab.py](../10-Knowledge/04-context-engineering/04-labs/context_lab.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/01-concepts/01-structured-output-and-tool-contracts.md](../10-Knowledge/05-tools-skills-protocols/01-concepts/01-structured-output-and-tool-contracts.md) | 新增；draft |
| [10-Knowledge/05-tools-skills-protocols/01-concepts/02-skills-and-progressive-disclosure.md](../10-Knowledge/05-tools-skills-protocols/01-concepts/02-skills-and-progressive-disclosure.md) | 新增；draft |
| [10-Knowledge/05-tools-skills-protocols/01-concepts/03-mcp.md](../10-Knowledge/05-tools-skills-protocols/01-concepts/03-mcp.md) | 新增；draft |
| [10-Knowledge/05-tools-skills-protocols/01-concepts/04-agent-communication-protocols.md](../10-Knowledge/05-tools-skills-protocols/01-concepts/04-agent-communication-protocols.md) | 新增；draft |
| [10-Knowledge/05-tools-skills-protocols/01-concepts/05-delegated-authorization.md](../10-Knowledge/05-tools-skills-protocols/01-concepts/05-delegated-authorization.md) | 新增；draft |
| [10-Knowledge/05-tools-skills-protocols/02-patterns/01-tool-runtime.md](../10-Knowledge/05-tools-skills-protocols/02-patterns/01-tool-runtime.md) | 新增；draft |
| [10-Knowledge/05-tools-skills-protocols/04-labs/01-tool-contracts-and-errors.ipynb](../10-Knowledge/05-tools-skills-protocols/04-labs/01-tool-contracts-and-errors.ipynb) | 新增；已实际执行 5 个代码单元 |
| [10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript/package-lock.json](../10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript/package-lock.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript/package.json](../10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript/package.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript/src/client.ts](../10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript/src/client.ts) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript/src/server.ts](../10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript/src/server.ts) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript/test/integration.test.ts](../10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript/test/integration.test.ts) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript/tsconfig.json](../10-Knowledge/05-tools-skills-protocols/05-code/mcp-server-typescript/tsconfig.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/agent-state.schema.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/agent-state.schema.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/eval-task.schema.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/eval-task.schema.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/agent-state.invalid.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/agent-state.invalid.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/agent-state.valid.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/agent-state.valid.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/eval-task.invalid.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/eval-task.invalid.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/eval-task.valid.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/eval-task.valid.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/tool-call.invalid.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/tool-call.invalid.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/tool-call.valid.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/tool-call.valid.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/tool-result.invalid.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/tool-result.invalid.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/tool-result.valid.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/tool-result.valid.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/trace-event.invalid.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/trace-event.invalid.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/trace-event.valid.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/trace-event.valid.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/trial-result.invalid.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/trial-result.invalid.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/trial-result.valid.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/examples/trial-result.valid.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/tool-call.schema.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/tool-call.schema.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/tool-result.schema.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/tool-result.schema.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/trace-event.schema.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/trace-event.schema.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/trial-result.schema.json](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/trial-result.schema.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/validate_examples.py](../10-Knowledge/05-tools-skills-protocols/05-code/shared-schemas/validate_examples.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/package-lock.json](../10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/package-lock.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/src/contracts.ts](../10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/src/contracts.ts) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/src/registry.ts](../10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/src/registry.ts) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/src/runtime.ts](../10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/src/runtime.ts) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/test/runtime.test.ts](../10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/test/runtime.test.ts) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/test/schemas.test.ts](../10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/test/schemas.test.ts) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/tsconfig.json](../10-Knowledge/05-tools-skills-protocols/05-code/tool-runtime-typescript/tsconfig.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/05-tools-skills-protocols/references.md](../10-Knowledge/05-tools-skills-protocols/references.md) | 新增；draft |
| [10-Knowledge/06-rag-and-knowledge-systems/01-concepts/03-ingestion-and-parsing.md](../10-Knowledge/06-rag-and-knowledge-systems/01-concepts/03-ingestion-and-parsing.md) | 新增；draft |
| [10-Knowledge/06-rag-and-knowledge-systems/01-concepts/04-chunking-and-metadata.md](../10-Knowledge/06-rag-and-knowledge-systems/01-concepts/04-chunking-and-metadata.md) | 新增；draft |
| [10-Knowledge/06-rag-and-knowledge-systems/01-concepts/05-index-lifecycle.md](../10-Knowledge/06-rag-and-knowledge-systems/01-concepts/05-index-lifecycle.md) | 新增；draft |
| [10-Knowledge/06-rag-and-knowledge-systems/01-concepts/06-query-planning-and-graph-retrieval.md](../10-Knowledge/06-rag-and-knowledge-systems/01-concepts/06-query-planning-and-graph-retrieval.md) | 新增；draft |
| [10-Knowledge/06-rag-and-knowledge-systems/01-concepts/07-citations-and-grounding.md](../10-Knowledge/06-rag-and-knowledge-systems/01-concepts/07-citations-and-grounding.md) | 新增；draft |
| [10-Knowledge/06-rag-and-knowledge-systems/04-labs/01-hybrid-retrieval-evaluation.ipynb](../10-Knowledge/06-rag-and-knowledge-systems/04-labs/01-hybrid-retrieval-evaluation.ipynb) | 新增；已实际执行 5 个代码单元 |
| [10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/fixtures/README.md](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/fixtures/README.md) | 新增；verified |
| [10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/fixtures/corpus.jsonl](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/fixtures/corpus.jsonl) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/fixtures/queries.jsonl](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/fixtures/queries.jsonl) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/pyproject.toml](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/pyproject.toml) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/requirements.lock](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/requirements.lock) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/run-report.json](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/run-report.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/src/rag_pipeline/__init__.py](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/src/rag_pipeline/__init__.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/src/rag_pipeline/chunking.py](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/src/rag_pipeline/chunking.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/src/rag_pipeline/citations.py](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/src/rag_pipeline/citations.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/src/rag_pipeline/cli.py](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/src/rag_pipeline/cli.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/src/rag_pipeline/ingest.py](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/src/rag_pipeline/ingest.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/src/rag_pipeline/ranking.py](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/src/rag_pipeline/ranking.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/src/rag_pipeline/retrieval.py](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/src/rag_pipeline/retrieval.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/tests/test_pipeline.py](../10-Knowledge/06-rag-and-knowledge-systems/05-code/rag-pipeline-python/tests/test_pipeline.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/06-rag-and-knowledge-systems/references.md](../10-Knowledge/06-rag-and-knowledge-systems/references.md) | 新增；draft |
| [10-Knowledge/07-state-and-memory/01-concepts/01-state-and-checkpoints.md](../10-Knowledge/07-state-and-memory/01-concepts/01-state-and-checkpoints.md) | 新增；draft |
| [10-Knowledge/07-state-and-memory/01-concepts/02-memory-lifecycle.md](../10-Knowledge/07-state-and-memory/01-concepts/02-memory-lifecycle.md) | 新增；draft |
| [10-Knowledge/07-state-and-memory/01-concepts/03-memory-evaluation.md](../10-Knowledge/07-state-and-memory/01-concepts/03-memory-evaluation.md) | 新增；draft |
| [10-Knowledge/07-state-and-memory/02-patterns/01-memory-write-and-retrieval.md](../10-Knowledge/07-state-and-memory/02-patterns/01-memory-write-and-retrieval.md) | 新增；draft |
| [10-Knowledge/07-state-and-memory/02-patterns/02-conflict-and-forgetting.md](../10-Knowledge/07-state-and-memory/02-patterns/02-conflict-and-forgetting.md) | 新增；draft |
| [10-Knowledge/07-state-and-memory/04-labs/01-state-memory-and-conflicts.ipynb](../10-Knowledge/07-state-and-memory/04-labs/01-state-memory-and-conflicts.ipynb) | 新增；已实际执行 4 个代码单元 |
| [10-Knowledge/07-state-and-memory/05-code/state-memory-python/README.md](../10-Knowledge/07-state-and-memory/05-code/state-memory-python/README.md) | 新增；verified |
| [10-Knowledge/07-state-and-memory/05-code/state-memory-python/fixtures/teaching-tasks.json](../10-Knowledge/07-state-and-memory/05-code/state-memory-python/fixtures/teaching-tasks.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/07-state-and-memory/05-code/state-memory-python/pyproject.toml](../10-Knowledge/07-state-and-memory/05-code/state-memory-python/pyproject.toml) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/07-state-and-memory/05-code/state-memory-python/requirements.lock](../10-Knowledge/07-state-and-memory/05-code/state-memory-python/requirements.lock) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/07-state-and-memory/05-code/state-memory-python/src/state_memory/__init__.py](../10-Knowledge/07-state-and-memory/05-code/state-memory-python/src/state_memory/__init__.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/07-state-and-memory/05-code/state-memory-python/src/state_memory/checkpoint.py](../10-Knowledge/07-state-and-memory/05-code/state-memory-python/src/state_memory/checkpoint.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/07-state-and-memory/05-code/state-memory-python/src/state_memory/memory.py](../10-Knowledge/07-state-and-memory/05-code/state-memory-python/src/state_memory/memory.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/07-state-and-memory/05-code/state-memory-python/src/state_memory/state.py](../10-Knowledge/07-state-and-memory/05-code/state-memory-python/src/state_memory/state.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/07-state-and-memory/05-code/state-memory-python/tests/test_memory.py](../10-Knowledge/07-state-and-memory/05-code/state-memory-python/tests/test_memory.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/07-state-and-memory/references.md](../10-Knowledge/07-state-and-memory/references.md) | 新增；draft |
| [10-Knowledge/08-planning-workflow-multi-agent/01-concepts/01-planning-and-replanning.md](../10-Knowledge/08-planning-workflow-multi-agent/01-concepts/01-planning-and-replanning.md) | 新增；draft |
| [10-Knowledge/08-planning-workflow-multi-agent/01-concepts/02-workflow-state-machines.md](../10-Knowledge/08-planning-workflow-multi-agent/01-concepts/02-workflow-state-machines.md) | 新增；draft |
| [10-Knowledge/08-planning-workflow-multi-agent/01-concepts/03-multi-agent-topologies.md](../10-Knowledge/08-planning-workflow-multi-agent/01-concepts/03-multi-agent-topologies.md) | 新增；draft |
| [10-Knowledge/08-planning-workflow-multi-agent/02-patterns/01-task-contract-and-handoff.md](../10-Knowledge/08-planning-workflow-multi-agent/02-patterns/01-task-contract-and-handoff.md) | 新增；draft |
| [10-Knowledge/08-planning-workflow-multi-agent/02-patterns/02-shared-state-and-merge.md](../10-Knowledge/08-planning-workflow-multi-agent/02-patterns/02-shared-state-and-merge.md) | 新增；draft |
| [10-Knowledge/08-planning-workflow-multi-agent/03-cases/01-single-vs-multi-agent.md](../10-Knowledge/08-planning-workflow-multi-agent/03-cases/01-single-vs-multi-agent.md) | 新增；draft |
| [10-Knowledge/08-planning-workflow-multi-agent/04-labs/01-single-vs-multi-agent.ipynb](../10-Knowledge/08-planning-workflow-multi-agent/04-labs/01-single-vs-multi-agent.ipynb) | 新增；已实际执行 5 个代码单元 |
| [10-Knowledge/08-planning-workflow-multi-agent/04-labs/artifacts/experiment.json](../10-Knowledge/08-planning-workflow-multi-agent/04-labs/artifacts/experiment.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/08-planning-workflow-multi-agent/04-labs/run-report.md](../10-Knowledge/08-planning-workflow-multi-agent/04-labs/run-report.md) | 新增；verified |
| [10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/examples/run_comparison.py](../10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/examples/run_comparison.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/pyproject.toml](../10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/pyproject.toml) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/src/multi_agent/__init__.py](../10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/src/multi_agent/__init__.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/src/multi_agent/contracts.py](../10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/src/multi_agent/contracts.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/src/multi_agent/fixture.py](../10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/src/multi_agent/fixture.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/src/multi_agent/merge.py](../10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/src/multi_agent/merge.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/src/multi_agent/router.py](../10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/src/multi_agent/router.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/src/multi_agent/supervisor.py](../10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/src/multi_agent/supervisor.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/tests/test_runtime.py](../10-Knowledge/08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/tests/test_runtime.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/08-planning-workflow-multi-agent/references.md](../10-Knowledge/08-planning-workflow-multi-agent/references.md) | 新增；draft |
| [10-Knowledge/09-runtime-harness-environment/01-concepts/01-runtime-and-harness.md](../10-Knowledge/09-runtime-harness-environment/01-concepts/01-runtime-and-harness.md) | 新增；draft |
| [10-Knowledge/09-runtime-harness-environment/01-concepts/02-durable-execution.md](../10-Knowledge/09-runtime-harness-environment/01-concepts/02-durable-execution.md) | 新增；draft |
| [10-Knowledge/09-runtime-harness-environment/01-concepts/03-concurrency-and-budgets.md](../10-Knowledge/09-runtime-harness-environment/01-concepts/03-concurrency-and-budgets.md) | 新增；draft |
| [10-Knowledge/09-runtime-harness-environment/01-concepts/04-workspaces-sandboxes-and-artifacts.md](../10-Knowledge/09-runtime-harness-environment/01-concepts/04-workspaces-sandboxes-and-artifacts.md) | 新增；draft |
| [10-Knowledge/09-runtime-harness-environment/02-patterns/01-retry-idempotency-compensation.md](../10-Knowledge/09-runtime-harness-environment/02-patterns/01-retry-idempotency-compensation.md) | 新增；draft |
| [10-Knowledge/09-runtime-harness-environment/04-labs/01-recovery-and-idempotency.ipynb](../10-Knowledge/09-runtime-harness-environment/04-labs/01-recovery-and-idempotency.ipynb) | 新增；已实际执行 4 个代码单元 |
| [10-Knowledge/09-runtime-harness-environment/04-labs/artifacts/recovery.json](../10-Knowledge/09-runtime-harness-environment/04-labs/artifacts/recovery.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/09-runtime-harness-environment/04-labs/run-report.md](../10-Knowledge/09-runtime-harness-environment/04-labs/run-report.md) | 新增；verified |
| [10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python/README.md](../10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python/README.md) | 新增；verified |
| [10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python/pyproject.toml](../10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python/pyproject.toml) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python/src/recoverable_runtime/__init__.py](../10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python/src/recoverable_runtime/__init__.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python/src/recoverable_runtime/events.py](../10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python/src/recoverable_runtime/events.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python/src/recoverable_runtime/recovery.py](../10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python/src/recoverable_runtime/recovery.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python/src/recoverable_runtime/runner.py](../10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python/src/recoverable_runtime/runner.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python/tests/test_recovery.py](../10-Knowledge/09-runtime-harness-environment/05-code/recoverable-runtime-python/tests/test_recovery.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/09-runtime-harness-environment/references.md](../10-Knowledge/09-runtime-harness-environment/references.md) | 新增；draft |
| [10-Knowledge/10-evaluation-observability/03-cases/01-from-task-dataset-to-regression.md](../10-Knowledge/10-evaluation-observability/03-cases/01-from-task-dataset-to-regression.md) | 新增；draft |
| [10-Knowledge/10-evaluation-observability/04-labs/01-evaluation-and-regression.ipynb](../10-Knowledge/10-evaluation-observability/04-labs/01-evaluation-and-regression.ipynb) | 新增；已实际执行 4 个代码单元 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/fixtures/README.md](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/fixtures/README.md) | 新增；verified |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/fixtures/tasks.jsonl](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/fixtures/tasks.jsonl) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/pyproject.toml](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/pyproject.toml) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/reports/baseline/summary.json](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/reports/baseline/summary.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/reports/baseline/trials.jsonl](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/reports/baseline/trials.jsonl) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/reports/candidate/summary.json](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/reports/candidate/summary.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/reports/candidate/trials.jsonl](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/reports/candidate/trials.jsonl) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/reports/comparison.json](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/reports/comparison.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/requirements.lock](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/requirements.lock) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/src/eval_harness/__init__.py](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/src/eval_harness/__init__.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/src/eval_harness/cli.py](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/src/eval_harness/cli.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/src/eval_harness/graders.py](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/src/eval_harness/graders.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/src/eval_harness/reports.py](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/src/eval_harness/reports.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/src/eval_harness/runner.py](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/src/eval_harness/runner.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/src/eval_harness/statistics.py](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/src/eval_harness/statistics.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/src/eval_harness/tasks.py](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/src/eval_harness/tasks.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/tests/test_harness.py](../10-Knowledge/10-evaluation-observability/05-code/eval-harness-python/tests/test_harness.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/11-safety-security-governance/01-concepts/01-threat-model-and-injection.md](../10-Knowledge/11-safety-security-governance/01-concepts/01-threat-model-and-injection.md) | 新增；draft |
| [10-Knowledge/11-safety-security-governance/01-concepts/02-identity-and-permissions.md](../10-Knowledge/11-safety-security-governance/01-concepts/02-identity-and-permissions.md) | 新增；draft |
| [10-Knowledge/11-safety-security-governance/01-concepts/03-data-secrets-and-audit.md](../10-Knowledge/11-safety-security-governance/01-concepts/03-data-secrets-and-audit.md) | 新增；draft |
| [10-Knowledge/11-safety-security-governance/01-concepts/04-supply-chain-and-response.md](../10-Knowledge/11-safety-security-governance/01-concepts/04-supply-chain-and-response.md) | 新增；draft |
| [10-Knowledge/11-safety-security-governance/04-labs/01-policy-and-injection.ipynb](../10-Knowledge/11-safety-security-governance/04-labs/01-policy-and-injection.ipynb) | 新增；已实际执行 4 个代码单元 |
| [10-Knowledge/11-safety-security-governance/04-labs/artifacts/policy.json](../10-Knowledge/11-safety-security-governance/04-labs/artifacts/policy.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/11-safety-security-governance/04-labs/run-report.md](../10-Knowledge/11-safety-security-governance/04-labs/run-report.md) | 新增；verified |
| [10-Knowledge/11-safety-security-governance/05-code/README.md](../10-Knowledge/11-safety-security-governance/05-code/README.md) | 新增；verified |
| [10-Knowledge/11-safety-security-governance/05-code/policy_lab.py](../10-Knowledge/11-safety-security-governance/05-code/policy_lab.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/11-safety-security-governance/05-code/test_policy.py](../10-Knowledge/11-safety-security-governance/05-code/test_policy.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/11-safety-security-governance/references.md](../10-Knowledge/11-safety-security-governance/references.md) | 新增；draft |
| [10-Knowledge/12-agent-learning/01-concepts/01-trajectory-data.md](../10-Knowledge/12-agent-learning/01-concepts/01-trajectory-data.md) | 新增；draft |
| [10-Knowledge/12-agent-learning/01-concepts/02-sft-and-preference-optimization.md](../10-Knowledge/12-agent-learning/01-concepts/02-sft-and-preference-optimization.md) | 新增；draft |
| [10-Knowledge/12-agent-learning/01-concepts/03-agentic-reinforcement-learning.md](../10-Knowledge/12-agent-learning/01-concepts/03-agentic-reinforcement-learning.md) | 新增；draft |
| [10-Knowledge/12-agent-learning/01-concepts/04-verifiers-and-reward-hacking.md](../10-Knowledge/12-agent-learning/01-concepts/04-verifiers-and-reward-hacking.md) | 新增；draft |
| [10-Knowledge/12-agent-learning/02-patterns/01-feedback-to-improvement.md](../10-Knowledge/12-agent-learning/02-patterns/01-feedback-to-improvement.md) | 新增；draft |
| [10-Knowledge/12-agent-learning/04-labs/01-trajectories-and-rewards.ipynb](../10-Knowledge/12-agent-learning/04-labs/01-trajectories-and-rewards.ipynb) | 新增；已实际执行 6 个代码单元 |
| [10-Knowledge/12-agent-learning/04-labs/README.md](../10-Knowledge/12-agent-learning/04-labs/README.md) | 新增；draft |
| [10-Knowledge/12-agent-learning/05-code/README.md](../10-Knowledge/12-agent-learning/05-code/README.md) | 新增；verified |
| [10-Knowledge/12-agent-learning/05-code/learning.py](../10-Knowledge/12-agent-learning/05-code/learning.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/12-agent-learning/05-code/test_learning.py](../10-Knowledge/12-agent-learning/05-code/test_learning.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/12-agent-learning/references.md](../10-Knowledge/12-agent-learning/references.md) | 新增；draft |
| [10-Knowledge/13-application-engineering/01-concepts/01-backend-and-streaming.md](../10-Knowledge/13-application-engineering/01-concepts/01-backend-and-streaming.md) | 新增；draft |
| [10-Knowledge/13-application-engineering/01-concepts/02-human-agent-interaction.md](../10-Knowledge/13-application-engineering/01-concepts/02-human-agent-interaction.md) | 新增；draft |
| [10-Knowledge/13-application-engineering/01-concepts/03-storage-and-multitenancy.md](../10-Knowledge/13-application-engineering/01-concepts/03-storage-and-multitenancy.md) | 新增；draft |
| [10-Knowledge/13-application-engineering/01-concepts/04-model-gateways.md](../10-Knowledge/13-application-engineering/01-concepts/04-model-gateways.md) | 新增；draft |
| [10-Knowledge/13-application-engineering/05-code/README.md](../10-Knowledge/13-application-engineering/05-code/README.md) | 新增；verified |
| [10-Knowledge/13-application-engineering/05-code/application_cases.py](../10-Knowledge/13-application-engineering/05-code/application_cases.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/.gitignore](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/.gitignore) | 新增；维护配置 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/recovery/fill-1.png](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/recovery/fill-1.png) | 新增；本地构造页面截图 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/recovery/state.json](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/recovery/state.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/recovery/submit-1.png](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/recovery/submit-1.png) | 新增；本地构造页面截图 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/success/denied-state.json](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/success/denied-state.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/success/fill-1.png](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/success/fill-1.png) | 新增；本地构造页面截图 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/success/state.json](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/success/state.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/success/submit-1.png](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/success/submit-1.png) | 新增；本地构造页面截图 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/test-report.txt](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/test-report.txt) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/timeout/fill-1.png](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/timeout/fill-1.png) | 新增；本地构造页面截图 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/timeout/state.json](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/artifacts/timeout/state.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/fixtures/index.html](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/fixtures/index.html) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/package-lock.json](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/package-lock.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/package.json](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/package.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/src/actions.ts](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/src/actions.ts) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/src/policy.ts](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/src/policy.ts) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/src/state.ts](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/src/state.ts) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/test/browser.test.ts](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/test/browser.test.ts) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/tsconfig.json](../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/tsconfig.json) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/13-application-engineering/05-code/test_application_cases.py](../10-Knowledge/13-application-engineering/05-code/test_application_cases.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/13-application-engineering/references.md](../10-Knowledge/13-application-engineering/references.md) | 新增；draft |
| [10-Knowledge/14-production-engineering/01-concepts/01-deployment-and-capacity.md](../10-Knowledge/14-production-engineering/01-concepts/01-deployment-and-capacity.md) | 新增；draft |
| [10-Knowledge/14-production-engineering/01-concepts/02-slos-reliability-and-cost.md](../10-Knowledge/14-production-engineering/01-concepts/02-slos-reliability-and-cost.md) | 新增；draft |
| [10-Knowledge/14-production-engineering/01-concepts/03-release-and-recovery.md](../10-Knowledge/14-production-engineering/01-concepts/03-release-and-recovery.md) | 新增；draft |
| [10-Knowledge/14-production-engineering/05-code/README.md](../10-Knowledge/14-production-engineering/05-code/README.md) | 新增；verified |
| [10-Knowledge/14-production-engineering/05-code/production_checks.py](../10-Knowledge/14-production-engineering/05-code/production_checks.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/14-production-engineering/references.md](../10-Knowledge/14-production-engineering/references.md) | 新增；draft |
| [10-Knowledge/15-multimodal-and-embodied/01-concepts/01-vision-and-document-ai.md](../10-Knowledge/15-multimodal-and-embodied/01-concepts/01-vision-and-document-ai.md) | 新增；draft |
| [10-Knowledge/15-multimodal-and-embodied/01-concepts/02-speech-audio-and-video.md](../10-Knowledge/15-multimodal-and-embodied/01-concepts/02-speech-audio-and-video.md) | 新增；draft |
| [10-Knowledge/15-multimodal-and-embodied/01-concepts/03-multimodal-context-and-rag.md](../10-Knowledge/15-multimodal-and-embodied/01-concepts/03-multimodal-context-and-rag.md) | 新增；draft |
| [10-Knowledge/15-multimodal-and-embodied/01-concepts/04-computer-use-vla-and-embodied.md](../10-Knowledge/15-multimodal-and-embodied/01-concepts/04-computer-use-vla-and-embodied.md) | 新增；draft |
| [10-Knowledge/15-multimodal-and-embodied/04-labs/01-document-evidence.ipynb](../10-Knowledge/15-multimodal-and-embodied/04-labs/01-document-evidence.ipynb) | 新增；已实际执行 5 个代码单元 |
| [10-Knowledge/15-multimodal-and-embodied/05-code/README.md](../10-Knowledge/15-multimodal-and-embodied/05-code/README.md) | 新增；verified |
| [10-Knowledge/15-multimodal-and-embodied/05-code/evidence.py](../10-Knowledge/15-multimodal-and-embodied/05-code/evidence.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/15-multimodal-and-embodied/05-code/test_evidence.py](../10-Knowledge/15-multimodal-and-embodied/05-code/test_evidence.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/15-multimodal-and-embodied/references.md](../10-Knowledge/15-multimodal-and-embodied/references.md) | 新增；draft |
| [10-Knowledge/16-research-frontiers/01-concepts/01-long-horizon-agents.md](../10-Knowledge/16-research-frontiers/01-concepts/01-long-horizon-agents.md) | 新增；draft |
| [10-Knowledge/16-research-frontiers/01-concepts/02-self-improvement-and-agent-swarms.md](../10-Knowledge/16-research-frontiers/01-concepts/02-self-improvement-and-agent-swarms.md) | 新增；draft |
| [10-Knowledge/16-research-frontiers/01-concepts/03-world-models-and-neuro-symbolic.md](../10-Knowledge/16-research-frontiers/01-concepts/03-world-models-and-neuro-symbolic.md) | 新增；draft |
| [10-Knowledge/16-research-frontiers/01-concepts/04-test-time-learning-and-oversight.md](../10-Knowledge/16-research-frontiers/01-concepts/04-test-time-learning-and-oversight.md) | 新增；draft |
| [10-Knowledge/16-research-frontiers/03-cases/01-research-and-science-agents.md](../10-Knowledge/16-research-frontiers/03-cases/01-research-and-science-agents.md) | 新增；draft |
| [10-Knowledge/16-research-frontiers/05-code/README.md](../10-Knowledge/16-research-frontiers/05-code/README.md) | 新增；verified |
| [10-Knowledge/16-research-frontiers/05-code/research_checks.py](../10-Knowledge/16-research-frontiers/05-code/research_checks.py) | 新增；实现、配置、样例或运行证据 |
| [10-Knowledge/16-research-frontiers/references.md](../10-Knowledge/16-research-frontiers/references.md) | 新增；draft |
| [20-Projects/domain-research-agent/README.md](../20-Projects/domain-research-agent/README.md) | 新增；verified |
| [20-Projects/domain-research-agent/evaluation/report/summary.json](../20-Projects/domain-research-agent/evaluation/report/summary.json) | 新增；实现、配置、样例或运行证据 |
| [20-Projects/domain-research-agent/evaluation/report/trials.jsonl](../20-Projects/domain-research-agent/evaluation/report/trials.jsonl) | 新增；实现、配置、样例或运行证据 |
| [20-Projects/domain-research-agent/evaluation/run_eval.py](../20-Projects/domain-research-agent/evaluation/run_eval.py) | 新增；实现、配置、样例或运行证据 |
| [20-Projects/domain-research-agent/fixtures/corpus.jsonl](../20-Projects/domain-research-agent/fixtures/corpus.jsonl) | 新增；实现、配置、样例或运行证据 |
| [20-Projects/domain-research-agent/pyproject.toml](../20-Projects/domain-research-agent/pyproject.toml) | 新增；实现、配置、样例或运行证据 |
| [20-Projects/domain-research-agent/run-report.md](../20-Projects/domain-research-agent/run-report.md) | 新增；导航、规范或记录 |
| [20-Projects/domain-research-agent/src/domain_research/__init__.py](../20-Projects/domain-research-agent/src/domain_research/__init__.py) | 新增；实现、配置、样例或运行证据 |
| [20-Projects/domain-research-agent/src/domain_research/cli.py](../20-Projects/domain-research-agent/src/domain_research/cli.py) | 新增；实现、配置、样例或运行证据 |
| [20-Projects/domain-research-agent/src/domain_research/service.py](../20-Projects/domain-research-agent/src/domain_research/service.py) | 新增；实现、配置、样例或运行证据 |
| [20-Projects/domain-research-agent/tests/test_integration.py](../20-Projects/domain-research-agent/tests/test_integration.py) | 新增；实现、配置、样例或运行证据 |
| [requirements-dev.lock](../requirements-dev.lock) | 新增；实现、配置、样例或运行证据 |
| [scripts/check_links.py](../scripts/check_links.py) | 新增；实现、配置、样例或运行证据 |
| [scripts/check_metadata.py](../scripts/check_metadata.py) | 新增；实现、配置、样例或运行证据 |
| [scripts/check_notebooks.py](../scripts/check_notebooks.py) | 新增；实现、配置、样例或运行证据 |
| [scripts/execute_notebook_ipython.py](../scripts/execute_notebook_ipython.py) | 新增；实现、配置、样例或运行证据 |
| [scripts/run_python.py](../scripts/run_python.py) | 新增；实现、配置、样例或运行证据 |
| [scripts/run_python_tests.py](../scripts/run_python_tests.py) | 新增；实现、配置、样例或运行证据 |
| [scripts/tests/test_checks.py](../scripts/tests/test_checks.py) | 新增；实现、配置、样例或运行证据 |

## 后续维护

本轮之外的真实模型评测、GPU 复现、人工审稿和历史图片来源核验，见[完成与后续计划](待补充计划.md)。月度链接任务只汇报检查结果，不自动修改仓库。

## 标准内核验证更新（2026-09-06）

提交 `5e5a40c09e00028c7887fd3bf3bd559d96fc972f` 的 [GitHub Actions 标准 Jupyter 执行](https://github.com/HarryYangthu/TheBestAIGuide/actions/runs/34013521515)已成功。原 Notebook 保存输出的本地 IPython 来源保留；这条更新补充标准内核证据，不代表交互控件或所有前端已验收。本轮新项目与后续结果见仓库 `00-Home/Round2-Completion.md`。
