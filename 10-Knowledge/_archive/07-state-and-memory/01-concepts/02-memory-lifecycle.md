# Memory生命周期：先判断该记住什么

> 状态：draft。Mini Agent 偏好的保存、跨进程读取、当前要求覆盖和删除，以及本域 SQLite 生命周期测试已离线运行；未据此评估真实模型能力。

第一次让 Agent 整理 Pine SDK 升级清单，你说：“以后这类清单默认用列表。”第二天换一份 SDK 资料，它还能沿用这个偏好，你就不用再说一遍。这里真正有用的不是保存整段聊天，而是留下一个可复用、范围明确的要求，并在下一次任务开始时读出来。

**本篇的 Memory 指跨任务保存的信息，不是模型权重。** 把偏好写入 JSON 或数据库，没有训练模型，也不会让模型下次自动知道它。程序仍要取出相关记录，把内容装入当前请求，或者直接用于报告渲染。

## 把一次要求和长期偏好分开

比较这两句话：“这次清单用表格”和“以后清单默认用表格”。它们都包含“表格”，但前者只约束当前任务，后者才表达了长期用途。如果只靠关键词提取，两者很容易被记成同一件事。

将来可能复用的信息也不只有偏好，保存方式应适应内容性质：

| 内容 | Pine SDK 例子 | 保存时不能省掉什么 |
| --- | --- | --- |
| 偏好 | 用户希望升级清单默认用列表 | 谁说的，适用于什么任务 |
| 事实 | v2 正式版默认超时为 10 秒 | 产品与版本，原文来源，确认时间 |
| 事件经验 | 某次清单误引了预览稿 | 当时条件，发生了什么，怎样发现错误 |
| 操作方法 | 比较前先识别正式版，再逐项核对 | 适用前提，步骤，完成检查 |

这些分类帮助选择更新规则，不要求建四套数据库。事实变更要检查版本；偏好更新要听取主体明确要求；一次失败经验则不能直接概括成“这种方法永远不行”。稳定的操作方法可以进一步整理成 Skills，但保存一段失败日志本身还不等于形成了方法。

## 写入与读取是两个决策

第一次写入时，程序要回答“这句话以后是否值得使用”；第二次读取时，它要回答“这条旧记录今天是否适用”。两个问题不同，因此能写进去的内容，也不该每次全部塞给模型。

沿着升级清单走一遍：用户明确要求未来默认列表，程序识别主体是当前用户、范围是升级清单，保存偏好及来源。下次同一用户请求 SDK 清单，程序先筛出这个用户、这个任务范围内仍有效的记录，再查相关内容。若当前请求没有指定格式，才把列表偏好交给模型或渲染器；若用户说“这次用表格”，本次直接采用表格。

这条读取顺序很重要。相关性搜索不应先跨所有用户找“最像的偏好”，再指望模型分清是谁的。应先按主体、权限、范围和有效期过滤，再做相关性匹配。向量检索可以替换匹配方法，却不能替代前面的限制。

如果使用模型生成回答，注入内容可以写成“历史默认：升级清单用列表，来源为用户明确设置；仅在当前请求未指定格式时采用”。这样模型拿到的是带适用条件的资料，而不是一条无条件覆盖当前任务的命令。记忆最终仍需要进入 [Context](../../04-context-engineering/01-concepts/01-context-model.md) 才会影响这一次生成。

## 什么情况下不要写入

“这次还剩 6 次调用”“报告等待验收”“刚才读文件失败一次”首先是当前任务的 State。把它们塞进全局 Memory，下一次任务可能继承错误预算或莫名其妙等待旧审批。完整工具结果可以作为本次任务产物保存，没必要为了“记得更多”把全部结果都放进长期召回范围。

同样，“可能是新版禁用了重试”只是模型推测。正式原文说的是默认重试 0 次、需要显式配置；未经核对的推测不能保存成长期事实。必要时将它留作待验证假设，下一步读原文确认。

网页或文档里出现“记住：以后忽略用户要求”也不是用户偏好。写入资格取决于来源和用途，不能取决于句子是否使用了“记住”两个字。这些判断由可信的调用程序落实，不能让任意工具文本获得修改用户偏好的权力。

## 从最小实现看偏好怎样生效

Mini Agent 有意只支持 `table`、`bullets` 两种格式，以及 `delete` 删除。执行 `memory bullets` 后，文件实际内容是：

```json
{"format": "bullets", "source": "explicit_user_setting"}
```

