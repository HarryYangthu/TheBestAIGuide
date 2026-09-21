"""A local, explicit DAG scheduler. Workers are async functions, not LLM agents."""
import asyncio
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from graphlib import TopologicalSorter


@dataclass(frozen=True)
class Node:
    task_id: str
    dependencies: tuple[str, ...]
    capability: str
    input_version: str = "1"
    timeout: float = 1.0


@dataclass(frozen=True)
class Role:
    name: str
    capabilities: frozenset[str]
    capacity: int
    cost: int


ROLES = (
    Role("reader", frozenset({"read"}), 2, 1),
    Role("calculator", frozenset({"calculate"}), 1, 1),
    Role("reviewer", frozenset({"review", "publish"}), 1, 2),
)


def validate_plan(nodes):
    plan = {node.task_id: node for node in nodes}
    if len(plan) != len(nodes):
        raise ValueError("duplicate task_id")
    for node in nodes:
        if not set(node.dependencies) <= plan.keys():
            raise ValueError(f"unknown dependency: {node.task_id}")
        if node.timeout <= 0:
            raise ValueError("timeout must be positive")
    TopologicalSorter({key: node.dependencies for key, node in plan.items()}).prepare()
    return plan


def affected_closure(plan, seeds):
    affected = set(seeds)
    while True:
        expanded = affected | {key for key, node in plan.items()
                               if affected.intersection(node.dependencies)}
        if expanded == affected:
            return affected
        affected = expanded


