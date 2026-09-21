"""The smallest delegation is a function call with a verifiable return value."""
import json
from pathlib import Path


def check_stock(order, inventory):
    available = inventory["stock"].get(order["sku"], 0)
    return {"sku": order["sku"], "requested": order["quantity"],
            "available": available, "shortage": max(0, order["quantity"] - available),
            "evidence": {"version": inventory["version"], "pointer": f"/stock/{order['sku']}"}}


def main():
    order = json.loads(Path("fixtures/order.json").read_text(encoding="utf-8"))
    inventory = json.loads(Path("fixtures/inventory-ready.json").read_text(encoding="utf-8"))
    result = check_stock(order, inventory)
    output = Path("runs/v1")
    output.mkdir(parents=True, exist_ok=True)
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"sku={result['sku']} requested={result['requested']} available={result['available']} shortage={result['shortage']}")
    print("owner=coordinator")
    print("artifacts=runs/v1")


if __name__ == "__main__":
    main()
