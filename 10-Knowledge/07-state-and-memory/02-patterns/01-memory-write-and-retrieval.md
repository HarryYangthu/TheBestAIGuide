# 写入与召回：身份、证据、时效先于相似度

> 状态：draft | 来源核验：2026-09-06

检索问题是“我后续希望用什么语言看代码”。数据库里有A用户的Python偏好、B用户的TypeScript偏好。二者与查询同样相关，向量模型无法替你决定哪个主体有权读取哪条记录。必须先限制合法候选，再计算相关性。

设全部记忆集合为 $M$，当前身份为 $u$，时间为 $t$，过滤后候选为

$$M' = \{m\in M\mid m.subject=u,\;m\text{未撤回},\;m.expires\_at>t\text{或无到期时间}\}.$$

检索与排序只在 $M'$ 上发生。这些是硬约束，不应放到加权分数里。若“错误主体”只是减0.2分，一条足够相似的他人记录仍可能排到前面。

## 写入时保存什么证据

一条明确的用户偏好可以保留原消息指针与时间；从文件得到的事实保留文件ID、版本和片段；从实验归纳的经验保留任务条件和实验结果。多次重复描述不应让一条未经证实的猜测变成高可信事实。确认同义条目能合并时，仍要保留更新来源；证据冲突则进入显式冲突处理。

本实现以`(subject,key)`作为唯一键，适合“language”“context_budget”这类可定位事实。写同一key的新值必须携带当前版本，因此不会因为最后到达数据库就静默胜出。复杂文本记忆需要实体规范化和去重策略，本例没有用一个简易字符串函数冒充语义合并。

```python
from state_memory import MemoryStore
store = MemoryStore(":memory:")
old = store.put("alice", "language", "Python", "user:1", 100)
new = store.put("alice", "language", "TypeScript", "user:2", 101,
                expected_version=old.version)
print(store.retrieve("alice", "language", now=102)[0].value)
store.close()
```

## 排序需要任务依据

过滤后可使用相关性、来源质量和时间新鲜度排序。一个常见工程形式为 $score=\alpha r+\beta q+\gamma f$，其中$r$表示查询相关性，$q$表示来源质量，$f$表示时间适用性；各项须先统一范围，权重通过验证集选择。这个式子不是记忆检索的通用最优公式。法律定义不会因为较旧就自动没用，用户当前状态却可能很快过时；应按事实类型设置时效规则。

本库[`retrieve`](../05-code/state-memory-python/src/state_memory/memory.py)只实现主体与过期硬过滤、key/value子串匹配及更新时间排序。选择简单匹配是为了把隔离规则看清楚；同义词、语义检索和重排属于后续扩展接口，不能把本例当作向量数据库性能方案。

## 召回后还要控制注入

返回一百条合法记录也可能挤满Context。应该根据当前任务挑选少量记录，保留来源并标明这是历史偏好。当前用户明确要求Java时，不应让“通常优先Python”的旧偏好覆盖当前要求。Memory是辅助上下文，当前任务约束仍由权威State表达。

实现与测试见[工程README](../05-code/state-memory-python/README.md)。生命周期依据见[概念篇](../01-concepts/02-memory-lifecycle.md)，外部存储研究参见[MemGPT](https://arxiv.org/abs/2310.08560)。
