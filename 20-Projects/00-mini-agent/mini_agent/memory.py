"""Lesson 04: explicit user preferences, not automatic conversation storage."""
import json
from pathlib import Path


def set_format(path, value):
    path = Path(path)
    if value not in ("table", "bullets", "delete"):
        raise ValueError("format must be table, bullets or delete")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {} if value == "delete" else {"format": value, "source": "explicit_user_setting"}
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)


def resolve_format(path, current=None):
    if current:
        return current, "current_request"
    path = Path(path)
    if path.exists():
        value = json.loads(path.read_text(encoding="utf-8")).get("format")
        if value in ("table", "bullets"):
            return value, "memory"
    return "table", "default"
