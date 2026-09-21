"""Versioned order policy. No model calls and no hidden fallback."""
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path


def validate_policy(policy):
    if set(policy) != {"normalize_status", "invalid_amount", "include_negative"}:
        raise ValueError("unexpected policy fields")
    if type(policy["normalize_status"]) is not bool or type(policy["include_negative"]) is not bool:
        raise ValueError("policy booleans required")
    if policy["invalid_amount"] not in {"reject", "skip_and_record"}:
        raise ValueError("unsupported invalid_amount action")


def aggregate(source, policy):
    validate_policy(policy)
    total, count, rejected = 0, 0, []
    with Path(source).open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            status = row["status"].strip().casefold() if policy["normalize_status"] else row["status"]
            if status != "paid":
                continue
            try:
                value = Decimal(row["amount"])
                if not value.is_finite() or value * 100 != (value * 100).to_integral_value():
                    raise InvalidOperation
                cents = int(value * 100)
            except (InvalidOperation, ValueError):
                if policy["invalid_amount"] == "reject":
                    raise ValueError(f"invalid_amount: order={row['order_id']}") from None
                rejected.append(row["order_id"])
                continue
            if cents < 0 and not policy["include_negative"]:
                continue
            total += cents
            count += 1
    return {"total_cents": total, "paid_rows": count, "rejected_rows": rejected}