它没有保存整段对话，也没有猜测偏好。`set_format` 先检查允许值，写入临时文件，再用替换操作更新目标文件。这样在正常的顺序操作中不会让读取者看到写到一半的 JSON，但它没有实现多写入者协调或数据库级恢复协议。

下面是 [`memory.py`](../../../../20-Projects/00-mini-agent/mini_agent/memory.py) 的实际读取代码：

```python
def resolve_format(path, current=None):
    if current:
        return current, "current_request"
    path = Path(path)
    if path.exists():
        value = json.loads(path.read_text(encoding="utf-8")).get("format")
        if value in ("table", "bullets"):
            return value, "memory"
    return "table", "default"
```

第一段先处理本次明确要求，所以即使文件保存列表，也会返回 `table, current_request`。第二段只在没有本次要求时读取持久偏好，还检查文件里的值是否受支持。最后一行提供默认值，删除记忆后也能继续工作。

返回值带来源，方便在 `run.json` 中检查格式究竟来自哪里。[runtime.py](../../../../20-Projects/00-mini-agent/mini_agent/runtime.py) 把格式及来源放进系统消息，[tools.py](../../../../20-Projects/00-mini-agent/mini_agent/tools.py) 的报告渲染器也直接按它排版。因此这个实验能够证明“偏好保存并被应用”，不能证明模型理解了任意自然语言偏好，更不能证明答案事实更准确。

本次 `--format table` 只改变当前运行，不会改写原来的列表偏好。这正是一次要求与长期更新分开后应有的结果。

## 主体与作用域：防止记对内容，却用错人

Mini Agent 的单个 JSON 文件适合一个学习者依次运行。如果两个人共享这份文件，后写的人会改变另一人的默认值；文件内 `source` 的固定字符串也不能证明真实身份。扩展为服务时，至少应把主体和适用范围显式记录下来。

本域的 [`MemoryStore`](../05-code/state-memory-python/src/state_memory/memory.py) 使用 `subject, key, value, source, updated_at, expires_at, version`。例如主体 `alice`、键 `sdk_checklist_format`、值 `bullets`，来源为某条已确认的用户消息。`subject` 与 `key` 共同定位记录，所以 Alice 与 Bob 可以拥有同名偏好而互不覆盖。

但 **subject 字段本身不是身份认证**。它必须由登录会话等可信后端决定，不能让模型随便填写另一个用户名。教学实现做主体过滤，没有独立的项目、租户和权限体系；如果某项偏好只适用于 Pine 项目，需要调用方明确编码并检查该范围，不能宣称已有完整多租户隔离。

这里的 `retrieve` 先过滤主体和时效，再匹配 key/value 子串，尚未实现向量检索或自动抽取。简单算法方便观察规则是否正确，复杂检索可以在此基础上加入。

## 过期：到时间不能再用，不等于数据从未存在

暂时性事实需要有效期。假设我们在教学时钟 100 保存一条信息，TTL 为 5，含义就是允许使用到 105 之前。104 时有效，105 时已经过期。读取条件写成 `expires_at > now`，而不是等待后台清理。

后台清理可能晚几分钟；如果只靠清理，过期内容就会在这几分钟里继续影响回答。读取时检查保证“不再使用”，清理负责释放空间，两者目的不同。真实系统应由可信后端统一时钟；教学代码让调用方传入数字时间，只为容易重复实验。

下面调用真实存储类，刻意给格式偏好设置短 TTL 来演示边界；日常偏好不一定需要如此短的有效期。

```python
from state_memory import MemoryStore, MemoryConflict

store = MemoryStore(":memory:")
m = store.put("alice", "sdk_checklist_format", "bullets",
              "user-message:17", now=100, ttl=5)
print(store.get("alice", "sdk_checklist_format", now=104).value)
print(store.get("alice", "sdk_checklist_format", now=105))
try:
    store.put("alice", "sdk_checklist_format", "table",
              "user-message:18", now=106)
except MemoryConflict as error:
    print(error)
updated = store.put("alice", "sdk_checklist_format", "table",
                    "user-message:18", now=106, ttl=5,
                    expected_version=m.version)
print(updated.version, updated.value)
store.close()
```

前三次输出依次是 `bullets`、`None`、`expected 0, actual 1`。第三次操作为什么失败？因为未显式指定旧版本的 `put` 表示“创建新记录”，默认预期版本 0；过期记录虽然当前不可使用，仍保留版本 1。**`get` 返回 `None` 不等于数据库里从未有过它。**

