# 生产工程：一手来源与采用范围

> 状态：draft · 更新：2026-09-06

核验日期：2026-09-06；全部为官方文档或由实践者撰写的官方书籍章节。以下内容支持工程方法，不是本库线上服务的运行证据。

| 来源 | 应读位置 | 用途 | 注意边界 |
|---|---|---|---|
| [Google SRE：Implementing SLOs](https://sre.google/workbook/implementing-slos/) | SLI、SLO、错误预算定义 | 面向用户定义可靠性 | 目标数字要由本业务确定 |
| [Error Budget Policy](https://sre.google/workbook/error-budget-policy/) | 预算与发布决策 | 预先约定预算耗尽后的行为 | 模板不能代替组织决策 |
| [Handling Overload](https://sre.google/sre-book/handling-overload/) | 过载、拒绝与重试 | 容量和背压设计 | Agent 工具与模型配额另需计量 |
| [SLO Engineering Case Studies](https://sre.google/workbook/slo-engineering-case-studies/) | Evernote 与 Home Depot | 公开系统方法分析 | 不把书中历史规模当作当前规模 |
| [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) | 更新与回滚 | 区分部署修订与业务恢复 | 回滚容器不撤销外部副作用 |

Little 定律、成本算例和重复写入脚本是通用数学/本地教学演示；没有进行真实负载测试。运行结果与限制见[代码说明](05-code/README.md)，案例分别见[公开方法分析](03-cases/production-systems/README.md)和[本地故障复盘](03-cases/failure-postmortems/README.md)。
