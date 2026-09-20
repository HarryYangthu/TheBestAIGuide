from copy import deepcopy
import json
from uuid import uuid4
from .models import Action, AgentState, Model
from .tools import Tool
from .trace import write_trace


def _validate_json(value) -> None:
    """Reject Python-only values before tracing or canonical signature creation."""
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("JSON object keys must be strings")
        for item in value.values():
            _validate_json(item)
    elif isinstance(value, list):
        for item in value:
            _validate_json(item)
    elif value is None or type(value) in {str, bool, int, float}:
        json.dumps(value, allow_nan=False)
    else:
        raise ValueError("value is not JSON data")


def run_agent(model: Model, tools: dict[str, Tool], task: str, *, max_steps: int = 8,
              repeat_limit: int = 2, trace_path: str | None = None) -> AgentState:
    """Bounded synchronous loop. No hard timeout/sandbox for untrusted Python."""
    if max_steps < 1 or repeat_limit < 1:
        raise ValueError("budgets must be positive")
    state = AgentState(task=task, run_id=uuid4().hex)
    events: list[dict] = []
    repetitions: dict[str, int] = {}

    def event(kind: str, data: dict) -> None:
        events.append({"run_id": state.run_id, "seq": len(events), "kind": kind, "data": deepcopy(data)})

    def stop(status: str, reason: str) -> None:
        state.status, state.stop_reason = status, reason

    for _ in range(max_steps):
        state.steps += 1
        try:
            # A model cannot corrupt the runtime by mutating the state it sees.
            action = deepcopy(model.decide(deepcopy(state)))
            if not isinstance(action, Action) or action.kind not in {"tool", "finish"}:
                raise ValueError("model must return Action(tool|finish)")
            if action.kind == "finish":
                if not isinstance(action.answer, str) or not action.answer.strip():
                    raise ValueError("finish requires a non-empty answer")
                state.answer = action.answer
                stop("completed", "model_finished")
                break
            if not isinstance(action.name, str) or not action.name or not isinstance(action.arguments, dict):
                raise ValueError("tool requires name and object arguments")
            _validate_json(action.arguments)
        except Exception as error:
            # Exception type is useful; provider messages may contain secrets.
            event("model_error", {"type": type(error).__name__})
            stop("failed", "invalid_model_output")
            break
        call_id = f"{state.run_id}:{state.steps}"
        event("tool_call", {"call_id": call_id, "name": action.name, "arguments": action.arguments})
        tool = tools.get(action.name)
        if tool is None:
            result = {"call_id": call_id, "ok": False, "error": {"code": "unknown_tool", "retryable": False}}
        elif not tool.allowed:
            result = {"call_id": call_id, "ok": False, "error": {"code": "permission_denied", "retryable": False}}
        else:
            try:
                data = tool.handler(deepcopy(action.arguments))
            except ValueError:
                result = {"call_id": call_id, "ok": False, "error": {"code": "invalid_arguments", "retryable": False}}
            except Exception:
                result = {"call_id": call_id, "ok": False, "error": {"code": "execution_error", "retryable": False}}
            else:
                try:
                    _validate_json(data)
                    result = {"call_id": call_id, "ok": True, "data": deepcopy(data)}
                except Exception:
                    result = {"call_id": call_id, "ok": False, "error": {"code": "invalid_output", "retryable": False}}
        state.observations.append(result)
        event("tool_result", result)
        signature = json.dumps([action.name, action.arguments, {k: v for k, v in result.items() if k != "call_id"}], sort_keys=True)
        repetitions[signature] = repetitions.get(signature, 0) + 1
        if repetitions[signature] >= repeat_limit:
            stop("stopped", "no_progress")
            break
    else:
        stop("stopped", "max_steps")
    event("run_finished", {"status": state.status, "reason": state.stop_reason, "steps": state.steps})
    write_trace(trace_path, events)
    return state
