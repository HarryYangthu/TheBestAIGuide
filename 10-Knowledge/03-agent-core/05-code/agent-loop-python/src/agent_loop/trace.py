"""Write a fresh JSONL trace per run; no hidden model reasoning is required."""
import json
from pathlib import Path


def write_trace(path: str | None, events: list[dict]) -> None:
    if path is None:
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create prevents accidentally overwriting a different run's trace.
    with target.open("x", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False, allow_nan=False) + "\n")
