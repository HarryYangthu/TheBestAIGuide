"""The model proposes actions; only the runtime changes authoritative state."""
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class Action:
    kind: str
    name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    answer: str = ""


@dataclass
class AgentState:
    task: str
    run_id: str
    status: str = "running"
    steps: int = 0
    observations: list[dict[str, Any]] = field(default_factory=list)
    answer: str = ""
    stop_reason: str = ""


class Model(Protocol):
    def decide(self, state: AgentState) -> Action: ...


class ScriptedModel:
    """Offline fixture, not an LLM. Useful for exercising runtime failure paths."""
    def __init__(self, actions: list[Action]):
        self.actions = iter(actions)

    def decide(self, state: AgentState) -> Action:
        return next(self.actions)


class EvidenceModel:
    """Deterministic policy for the local document-search teaching task."""
    def decide(self, state: AgentState) -> Action:
        if not state.observations:
            return Action("tool", "search", {"query": state.task})
        result = state.observations[-1]
        if not result["ok"]:
            return Action("finish", answer="检索失败，不能给出有证据的答案。")
        docs = result["data"]["documents"]
        if not docs:
            return Action("finish", answer="教学语料没有对应证据。")
        return Action("finish", answer="\n".join(f"[{d['id']}] {d['text']}" for d in docs))
