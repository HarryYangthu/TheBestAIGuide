# 订单执行记录

- accepted: True
- executions: 10
- peak_active: 2

| 节点 | 状态 |
|---|---|
| stock | succeeded |
| prices | succeeded |
| policy | succeeded |
| quote | succeeded |
| review | succeeded |
| publish | succeeded |

## 验收后的报价

```json
{
  "order_id": "event-001",
  "subtotal_cents": 5800,
  "shipping_cents": 0,
  "total_cents": 5800,
  "available": true,
  "price_version": 2
}
```
