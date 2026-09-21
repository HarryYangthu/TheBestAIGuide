# 跨次任务复用实验

| 阶段 | 独立进程输出 |
|---|---|
| learn | stored=8 active=7 |
| reuse | selected=fact-timeout-v3,failure-permission,procedure-rollback; language=en |
| no-trigger | selected=fact-timeout-v3,procedure-rollback; language=en |
| conflict | status=disputed |
| disputed | selected=failure-permission,procedure-rollback; language=en |
| update | status=active |
| new-policy | selected=fact-timeout-v4,failure-permission,procedure-rollback; language=en |
| expiry | expired=6 |
| expired | selected=; language=en |
| forget | forgot=pref-language |
