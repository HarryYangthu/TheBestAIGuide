"""Task 中的 expected 属于评分侧；被测函数只接收 input 与独立 fixture。"""
from dataclasses import dataclass, field
from copy import deepcopy
from typing import Any


@dataclass(frozen=True)
class EvalTask:
    id: str
    input: dict
    expected: dict
    fixture: dict = field(default_factory=dict)
    tags: tuple[str, ...] = ()
    critical: bool = False
    version: str = "1"

    def __post_init__(self):
        if not self.id or not self.version:
            raise ValueError("task id and version are required")
        if not all(isinstance(x,dict) for x in (self.input,self.fixture,self.expected)):
            raise ValueError("input, fixture and expected must be dictionaries")
        if any(key in self.expected and not isinstance(self.expected[key],dict)
               for key in ("output","state")):
            raise ValueError("expected.output and expected.state must be dictionaries")
        forbidden = self.expected.get("forbidden_strings",[])
        if not isinstance(forbidden,list) or any(not isinstance(x,str) or not x for x in forbidden):
            raise ValueError("expected.forbidden_strings must be a list of non-empty strings")
        if not any(self.expected.get(key) for key in ("output", "state", "forbidden_strings")):
            raise ValueError("task requires at least one non-empty grading criterion")
        unknown = set(self.expected) - {"output", "state", "forbidden_strings"}
        if unknown:
            raise ValueError(f"unknown grading criteria: {sorted(unknown)}")


@dataclass
class TrialFixture:
    data: dict[str, Any]

    @classmethod
    def from_task(cls, task: EvalTask):
        return cls(deepcopy(task.fixture))


@dataclass
class TrialResult:
    task_id: str
    task_version: str
    trial_index: int
    status: str
    success: bool
    checks: dict[str, bool]
    outcome: dict
    state: dict
    events: list[dict]
    latency_ms: float
    tags: tuple[str, ...]
    critical: bool
    error: str | None = None
