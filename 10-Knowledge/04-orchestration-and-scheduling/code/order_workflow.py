import asyncio
import json
from copy import deepcopy
from pathlib import Path
from scheduler import Node


def load_inputs(prices="prices-v1.json"):
    root = Path(__file__).resolve().parent.parent / "fixtures"
    names = {"order": "order.json", "stock": "stock.json",
             "prices": prices, "policy": "policy.json"}
    return {key: json.loads((root / name).read_text(encoding="utf-8"))
            for key, name in names.items()}


def make_plan(price_version="1", shipping=False):
    nodes = [Node("stock", (), "read"), Node("prices", (), "read", price_version),
             Node("policy", (), "read")]
    if shipping:
        nodes.append(Node("shipping", ("policy",), "calculate"))
    quote_deps = ("stock", "prices", "shipping") if shipping else ("stock", "prices")
    return nodes + [Node("quote", quote_deps, "calculate"),
                    Node("review", ("quote", "policy"), "review"),
                    Node("publish", ("review",), "publish")]


class OrderWorker:
    def __init__(self, inputs, delays=None):
        self.inputs = deepcopy(inputs)
        self.delays = delays or {"stock": .02, "prices": .03, "policy": .01}

    async def __call__(self, node, dependencies):
        await asyncio.sleep(self.delays.get(node.task_id, .001))
        inputs = self.inputs
        if node.task_id == "stock":
            available = all(inputs["stock"].get(item["sku"], 0) >= item["quantity"]
                            for item in inputs["order"]["items"])
            return {"available": available, "items": deepcopy(inputs["order"]["items"])}
        if node.task_id == "prices":
            prices = inputs["prices"]
            for item in inputs["order"]["items"]:
                if item["sku"] not in prices["unit_cents"]:
                    raise ValueError(f"missing price: {item['sku']}")
            return deepcopy(prices)
        if node.task_id == "policy":
            return deepcopy(inputs["policy"])
        if node.task_id == "shipping":
            return {"shipping_cents": dependencies["policy"]["shipping_cents"]}
        if node.task_id == "quote":
            stock, prices = dependencies["stock"], dependencies["prices"]
            total = sum(item["quantity"] * prices["unit_cents"][item["sku"]]
                        for item in stock["items"])
            fee = dependencies.get("shipping", {}).get("shipping_cents", 0)
            return {"order_id": inputs["order"]["order_id"], "subtotal_cents": total,
                    "shipping_cents": fee, "total_cents": total + fee,
                    "available": stock["available"], "price_version": prices["version"]}
        if node.task_id == "review":
            quote = dependencies["quote"]
            if not quote["available"]:
                raise ValueError("insufficient stock")
            if quote["total_cents"] > dependencies["policy"]["maximum_cents"]:
                raise ValueError("over budget")
            return {"accepted": True, "quote": deepcopy(quote)}
        if node.task_id == "publish":
            return deepcopy(dependencies["review"])
        raise ValueError(f"unknown worker: {node.task_id}")


def save_run(output, scheduler, inputs, extra=None):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    result = scheduler.snapshot()
    result["accepted"] = result["results"].get("publish", {}).get("accepted", False)
    result.update(extra or {})
    (output / "input.json").write_text(json.dumps(inputs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "events.jsonl").write_text("".join(json.dumps(event, ensure_ascii=False) + "\n" for event in result["events"]), encoding="utf-8")
    lines = ["# 订单执行记录", "", f"- accepted: {result['accepted']}",
             f"- executions: {result['executions']}", f"- peak_active: {result['peak_active']}", "",
             "| 节点 | 状态 |", "|---|---|"]
    lines.extend(f"| {key} | {state} |" for key, state in result["states"].items())
    if result["accepted"]:
        lines += ["", "## 验收后的报价", "", "```json",
                  json.dumps(result["results"]["publish"]["quote"], ensure_ascii=False, indent=2), "```"]
    if result["errors"]:
        lines += ["", "## 失败原因", "", json.dumps(result["errors"], ensure_ascii=False)]
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result
