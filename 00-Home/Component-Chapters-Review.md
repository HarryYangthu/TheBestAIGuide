# Agent 组件章节交付与读者走读

日期：2026-09-20。范围为 [10-Knowledge 的 15 个组件](../10-Knowledge/02_Harness/README.md)，原领域内容保留在归档。本轮使用“Agent 技术章节写作”Skill，补齐其余 14 章，并重新阅读与修订已有执行循环章。

## 阅读与运行入口

每章 README 给出贯穿任务、总览图、阅读顺序、环境、完整命令与输出。正文沿图展开实现；独立片段、函数定义、源码节选与数据格式分别标明用途。输入文件已随章保存，实验结果来自实际文件与进程。

| 组件 | 已执行的核心读者路径 | 可检查的结果 |
|---|---|---|
| [01 任务与协议](../10-Knowledge/02_Harness/01-task-contracts/README.md) | 最小请求 → Schema → 验收 → 12 个场景 | 契约结果、错误分类与报告 |
| [02 模型接入](../10-Knowledge/02_Harness/02-model-adapters/README.md) | 配置校验、5 类协议场景、SDK 传输测试 | 规范化响应、参数字典、用量与错误文件 |
| [03 执行循环](../10-Knowledge/02_Harness/03-agent-loop/README.md) | 真实输入检查、固定响应实验、停止与错误测试 | 运行轨迹、文件产物和停止原因 |
| [04 编排调度](../10-Knowledge/02_Harness/04-orchestration-and-scheduling/README.md) | 顺序/并行、缺价、价格更新、增运费、取消 | DAG 状态、执行次数与局部重规划 |
| [05 通信交接](../10-Knowledge/02_Harness/05-communication-and-handoff/README.md) | 委派、失败重试、重复与迟到、负责人交接 | 消息关联、接收决定和待确认草稿 |
| [06 上下文](../10-Knowledge/02_Harness/06-context-management/README.md) | 最小上下文、默认预算、1301/1302 边界 | 消息文件、实际 token 量与证据缺口 |
| [07 状态产物](../10-Knowledge/02_Harness/07-state-and-artifacts/README.md) | 状态更新、版本失效、并发 CAS、重读合并 | 状态版本、内容哈希与有效证据 |
| [08 工具环境](../10-Knowledge/02_Harness/08-tools-and-environment/README.md) | 单工具、完整任务、stdio MCP、8 个场景 | 标准工具结果、补货文件与验收 |
| [09 恢复](../10-Knowledge/02_Harness/09-persistence-and-recovery/README.md) | 12 个中断场景与幂等键对照 | 检查点、独立接收库、次数与真实效果 |
| [10 评估验收](../10-Knowledge/02_Harness/10-evaluation-and-acceptance/README.md) | 单题独立验收、36 次配对运行 | 基线 9/18、候选 15/18，发布仍 hold |
| [11 Trace](../10-Knowledge/02_Harness/11-trace-and-observability/README.md) | 最小 span、并行任务、去延迟对照 | 11 条 span、时间图和一成功一失败 |
| [12 权限资源](../10-Knowledge/02_Harness/12-permissions-and-resources/README.md) | 数据范围、预留结算、并发取消、批准入口 | 拒绝记录、预算账本与批准后的本地文件 |
| [13 Memory](../10-Knowledge/02_Harness/13-memory/README.md) | 10 个独立进程、冲突更新、到期与遗忘 | 持久库、检索上下文和生命周期对照 |
| [14 Skills](../10-Knowledge/02_Harness/14-skills/README.md) | 直接脚本、渐进加载、4 个版本/路由场景 | 双侧证据报告、加载轨迹和包指纹 |
| [15 自进化](../10-Knowledge/02_Harness/15-self-improvement/README.md) | 失败生成候选、门禁、采用、回滚、回归拒绝 | 候选差异、开发/留出评测、实际行为恢复 |

## 走读后完成的修订

| 发现的问题 | 调整与复核 |
|---|---|
| 错误类型的摘要字段可能绕过回退 | 先校验摘要形状与字段类型，失败保留原历史；新增回归 |
| 工具章图把独立容器入口画进注册分发 | 图中区分本地注册工具与独立容器命令 |
| 子任务主动取消后状态仍为 running | 单独回收子取消，保存明确终态 |
| 交接期间的版本与新增任务不够严格 | 核对实际输入版本，未决交接阻止新增委派，健壮记录畸形消息 |
| 批准只绑定请求，未绑定发布值 | 展示并绑定具体投影内容，执行时重新核对 |
| 技能报告标题错误或产物缺字段未被稳定拒绝 | 验收标题及文件形状，失败仍保存验收与运行记录 |
| 自进化缺输入时未留下失败结果 | 读取输入纳入错误记录，缺失哈希拒绝进入可比门禁 |
| 既有执行循环的异常图与实际分支不一致 | 修正空回复、协议错误和终止路径，更新后续章节导航 |
| 远端 Python 工作流缺 RAG 绘图依赖 | 统一安装组件及 RAG 依赖，源码检查覆盖所有随章快照 |

## 验证范围

机器可读汇总见 [component-chapters.json](verification/component-chapters.json)。统一检查包括 Python 行为测试、本地链接、元数据、21 本 Notebook 格式、源码快照和 85 幅 Mermaid 图语法。图表另外核对实际数据及可读性。

本地没有 API 配置，因此没有执行真实模型请求；第 08 章的可选 Docker 隔离实验也未运行。接口模拟、本地工具、并发、子进程故障、持久化和报告生成均按各章记录实际执行。没有将缺失模型费用填成零。API Notebook 保留需要密钥的执行边界，其余 Notebook 的标准内核执行由 GitHub Actions 检查。
