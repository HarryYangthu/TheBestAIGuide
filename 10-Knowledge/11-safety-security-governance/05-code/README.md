# 本地策略 Runtime

> 状态：verified（5 项 unittest 及 Notebook）；执行日期：2026-09-06。

Python 3.11+，无第三方运行依赖。进入本目录运行：

```bash
python -m unittest -v test_policy.py
```

[policy_lab.py](policy_lab.py)导出 `Principal`、`Proposal`、`PolicyRuntime`、`Denied`、`fixture`、`injection_cases`。`execute(principal, run_id, proposal)`先检查工具、scope 和租户；删除还检查绑定到用户、Run 与资源的短期审批令牌。`approve`仅供可信服务端在真实用户确认后调用，不是模型工具。

[test_policy.py](test_policy.py)覆盖：合法读取、引用攻击文本的合法请求、跨租户/越权工具/无审批删除/伪路径拒绝；批准后合法删除；令牌换用户、换 Run、换资源、过期、重复使用拒绝；secret 不进入响应和审计。

这是内存内的权限教学实现，没有认证服务器、持久化审计或多进程事务。生产系统必须从可信会话构造 Principal，审批消费与副作用应具有可靠事务或幂等语义。模型收到的文本不由此程序分类，实验不测模型是否听从恶意内容。

[Notebook](../04-labs/01-policy-and-injection.ipynb) · [身份与权限正文](../01-concepts/02-identity-and-permissions.md) · [本域导航](../README.md)
