# 代码仓：用固定快照对照实现

下面的 SHA 均在 2026-09-06 通过 GitHub 读取提交元数据，并读取该提交的 README；不是根据分支名猜测的版本。这里只把它们作为外部实现与评测入口，没有声称跑过这些工程。详细任务与指标见 [数据集索引](../datasets-and-benchmarks/README.md)。

| 仓库与固定阅读入口 | 固定提交（提交日期） | 从哪里开始读 | 本轮范围和限制 |
| --- | --- | --- | --- |
| [openai/human-eval](https://github.com/openai/human-eval/tree/6d43fb980f9fee3c892a914eda09951f772ad10d) | `6d43fb980f9fee3c892a914eda09951f772ad10d`（2025-01-17） | README 的 JSONL 样本格式 → `human_eval/execution.py` 的测试程序构造、子进程和超时 | 已读 README 与 execution.py。README 对“执行调用仍被注释”的描述落后于此快照源码；实际 `exec` 已启用，不能把 README 当作安全开关的证据 |
| [beir-cellar/beir](https://github.com/beir-cellar/beir/tree/ef83d29307061c65d04b035b4f4e7c18bd8374af) | `ef83d29307061c65d04b035b4f4e7c18bd8374af`（2025-10-16） | README 的 `GenericDataLoader` → 检索结果字典 → `EvaluateRetrieval` 指标示例 | 已读 README、可用数据集表与许可说明；未下载模型、索引语料或对照数值结果 |
| [web-arena-x/webarena](https://github.com/web-arena-x/webarena/tree/dce04686a56253aefba7b18a4fa0937cf1dc987b) | `dce04686a56253aefba7b18a4fa0937cf1dc987b`（2025-11-26） | README 的 `reset` / `step` 示例 → 自托管环境步骤 → 任务配置与轨迹保存 | 已读 README；它是论文的 canonical 实现入口。没有把展示网页当实验环境，也没有运行浏览器任务 |
| [SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench/tree/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e) | `02e7a74ffd0b707aab73d203fe87bdc7c76afc8e`（2026-09-02） | README 的数据集选择 → gold patch 安装自检 → 预测补丁评估 → 输出与缓存规则 | 已读 README；未构建 Docker 镜像、运行 gold patch 或提交排行榜。不要直接照抄此快照命令到不同版本的安装环境 |
| [open-telemetry/semantic-conventions-genai](https://github.com/open-telemetry/semantic-conventions-genai/tree/94f432d7126f5884d30a2cdde6f4e89908ebb6fd) | `94f432d7126f5884d30a2cdde6f4e89908ebb6fd`（2026-09-03） | README → `docs/gen-ai/README.md` → `docs/gen-ai/gen-ai-spans.md`；具体字段再定位 `model/` 定义 | 已读这三份文档，GenAI 总览与 model span 页为 Development；Schema URL 未填写。本轮没有运行 `reference/` 中的实现 |

读代码时，每条结论都尽量落到“输入在哪里进入、哪个函数改变状态、结果如何保存、失败如何处理”。仅列目录或类名，不足以说明实现机制。引用源码时用固定提交的 `blob/<SHA>/...` 链接；需要研究新版本时另记新快照，不悄悄替换旧结论。

与知识库结构有关的既有走读保留在 [AgentGuide 案例](../../00-Home/reference-cases/AgentGuide/README.md)。技术仓库的深入分析进入对应知识领域 `03-cases/`，其实际运行记录进入 `04-labs/`。
