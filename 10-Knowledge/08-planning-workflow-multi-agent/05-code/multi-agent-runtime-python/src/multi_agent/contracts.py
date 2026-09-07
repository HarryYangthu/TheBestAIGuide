"""教学任务契约：仅接收 JSON 兼容数据，不传整个主 Agent 状态。"""
from dataclasses import dataclass, field
from typing import Any, Literal
import json, math

@dataclass(frozen=True)
class Task:
    task_id: str
    kind: str
    payload: dict[str, Any]
    required_keys: tuple[str, ...]
    timeout_s: float = 1.0

    def __post_init__(self):
        if not self.task_id or not self.kind:
            raise ValueError("task_id and kind are required")
        if not isinstance(self.payload, dict) or not all(isinstance(k, str) for k in self.payload):
            raise ValueError("payload must be an object with string keys")
        json.dumps(self.payload, allow_nan=False)
        if not math.isfinite(self.timeout_s) or self.timeout_s <= 0:
            raise ValueError("timeout_s must be positive and finite")
        if len(set(self.required_keys)) != len(self.required_keys):
            raise ValueError("required_keys must be unique")

@dataclass
class WorkerResult:
    task_id: str
    status: Literal["ok", "error", "timeout"]
    values: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

@dataclass
class RunResult:
    results: list[WorkerResult]
    trace: list[dict[str, Any]]
    max_active: int
