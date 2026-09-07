# 应用代码与验证范围

> 状态：verified · 更新：2026-09-06

| 实现 | 运行方式（仓库根目录） | 已验证 |
|---|---|---|
| [Python 领域算例](application_cases.py) | `python 10-Knowledge/13-application-engineering/05-code/application_cases.py` | 权限过滤、能力选择、价格修复、运维建议、合成搜索 |
| [Python 测试](test_application_cases.py) | `python -m unittest discover -s 10-Knowledge/13-application-engineering/05-code -p 'test_*.py'` | 5 个测试通过，含正常与反例 |
| [浏览器 TypeScript 工程](browser-agent-typescript/README.md) | 在工程目录 `npm ci`，安装浏览器后 `npm test` | 3 个真实 Chromium E2E 通过 |

Python 3.12，标准库，无需 API key。浏览器环境与详细输出见工程 README 和 artifacts。领域算例由固定规则执行，没有接入 LLM；它们验证局部工程语义，不能证明开放任务自主性。跨域[工作台](../../../20-Projects/learning-workbench/README.md)已有本地 SSE/SQLite Run 服务与真实模型适配器；PostgreSQL 行安全 SQL、完整多供应商网关仍是设计说明。

返回[知识文章与案例](../README.md)。
