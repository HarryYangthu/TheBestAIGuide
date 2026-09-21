"""Versioned sample policy. No model calls and no hidden fallback."""
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path


def validate_policy(policy):
    if set(policy) != {"normalize_status", "invalid_value", "include_negative"}:
        raise ValueError("unexpected policy fields")
    if type(policy["normalize_status"]) is not bool or type(policy["include_negative"]) is not bool:
        raise ValueError("policy booleans required")
    if policy["invalid_value"] not in {"reject", "skip_and_record"}:
        raise ValueError("unsupported invalid_value action")


def aggregate(source, policy):
    validate_policy(policy)
    total, count, rejected = 0, 0, []
    with Path(source).open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            status = row["status"].strip().casefold() if policy["normalize_status"] else row["status"]
            if status != "valid":
                continue
            try:
                value = Decimal(row["value"])
                if not value.is_finite() or value != (value).to_integral_value():
                    raise InvalidOperation
                integer_values = int(value)
            except (InvalidOperation, ValueError):
                if policy["invalid_value"] == "reject":
                    raise ValueError(f"invalid_value: sample={row['sample_id']}") from None
                rejected.append(row["sample_id"])
                continue
            if integer_values < 0 and not policy["include_negative"]:
                continue
            total += integer_values
            count += 1
    return {"total": total, "valid_rows": count, "rejected_rows": rejected}