class Scheduler:
    def __init__(self, nodes, worker, concurrency=2, roles=ROLES, max_executions=20):
        if concurrency < 1 or max_executions < 1:
            raise ValueError("limits must be positive")
        self.plan = validate_plan(nodes)
        if any(role.capacity < 1 for role in roles):
            raise ValueError("role capacity must be positive")
        for node in nodes:
            if not any(node.capability in role.capabilities for role in roles):
                raise ValueError(f"no qualified role: {node.task_id}")
        self.worker, self.concurrency, self.roles = worker, concurrency, roles
        self.max_executions = max_executions
        self.states = {key: "pending" for key in self.plan}
        self.results, self.errors, self.events = {}, {}, []
        self.running, self.role_use = {}, Counter()
        self.executions, self.peak_active, self.plan_version = 0, 0, 1
        self._in_run = False

    def emit(self, kind, task_id=None, **details):
        self.events.append({"seq": len(self.events) + 1, "kind": kind,
                            "task_id": task_id, "plan_version": self.plan_version,
                            **details})

    def select_role(self, node):
        candidates = [role for role in self.roles
                      if node.capability in role.capabilities
                      and self.role_use[role.name] < role.capacity]
        return min(candidates, key=lambda role: (role.cost, role.name), default=None)

    async def execute_child(self, node, role):
        # Each child receives its own dependency snapshot; mutation cannot leak.
        context = {key: deepcopy(self.results[key]) for key in node.dependencies}
        try:
            value = await asyncio.wait_for(self.worker(node, context), node.timeout)
            if not isinstance(value, dict):
                raise TypeError("worker result must be a dictionary")
            return value
        finally:
            self.emit("cleanup", node.task_id, role=role.name)

    async def run(self):
        if self._in_run:
            raise RuntimeError("scheduler is already running")
        self._in_run = True
        try:
            while True:
                # Failure blocks descendants, while unrelated branches may finish.
                terminal_roots = {key for key, state in self.states.items()
                                  if state in {"failed", "blocked", "cancelled"}}
                blocked = affected_closure(self.plan, terminal_roots)
                for key in self.plan:
                    if self.states[key] in {"pending", "ready"} and key in blocked:
                        self.states[key] = "blocked"
                        self.emit("blocked", key)
                ready = sorted(key for key, node in self.plan.items()
                               if self.states[key] in {"pending", "ready"}
                               and all(self.states[dep] == "succeeded"
                                       for dep in node.dependencies))
                for key in ready:
                    if self.states[key] == "pending":
                        self.states[key] = "ready"
                        self.emit("ready", key)
                    if len(self.running) >= self.concurrency:
                        break
                    role = self.select_role(self.plan[key])
                    if role is None:
                        continue
                    if self.executions >= self.max_executions:
                        self.states[key] = "failed"
                        self.errors[key] = "execution budget exhausted"
                        self.emit("failed", key, error=self.errors[key])
                        continue
                    self.executions += 1
                    self.role_use[role.name] += 1
                    self.states[key] = "running"
                    handle = asyncio.create_task(self.execute_child(self.plan[key], role), name=key)
                    self.running[handle] = (key, role)
                    self.peak_active = max(self.peak_active, len(self.running))
                    self.emit("start", key, role=role.name, active=len(self.running),
                              input_version=self.plan[key].input_version)
                if not self.running:
                    if all(state in {"succeeded", "failed", "blocked", "cancelled"}
                           for state in self.states.values()):
                        break
                    # A budget failure may have made another layer blockable.
                    if any(state == "failed" for state in self.states.values()):
                        before = dict(self.states)
                        for key in affected_closure(self.plan, set(self.errors)):
                            if self.states[key] in {"pending", "ready"}:
                                self.states[key] = "blocked"
                                self.emit("blocked", key)
                        if before != self.states:
                            continue
                    raise RuntimeError("no runnable tasks")
                done, _ = await asyncio.wait(self.running, return_when=asyncio.FIRST_COMPLETED)
                for handle in sorted(done, key=lambda item: self.running[item][0]):
                    key, role = self.running.pop(handle)
                    self.role_use[role.name] -= 1
                    try:
                        value = handle.result()
                    except asyncio.CancelledError:
                        self.states[key] = "cancelled"
                        self.errors[key] = "child cancelled itself"
                        self.emit("cancelled", key, reason="child_cancelled")
                    except Exception as error:
                        self.states[key] = "failed"
                        self.errors[key] = f"{type(error).__name__}: {error}"
                        self.emit("failed", key, error=self.errors[key])
                    else:
                        self.results[key] = value
                        self.states[key] = "succeeded"
                        self.emit("succeeded", key)
        except asyncio.CancelledError:
            self.emit("parent_cancelled")
            raise
        finally:
            # Cancellation is a request; await children before releasing ownership.
            handles = list(self.running)
            for handle in handles:
                handle.cancel()
            if handles:
                await asyncio.gather(*handles, return_exceptions=True)
            for handle in handles:
                key, role = self.running.pop(handle)
                self.role_use[role.name] -= 1
                self.states[key] = "cancelled"
                self.emit("cancelled", key)
            for key, state in self.states.items():
                if state in {"pending", "ready"}:
                    self.states[key] = "cancelled"
                    self.emit("cancelled", key)
            self._in_run = False
        return deepcopy(self.results)

    def replan(self, nodes, changed_inputs=()):
        if self._in_run:
            raise RuntimeError("replan requires a quiescent scheduler")
        replacement = validate_plan(nodes)
        for node in nodes:
            if not any(node.capability in role.capabilities for role in self.roles):
                raise ValueError(f"no qualified role: {node.task_id}")
        unknown = set(changed_inputs) - (self.plan.keys() | replacement.keys())
        if unknown:
            raise ValueError(f"unknown changed inputs: {sorted(unknown)}")
        changed = set(changed_inputs) | {
            key for key in self.plan.keys() | replacement.keys()
            if self.plan.get(key) != replacement.get(key)
        }
        # Union of both closures covers removed edges and newly added edges.
        affected = affected_closure(self.plan, changed) | affected_closure(replacement, changed)
        retained = sorted(key for key in self.results if key in replacement and key not in affected)
        self.results = {key: self.results[key] for key in retained}
        self.errors = {}
        self.plan = replacement
        self.states = {key: "succeeded" if key in self.results else "pending" for key in self.plan}
        self.plan_version += 1
        self.emit("replan", invalidated=sorted(affected), retained=retained)
        return sorted(affected)

    def snapshot(self):
        return {"states": deepcopy(self.states), "results": deepcopy(self.results),
                "errors": dict(self.errors), "executions": self.executions,
                "peak_active": self.peak_active, "plan_version": self.plan_version,
                "events": deepcopy(self.events)}
