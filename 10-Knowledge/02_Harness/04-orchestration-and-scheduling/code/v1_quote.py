"""Minimal calculation. Run from the chapter directory; standard library only."""
import json
from pathlib import Path


def main():
    order = json.loads(Path("fixtures/order.json").read_text(encoding="utf-8"))
    prices = json.loads(Path("fixtures/prices-v1.json").read_text(encoding="utf-8"))
    total = sum(item["quantity"] * prices["unit_cents"][item["sku"]]
                for item in order["items"])
    output = Path("runs/v1")
    output.mkdir(parents=True, exist_ok=True)
    result = {"order_id": order["order_id"], "total_cents": total}
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"order={order['order_id']} total_cents={total}")
    print("artifacts=runs/v1")


if __name__ == "__main__":
    main()
