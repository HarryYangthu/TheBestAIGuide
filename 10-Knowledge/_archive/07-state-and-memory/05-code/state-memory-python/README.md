# State / Memory Python参考实现

> 状态：verified | 2026-09-06，Python 3.12，4项组合测试通过

Python 3.11+，运行只使用标准库SQLite，无服务凭据或远程数据库。从本目录运行：

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

PowerShell先执行`$env:PYTHONPATH="src"`；或使用`python -m pip install -e .`安装包。

| 入口 | 输入与输出 |
| --- | --- |
| `CheckpointStore(path).save(run_id,state,expected_version=0)` | 接受JSON对象；成功返回新整数版本，冲突抛VersionConflict |
| `load(run_id)` | 返回`(version,state)`；缺失为`(0,{})` |
| `MemoryStore(path).put(subject,key,value,source,now,ttl=None,expected_version=None)` | 返回Memory对象；创建默认预期版本0，首次成功返回version=1，更新须显式旧版本 |
| `get(subject,key,now)` | 返回有效Memory或None |
| `retrieve(subject,query,now,limit=5)` | 主体/时间过滤后做key与value子串匹配 |
| `forget(subject,key)` | 清空活动内容/来源，保留版本墓碑；返回是否实际删除 |
| `close()` | 关闭数据库连接；两个Store都提供 |

[checkpoint.py](src/state_memory/checkpoint.py)演示事务中的CAS快照，[memory.py](src/state_memory/memory.py)实现选择性事实存储，[测试](tests/test_memory.py)验证两个独立连接恢复、旧版本冲突、过期边界、跨主体读取、删除及错误数据不提交。

注意：subject必须由可信调用方传入，本包没有网络身份认证；教学时钟由调用方指定；无向量检索或模型自动记忆抽取；删除是活动表逻辑清除而非安全擦盘；Checkpoint历史和备份没有自动保留期；过期记录仍保留版本，防止旧写入重新创建。读[概念篇](../../01-concepts/01-state-and-checkpoints.md)和[实验](../../04-labs/01-state-memory-and-conflicts.ipynb)了解这些取舍。
