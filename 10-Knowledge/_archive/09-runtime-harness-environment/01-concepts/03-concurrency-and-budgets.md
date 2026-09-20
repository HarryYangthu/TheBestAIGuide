# 并发与预算：让任务数量、速度和积压都有上界

> 状态：draft。本文同时讲解核心组件中的权限与资源控制。仓库已有本地授权、队列和并发实验；跨进程权限服务与原子 Token 预留是扩展设计，尚未在 Mini Agent 中实现。

两个子 Agent 同时比较 Pine SDK 的旧版和新版。每个都看到“还剩 1,000 token”，A 准备发出最多使用 800 token 的请求，B 准备发出最多使用 600 token 的请求。单独看两次判断都没超额，合起来却可能花掉 1,400。这不是模型不会节省，而是系统把同一笔额度答应给了两个人。

另一个子 Agent 发现资料缺失，想读相邻项目目录。即使剩余预算充足，也不意味着它可以读取。**权限决定哪些动作允许发生，资源限制决定允许的动作能进行多少、进行多久。** 两者都应该在真实操作前由程序检查。

## 权限检查要落到主体、工具与资源

假设 Alice 被允许读取 A 项目的 Pine 文档。模型提出 `read_file("B/private.md")` 时，宿主需要知道调用者仍是 Alice、动作是读文件、目标属于 B。只检查“有 read 权限”会放行错误对象；只检查工具在菜单里，也无法区分同一个工具能读哪份文档。

主体身份应来自已认证的会话，不能采用模型自己填写的 `user="admin"`。工具权限来自宿主保存的授权范围；资源归属则从实际记录或路径规则中查询。模型可以提出“读 B”，但不能同时决定“B 也属于我”。

下面是 [policy_lab.py](../../11-safety-security-governance/05-code/policy_lab.py)的实际授权函数。教学实现用记录代替文件，`tenant` 表示各组的数据边界：

```python
def _target(self, principal, proposal):
    if proposal.tool not in {'read_record', 'delete_record'}:
        raise Denied('unknown_tool')
    needed = 'read' if proposal.tool == 'read_record' else 'delete'
    if needed not in principal.scopes:
        raise Denied('missing_scope')
    record = self.records.get(proposal.resource_id)
    if record is None or record['tenant'] != principal.tenant:
        raise Denied('resource_not_accessible')
    return record
```

A 组有读取权限的主体读取 a1，可以继续；换成 B 组的 b1，则被拒绝。检查必须发生在原文返回模型之前。先让模型看见全部资料，再要求它不要引用越权内容，数据已经泄露。子 Agent 也应继承受限范围，不能因为角色叫“管理员”就多出删除权限。

审批处理的是某些动作是否得到具体确认。它不应成为每次读文件的固定步骤；用户已经授权的范围内应继续执行。需要确认时，把批准绑定到本次动作、参数与目标，而不是收一句含糊的“可以”后永久开放删除。身份、授权和审批的详细区别见[身份与权限](../../11-safety-security-governance/01-concepts/02-identity-and-permissions.md)。

Mini Agent 当前用限定资料目录、限定工具集合和固定报告出口控制操作范围，没有多用户登录或租户系统。TS Tool Runtime 只演示 scope 检查，资源级约束仍须 handler 落实。不能把几个教学例子拼成一句“系统已支持完整权限管理”。

## 五个限制管的是不同的事

现在假定两个子 Agent 都有权限调用模型。还要决定何时放行。下面五个限制经常写在同一配置文件里，但解决的问题不同：

| 限制 | 实际约束 | 不能替代什么 |
| --- | --- | --- |
| 并发最多 2 | 此刻最多两个请求执行 | 不保证每秒请求数少 |
| 每秒最多 5 次 | 单位时间的发出速度 | 不保证请求很快结束 |
| 最多排队 3 项 | 尚未执行的积压数量 | 不等于最多执行 3 项 |
| 总计最多 20 次调用 | 本次任务累计消耗 | 不限制这 20 次是否同时发出 |
| 30 秒截止 | 从受理到结束的期限 | 不等于每次请求可各用 30 秒 |

例如两个并发名额，每个请求只用 10 毫秒，理想情况下每秒可发出约 200 个请求，仍然会撞上每秒 5 次的限制。信号量只负责名额；速率限制还需要按时间发放通行资格，例如以固定速度补充令牌的令牌桶。

排队也必须有上界。用户每秒提交 10 项，系统每秒只能完成 5 项，队列每秒净增约 5 项。给它无限列表，只是把拒绝推迟成更长等待和内存耗尽。队列满时可以明确返回繁忙、让上游减速或延迟重试，这种让提交速度适应处理能力的做法叫背压。

## 从队列长度判断是不是可持续

在稳定系统中，可用 Little 定律估算平均积压：$L=\lambda W$。这里 $L$ 是系统内平均任务数，$\lambda$ 是平均到达率，$W$ 是从进入到离开的平均时间。每秒进入 4 项，平均停留 3 秒，平均在系统中的任务约为 12 项，包括排队和执行。

这是教学算例，不是本库吞吐实测。前提是系统能够稳定处理流量；若积压一直增长，就不存在这里假设的稳定平均值。更多 Worker 也不一定有用：下游限流不变时，只会增加同时等待或失败的请求。公式来源见[本域参考资料](../references.md)。

## 排队时间也会花掉用户的期限

