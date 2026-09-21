# 订单通信记录

负责人：coordinator；epoch：1。

| 顺序 | 消息 | 接收决定 |
|---:|---|---|
| 1 | request-001 | delegated |
| 2 | message-002 | accepted_started |
| 3 | message-003 | accepted_failure |
| 4 | request-004 | delegated |
| 5 | message-005 | accepted_started |
| 6 | message-006 | accepted_result |
| 7 | message-006 | duplicate |
| 8 | message-006 | conflicting_message |
| 9 | message-007 | stale_attempt |
| 10 | message-008 | late_progress |
| 11 | message-009 | wrong_correlation |
| 12 | message-010 | stale_input |
| 13 | message-011 | duplicate_outcome |
| 14 | message-012 | conflicting_outcome |
| 15 | message-006 | duplicate |

## 待客户确认的草稿

尚未生成。
