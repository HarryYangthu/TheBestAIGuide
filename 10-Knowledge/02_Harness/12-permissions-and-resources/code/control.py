"""Single-process permission, approval, and resource enforcement."""
from __future__ import annotations

import asyncio
import hashlib
import json
import secrets
import time
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Denied(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class Principal:
    subject: str
    tenant: str
    tools: frozenset[str]


@dataclass(frozen=True)
class Request:
    id: str
    tool: str
    resource: str
    steps: int = 1
    delay_ms: int = 0


def fingerprint(principal, request, payload):
    value = {"subject": principal.subject, "tenant": principal.tenant,
             "request": asdict(request), "payload": payload}
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class Approvals:
    """Host-owned store; grant is never exposed as an Agent tool."""
    def __init__(self, events):
        self.entries, self.events = {}, events

    def grant(self, principal, request, payload, ttl=60, source="human"):
        token = secrets.token_urlsafe(24)
        signature = fingerprint(principal, request, payload)
        self.entries[token] = {"fingerprint": signature, "expires": time.monotonic() + ttl, "used": False}
        self.events.append({"event": "approval_granted", "request": request.id,
                            "fingerprint": signature, "source": source})
        return token

    def check(self, token, principal, request, payload, consume=False):
        entry = self.entries.get(token)
        if entry is None:
            raise Denied("approval_required")
        if entry["used"]:
            raise Denied("approval_used")
        if time.monotonic() >= entry["expires"]:
            raise Denied("approval_expired")
        if entry["fingerprint"] != fingerprint(principal, request, payload):
            raise Denied("approval_mismatch")
        if consume:
            entry["used"] = True
        return entry["fingerprint"]


class Budget:
    def __init__(self, units=20, cost_micros=60, calls=10, events=None):
        if any(type(x) is not int or x < 0 for x in (units, cost_micros, calls)):
            raise ValueError("invalid budget")
        self.limit_units, self.limit_cost, self.limit_calls = units, cost_micros, calls
        self.spent_units = self.spent_cost = self.calls = 0
        self.reservations, self.settled, self.seen = {}, set(), set()
        self.lock = asyncio.Lock()
        self.events = events if events is not None else []

    def snapshot(self):
        reserved_units = sum(r["units"] for r in self.reservations.values())
        reserved_cost = sum(r["cost_micros"] for r in self.reservations.values())
        return {"spent_units": self.spent_units, "reserved_units": reserved_units,
                "available_units": self.limit_units - self.spent_units - reserved_units,
                "spent_cost_micros": self.spent_cost, "reserved_cost_micros": reserved_cost,
                "available_cost_micros": self.limit_cost - self.spent_cost - reserved_cost,
                "calls": self.calls, "unknown": sorted(k for k, r in self.reservations.items() if r["unknown"])}

    async def reserve(self, request_id, units, cost_micros):
        if type(units) is not int or units <= 0 or type(cost_micros) is not int or cost_micros < 0:
            raise Denied("invalid_reservation")
        async with self.lock:
            if request_id in self.seen:
                raise Denied("duplicate_request")
            state = self.snapshot()
            if self.calls >= self.limit_calls:
                raise Denied("call_budget_exhausted")
            if units > state["available_units"] or cost_micros > state["available_cost_micros"]:
                raise Denied("budget_exhausted")
            self.reservations[request_id] = {"units": units, "cost_micros": cost_micros, "unknown": False}
            self.seen.add(request_id)
            self.calls += 1
            self.events.append({"event": "reserved", "request": request_id, **self.snapshot()})

    async def settle(self, request_id, units, cost_micros):
        async with self.lock:
            if request_id in self.settled:
                raise Denied("already_settled")
            if request_id not in self.reservations:
                raise Denied("no_reservation")
            reservation = self.reservations[request_id]
            if type(units) is not int or type(cost_micros) is not int or not 0 <= units <= reservation["units"] or not 0 <= cost_micros <= reservation["cost_micros"]:
                raise Denied("receipt_exceeds_reservation")
            self.spent_units += units
            self.spent_cost += cost_micros
            del self.reservations[request_id]
            self.settled.add(request_id)
            self.events.append({"event": "settled", "request": request_id, **self.snapshot()})

    async def mark_unknown(self, request_id):
        async with self.lock:
            self.reservations[request_id]["unknown"] = True
            self.events.append({"event": "usage_unknown", "request": request_id, **self.snapshot()})


class Runtime:
    def __init__(self, output, *, concurrency=2, budget=None):
        if type(concurrency) is not int or concurrency < 1:
            raise ValueError("invalid concurrency")
        self.output = Path(output)
        self.output.mkdir(parents=True, exist_ok=True)
        self.records = json.loads((ROOT / "examples/records.json").read_text(encoding="utf-8"))
        self.events = []
        self.approvals = Approvals(self.events)
        self.budget = budget or Budget()
        self.budget.events = self.events
        self.semaphore = asyncio.Semaphore(concurrency)
        self.active = self.peak = 0

    def authorize(self, principal, request):
        if any(type(value) is not str or not value for value in (request.id, request.tool, request.resource)):
            raise Denied("invalid_arguments")

        if request.tool not in principal.tools or request.tool not in {"read_record", "publish_record"}:
            raise Denied("tool_denied")
        if request.resource not in self.records or self.records[request.resource]["tenant"] != principal.tenant:
            # Do not reveal whether another tenant's resource exists.
            raise Denied("resource_denied")
        if type(request.steps) is not int or not 1 <= request.steps <= 20 or type(request.delay_ms) is not int or not 0 <= request.delay_ms <= 1000:
            raise Denied("invalid_arguments")

    def project(self, request):
        record = self.records[request.resource]
        return {key: record[key] for key in ("title", "daily_delivery")}

    async def execute(self, principal, request, *, deadline, token=None, upper_units=None):
        """deadline uses the event loop's monotonic clock and includes queue time."""
        upper_units = request.steps if upper_units is None else upper_units
        receipt = {"units": 0, "cost_micros": 0}
        reserved = False
        result = None
        try:
            self.authorize(principal, request)
            if request.tool == "publish_record":
                self.approvals.check(token, principal, request, self.project(request))
            if type(upper_units) is not int or upper_units < request.steps:
                raise Denied("reservation_too_small")
            if asyncio.get_running_loop().time() >= deadline:
                raise Denied("deadline_exceeded")
            async with asyncio.timeout_at(deadline):
                async with self.semaphore:
                    await self.budget.reserve(request.id, upper_units, upper_units * 3)
                    reserved = True
                    if request.tool == "publish_record":
                        approved_fingerprint = self.approvals.check(token, principal, request, self.project(request), consume=True)
                    self.active += 1
                    self.peak = max(self.peak, self.active)
                    self.events.append({"event": "started", "request": request.id, "active": self.active})
                    try:
                        for _ in range(request.steps):
                            await asyncio.sleep(request.delay_ms / 1000)
                            # Local service bills exactly three microcredits per completed unit.
                            receipt["units"] += 1
                            receipt["cost_micros"] += 3
                        self.authorize(principal, request)
                        projected = self.project(request)
                        if request.tool == "publish_record":
                            if fingerprint(principal, request, projected) != approved_fingerprint:
                                raise Denied("approval_content_changed")
                            target = self.output / f"{request.resource}.json"
                            target.write_text(json.dumps(projected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                            projected = {"artifact": target.name}
                        result = {"id": request.id, "status": "completed", "data": projected}
                    finally:
                        self.active -= 1
                        self.events.append({"event": "released", "request": request.id, "active": self.active})
        except TimeoutError:
            result = {"id": request.id, "status": "deadline_exceeded"}
        except asyncio.CancelledError:
            self.events.append({"event": "cancelled", "request": request.id})
            raise
        except Denied as exc:
            result = {"id": request.id, "status": exc.code}
        finally:
            if reserved:
                # Local work has an exact receipt even on cancellation. Remote unknown
                # usage must call mark_unknown instead (see the dedicated experiment).
                await self.budget.settle(request.id, **receipt)
        self.events.append({"event": "result", **result})
        return result


def principal():
    return Principal("alice", "A", frozenset({"read_record", "publish_record"}))
