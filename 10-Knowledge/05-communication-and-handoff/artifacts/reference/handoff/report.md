# 订单通信记录

负责人：fulfillment-specialist；epoch：2。

| 顺序 | 消息 | 接收决定 |
|---:|---|---|
| 1 | request-001 | delegated |
| 2 | message-002 | accepted_started |
| 3 | message-003 | accepted_result |
| 4 | — | handoff_offered |
| 5 | — | handoff_accepted |
| 6 | — | rejected_stale_owner |
| 7 | — | draft_created |

## 待客户确认的草稿

订单 order-017 需要 3 支笔，当前可供 2 支，还缺 1 支。请确认是否接受分批发货；补货日期待确认。