用户给这次比较 30 秒，任务先排队 28 秒，执行阶段就不能再自作主张获得完整 30 秒。期限应从任务受理时开始计算，每次进入队列、重试和调用前重新计算剩余时间。

本库 [Supervisor](../../08-planning-workflow-multi-agent/05-code/multi-agent-runtime-python/src/multi_agent/supervisor.py)用下面的结构让每个子任务的超时包含等待并发名额；此处是保留关键顺序的简化代码：

```python
async def perform(task):
    async with semaphore:
        return await worker(task)

result = await asyncio.wait_for(perform(task), timeout=task.timeout_s)
```

关键在于 `wait_for` 包住了获取信号量的过程。若在外面先等待信号量，再开始计时，排队多久都不会触发这个超时。当前实现是每任务期限；若要让全部子任务共同遵守父任务的全局截止时间，还需传播统一 deadline，不能给每次新委派重新分配整段时间。

## 并发下怎样守住总 Token 预算

回到开头的 1,000 token。执行前要先预留一笔额度，结束后按实际使用结算。“检查余额”和“扣下预留额”必须合成一个不可被其他 Worker 插入的操作。一个具体过程如下，数字只用于讲机制：

1. 初始已使用 0、已预留 0、可用 1,000。A 请求上界 800，成功预留后，可用降到 200。
2. B 需要 600；它检查到只剩 200，所以等待或被拒绝，不能先发请求再想办法。
3. A 返回实际用量 300。系统撤掉 A 的 800 预留，记入 300 实际消耗，可用变成 700。
4. B 现在预留 600，可用剩 100；若 B 最终用 450，累计已用 750，可用回到 250。

预留额要包括此次调用的输入和最大输出。输入已占 400、最大输出设成 800，总上界应按 1,200 考虑；不同服务的计费细项要按实际口径处理。费用预算与 token 预算也不能直接混用，因为模型或输入输出的价格可能不同。

下面仅展示单进程协程的原子预留思路，**不是本库已接入的预算类**。`spent`、`reserved` 属于同一账户，所有相关写入都须遵守同一把锁：

```python
async def reserve(account, request_id, upper_bound):
    if upper_bound <= 0:
        raise ValueError("positive reservation required")
    async with account.lock:
        if request_id in account.reserved:
            raise ValueError("duplicate request id")
        available = account.limit - account.spent - sum(account.reserved.values())
        if upper_bound > available:
            raise ValueError("budget_exhausted")
        account.reserved[request_id] = upper_bound
```

跨进程 Worker 不能靠各自的 `asyncio.Lock` 协调，要使用共同存储上的事务或其他原子更新。结算也须去重，否则同一回执处理两次会重复记账。请求超时或服务缺少 `usage` 时，实际消耗是未知，不是 0；保守做法是暂时保留预留额度并等待核对，不能立刻退回后再次消费。

如果服务无法提供可靠的消耗上界，或者本地输入估算有误，就不能承诺绝不超额。此时应明确是软预算，通过控制并发、输出上限和留出余量减少风险。Mini Agent 当前限制主循环次数并记录服务返回的 usage，没有实现这里的原子预留；部分调用缺少 usage 时，已有数字也不代表完整总用量。

## 取消不是撤销已发生的效果

用户取消报告任务后，应阻止尚未执行的步骤，并向正在执行的操作传递取消。但已保存的报告不会自动消失，远端已提交的实验也不会因此回滚。取消结果应区分“尚未开始”“已停止”和“外部结果待确认”。

Python 协程通常在可中断点收到 `CancelledError`。Worker 可以在 `finally` 释放资源，然后继续传播取消，不能随意吞掉异常并伪装成功。`wait_for` 还可能等待取消清理，因此实际返回时间可能超过参数中的秒数；阻塞计算和不合作的远端服务需要另行处理。语义见 [Python 官方任务文档](https://docs.python.org/3/library/asyncio-task.html)。

## 跑一次队列实验，再检查权限反例

从仓库根目录执行：

```bash
python scripts/run_python.py -m learning_workbench.cli queue --output .runs/queue-lesson
python -m unittest discover -s 10-Knowledge/_archive/11-safety-security-governance/05-code -p test_policy.py -v
```

第一条生成 `.runs/queue-lesson/queue.json`，包含 `unbounded` 和 `bounded` 两组。两组都提交 30 项、使用两个 Worker，区别是队列无限与最多积压 3 项。查看 `completed`、`rejected`、`max_depth` 和等待时间：每组应满足 `completed + len(rejected) = 30`；有界组的 `max_depth` 不超过 3。具体接收数量和耗时受调度影响，不应背一个固定毫秒数。

任务执行的是人工设置的异步等待，并包含预设重试条件；它展示真实本地排队机制，不测模型吞吐。第二条运行内存权限用例，预期全部通过：合法读取被允许，越权对象和未批准删除被拒绝。它没有实现认证服务器，也不证明模型能抵御所有诱导。

**练习 1：** A 的 800 预留还没结算就超时，能否马上把 800 全退给 B？答案：不能假设全未使用。外部请求可能已完成或仍在执行，应保留未知消耗记录，通过回执或服务用量核对后处理。

**练习 2：** 并发从 2 提高到 4 后，队列变短而限流错误变多，算成功优化吗？答案：不能只看队列长度。要比较完整任务完成率、端到端时间和含重试的消耗；若下游容量没变，新增并发可能只是把等待转成失败。

返回 [Agent 核心组件总览](../../03-agent-core/01-concepts/04-core-components.md)，把权限和资源限制放回任务执行过程理解。