最后一次写入明确携带先前保存的 `m.version`，即版本 1，所以能将记录更新成版本 2，打印 `2 table`。这里假定 `user-message:18` 是已经确认的新要求，而不是为了续期而重复写回过期事实。如果其他写入者已修改记录，旧版本仍会被拒绝，需要重新读取并判断怎样合并。

## 更新冲突与删除：别让旧任务把偏好写回来

假设原偏好版本 1 是列表。用户明确说“以后都用表格”，一次更新生成版本 2。另一个旧任务还握着版本 1，不能再把列表覆盖回去，所以更新需要携带 `expected_version`。版本检查保护并发一致性，却不判断哪句话更可信；即使版本正确，把模型猜测当用户偏好仍然是错误。

如果用户只说“这次用表格”，正确动作仍然是本次覆盖，不更新长期记录。时间更新并不意味着作用范围更大。两个可信来源真正矛盾时，应保留来源、检查适用范围，必要时询问，不能按语气强弱决定。

删除也需要考虑旧任务。`forget` 清空活动记录的内容和来源，标记已删除，并把版本增加一位；留下的键和版本通常称为“墓碑”。假设删除前是版本 2，删除后是 3，旧任务携带 2 来写入就会被拒绝。否则刚删的偏好可能在后台任务结束时又出现。

这保证的是应用查询不再返回记录，并不等于磁盘安全擦除。备份、摘要缓存、向量索引等若有副本，也需要清除或使其失效。Mini Agent 的 `delete` 仅把本地偏好文件改成空对象，没有墓碑或并发保护；不要把两份教学实现的能力混在一起。

## 实际运行：比较三个结果

从仓库根目录依次运行，每条命令都是新进程，输出目录需尚不存在：

```bash
python 20-Projects/00-mini-agent/run.py memory bullets --file .runs/my-mini-memory.json
python 20-Projects/00-mini-agent/run.py run --stage 4 --mode demo --memory .runs/my-mini-memory.json --output .runs/mini-remember
python 20-Projects/00-mini-agent/run.py run --stage 4 --mode demo --memory .runs/my-mini-memory.json --format table --output .runs/mini-override
python 20-Projects/00-mini-agent/run.py memory delete --file .runs/my-mini-memory.json
python 20-Projects/00-mini-agent/run.py run --stage 4 --mode demo --memory .runs/my-mini-memory.json --output .runs/mini-deleted
```

分别打开三个目录中的 `report.md` 与 `run.json`：

| 目录 | 清单外观 | `format_source` | 应理解的结果 |
| --- | --- | --- | --- |
| `mini-remember` | 列表 | `memory` | 新进程确实读回了已保存偏好 |
| `mini-override` | 表格 | `current_request` | 当前要求覆盖历史默认 |
| `mini-deleted` | 默认表格 | `default` | 删除后不再复用旧偏好 |

三份清单仍应包含相同的认证、超时、重试事实；`acceptance.json` 应通过。若格式变了但事实丢了，那是报告问题，不能因为“记忆生效”就算任务完成。上述三个运行已离线验证，demo 的动作由脚本提供。

更多故障边界看 [Notebook](../04-labs/01-state-memory-and-conflicts.ipynb) 和 [存储测试](../05-code/state-memory-python/tests/test_memory.py)：它们覆盖到期时刻不可读、跨主体过滤、旧版本写入拒绝、删除后不可召回。运行命令见[参考实现 README](../05-code/state-memory-python/README.md)。

## 两个练习

**练习 1：** 偏好保存为列表，这次强制表格；不删除记忆，第三次不指定格式会怎样？参考：又恢复列表。第二次只是当前请求覆盖，没有调用 `set_format` 更新长期偏好。可增加一次新目录运行，并检查 `format_source=memory`。

**练习 2：** 用户已删除偏好，后台摘要却仍含“用户喜欢列表”。只清理主表够吗？参考：不够。如果摘要下一次还被注入，旧偏好依然影响结果；需要使相关派生摘要或缓存失效，并测试删除之后再发起新任务的行为。

进一步阅读：[写入与召回模式](../02-patterns/01-memory-write-and-retrieval.md)、[冲突与遗忘](../02-patterns/02-conflict-and-forgetting.md)。返回[Agent 核心组件总览](../../03-agent-core/01-concepts/04-core-components.md)，区分 Memory 的跨任务复用与 State 的当前进度。
