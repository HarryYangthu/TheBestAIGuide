"""串行、进程内的教学 Harness；隔离可变输入，但不是不可信代码沙箱。"""
from copy import deepcopy
from time import perf_counter
from .tasks import EvalTask, TrialFixture, TrialResult
from .graders import grade


def run_suite(tasks: list[EvalTask], system, trials: int = 1) -> list[TrialResult]:
    if trials < 1 or len({t.id for t in tasks}) != len(tasks):
        raise ValueError("positive trials and unique task ids are required")
    results = []
    for task in tasks:
        for trial_index in range(trials):
            fixture = TrialFixture.from_task(task)
            events = []
            def emit(event_type: str, **attributes):
                # 默认只留调用者明确提供的非敏感元数据，不自动记录请求正文。
                events.append({"sequence": len(events), "type": event_type,
                               "attributes": deepcopy(attributes)})
            started = perf_counter()
            status, error, output = "completed", None, {}
            emit("trial_start", task_id=task.id, trial_index=trial_index)
            try:
                output = system(deepcopy(task.input), fixture.data, emit)
                if not isinstance(output, dict):
                    raise TypeError("system output must be a dict")
                checks = grade(task.expected, output, fixture.data)
            except Exception as exc:
                status, error = "system_error", type(exc).__name__
                checks = {"system_completed": False}
                emit("system_error", error_type=error)
            elapsed = (perf_counter() - started) * 1000
            success = status == "completed" and bool(checks) and all(checks.values())
            emit("trial_end", status=status, success=success)
            results.append(TrialResult(task.id, task.version, trial_index, status,
                success, checks, deepcopy(output), deepcopy(fixture.data), events,
                elapsed, tuple(task.tags), task.critical, error))
    return results
