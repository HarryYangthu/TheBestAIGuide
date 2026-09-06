# Safety、Security 与 Governance

> 状态：draft；来源核验：2026-09-06；本地策略与正反例实验为 verified 范围。

本域用一个有 A/B 两个租户的记录工具解释信任边界：用户想读 A 组资料，文档却诱导 Agent 读 B 组或删除文件，程序怎样保证动作不越权，同时正常请求仍能完成。

| 学习问题 | 正文 | 实践 |
|---|---|---|
| 文档为何不能成为新的命令来源 | [威胁模型与提示注入](01-concepts/01-threat-model-and-injection.md) | 合法文本与越权动作对照 |
| 身份、权限与审批各控制什么 | [身份与权限](01-concepts/02-identity-and-permissions.md) | 主体、租户、scope、具体动作审批 |
| 密钥不进入上下文，如何还能审计 | [数据、Secrets 与审计](01-concepts/03-data-secrets-and-audit.md) | 允许字段投影、最小审计事件 |
| 工具更新和出事后怎样处理 | [供应链与响应](01-concepts/04-supply-chain-and-response.md) | 版本记录、负例回归、资源状态验收 |

[运行 Notebook](04-labs/01-policy-and-injection.ipynb) · [完整代码](05-code/README.md) · [来源索引](references.md)

本实验没有调用模型，也不声称解决全部提示注入；它验证的是模型提出越权动作以后，确定性执行边界仍能拒绝。模型可靠性、校准和可解释性继续参考 [AI 基础](../01-ai-foundations/README.md)。
