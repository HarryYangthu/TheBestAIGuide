"""In-process message protocol with correlation, retries and explicit ownership."""
import asyncio
from copy import deepcopy
import json
from pathlib import Path
from v1_delegate import check_notes

ROOT = Path(__file__).resolve().parent.parent


def read_fixture(name):
    # All snapshot reads must stay within fixtures; inputs never select tools.
    path = (ROOT / "fixtures" / name).resolve()
    if not path.is_relative_to((ROOT / "fixtures").resolve()):
        raise ValueError("fixture path escapes allowed directory")
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(message):
    return json.dumps(message, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class Inbox:
    def __init__(self):
        self.seen = {}

    def register(self, message):
        fingerprint = canonical(message)
        previous = self.seen.get(message["message_id"])
        if previous is not None:
            return "duplicate" if previous == fingerprint else "conflicting_message"
        self.seen[message["message_id"]] = fingerprint
        return "new"


class LocalBus:
    def __init__(self, names):
        self.queues = {name: asyncio.Queue() for name in names}
        self.wire = []
        self.worker_inbox, self.worker_cache = Inbox(), {}
        self.worker_lock = asyncio.Lock()
        self.worker_executions = 0

    async def send(self, message):
        encoded = canonical(message)
        self.wire.append(json.loads(encoded))
        await self.queues[message["to"]].put(encoded)

    async def receive(self, recipient):
        encoded = await self.queues[recipient].get()
        self.queues[recipient].task_done()
        return json.loads(encoded)


class Case:
    def __init__(self, task=None, max_attempts=2):
        self.task = deepcopy(task or read_fixture("task.json"))
        self.case_id = self.task["case_id"]
        self.owner, self.epoch = "coordinator", 1
        self.requests, self.states, self.results, self.failures = {}, {}, {}, {}
        self.inbox, self.events, self.counter = Inbox(), [], 0
        self.offer, self.draft = None, None
        self.max_attempts = max_attempts

    def new_id(self, prefix):
        self.counter += 1
        return f"{prefix}-{self.counter:03}"

    def record(self, decision, message=None, **extra):
        self.events.append({"seq": len(self.events) + 1, "decision": decision,
                            "message_id": message.get("message_id") if isinstance(message, dict) else None,
                            "owner": self.owner, "epoch": self.epoch, **extra})
        return decision

    def delegate(self, actor, snapshot_name, task_id="read-notes"):
        if actor != self.owner:
            raise PermissionError("only current owner may delegate")
        if self.offer is not None:
            raise ValueError("cannot delegate while a handoff is pending")
        if task_id in self.requests:
            if self.states[task_id] != "failed" or not self.failures[task_id]["retryable"]:
                raise ValueError("retry requires a retryable failure")
        attempt = self.requests.get(task_id, {}).get("attempt", 0) + 1
        if attempt > self.max_attempts:
            raise ValueError("attempt budget exhausted")
        snapshot = read_fixture(snapshot_name)
        request_id = self.new_id("request")
        request = {"protocol": 1, "message_id": request_id, "case_id": self.case_id,
                   "task_id": task_id, "correlation_id": request_id, "attempt": attempt,
                   "input_version": snapshot["version"], "epoch": self.epoch,
                   "from": actor, "to": "notes-reader", "kind": "delegate",
                   "payload": {"task": deepcopy(self.task), "snapshot_file": snapshot_name,
                               "return_fields": ["path", "required", "found", "missing", "evidence"]}}
        self.requests[task_id] = deepcopy(request)
        self.states[task_id] = "pending"
        self.failures.pop(task_id, None)
        self.results.pop(task_id, None)
        self.record("delegated", request, attempt=attempt)
        return request

    def response(self, request, kind, payload):
        return {"protocol": 1, "message_id": self.new_id("message"),
                "case_id": request["case_id"], "task_id": request["task_id"],
                "correlation_id": request["correlation_id"], "attempt": request["attempt"],
                "input_version": request["input_version"], "epoch": request["epoch"],
                "from": request["to"], "to": request["from"], "kind": kind,
                "payload": deepcopy(payload)}

    def receive(self, message):
        required = {"protocol", "message_id", "case_id", "task_id", "correlation_id", "attempt",
                    "input_version", "epoch", "from", "to", "kind", "payload"}
        if not isinstance(message, dict) or set(message) != required or type(message["protocol"]) is not int or message["protocol"] != 1:
            return self.record("malformed_message", message)
        if not all(isinstance(message[key], str) and message[key]
                   for key in ("message_id", "case_id", "task_id", "correlation_id",
                               "input_version", "from", "to", "kind")):
            return self.record("malformed_message", message)
        if (type(message["attempt"]) is not int or message["attempt"] < 1
                or type(message["epoch"]) is not int or message["epoch"] < 1
                or not isinstance(message["payload"], dict)):
            return self.record("malformed_message", message)
        status = self.inbox.register(message)
        if status != "new":
            return self.record(status, message)
        if message["case_id"] != self.case_id:
            return self.record("wrong_case", message)
        if message["epoch"] != self.epoch:
            return self.record("stale_owner", message)
        request = self.requests.get(message["task_id"])
        if request is None:
            return self.record("unknown_task", message)
        if message["from"] != request["to"] or message["to"] != request["from"]:
            return self.record("wrong_participant", message)
        if message["attempt"] != request["attempt"]:
            return self.record("stale_attempt", message)
        if message["input_version"] != request["input_version"]:
            return self.record("stale_input", message)
        if message["correlation_id"] != request["correlation_id"]:
            return self.record("wrong_correlation", message)
        task_id, kind, payload = message["task_id"], message["kind"], message["payload"]
        state = self.states[task_id]
        if state in {"completed", "failed"}:
            if kind == "started":
                return self.record("late_progress", message)
            known = self.results.get(task_id) if kind == "result" else self.failures.get(task_id)
            return self.record("duplicate_outcome" if payload == known else "conflicting_outcome", message)
        if kind == "started":
            self.states[task_id] = "running"
            return self.record("accepted_started", message)
        if kind == "failure":
            if (set(payload) != {"code", "retryable", "message", "evidence"}
                    or type(payload["retryable"]) is not bool
                    or not all(isinstance(payload[key], str) and payload[key] for key in ("code", "message"))
                    or not isinstance(payload["evidence"], dict)):
                return self.record("invalid_failure", message)
            self.states[task_id] = "failed"
            self.failures[task_id] = deepcopy(payload)
            return self.record("accepted_failure", message)
        if kind == "result":
            snapshot = read_fixture(request["payload"]["snapshot_file"])
            if snapshot["version"] != request["input_version"]:
                return self.record("stale_input", message)
            if snapshot["status"] != "ready":
                return self.record("invalid_evidence", message)
            expected = check_notes(request["payload"]["task"], snapshot)
            expected["evidence"]["file"] = request["payload"]["snapshot_file"]
            if payload != expected:
                return self.record("invalid_evidence", message)
            self.states[task_id] = "completed"
            self.results[task_id] = deepcopy(payload)
            return self.record("accepted_result", message)
        return self.record("unknown_kind", message)

    def merge(self, expected_tasks):
        unknown = set(self.results) - set(expected_tasks)
        if unknown:
            raise ValueError(f"unexpected task results: {sorted(unknown)}")
        missing = sorted(set(expected_tasks) - self.results.keys())
        return {"complete": not missing, "missing_tasks": missing,
                "results": deepcopy(self.results)}

    def offer_handoff(self, actor, target):
        if actor != self.owner:
            raise PermissionError("only current owner may offer handoff")
        if any(state in {"pending", "running"} for state in self.states.values()):
            raise ValueError("wait for delegated tasks before handoff")
        if not self.merge(["read-notes"])["complete"]:
            raise ValueError("handoff requires accepted facts evidence")
        if self.offer is not None:
            raise ValueError("a handoff is already pending")
        if target == self.owner or target != "report-writer":
            raise ValueError("target is not the configured successor")
        policy = read_fixture("policy.json")
        self.offer = {"handoff_id": self.new_id("handoff"), "case_id": self.case_id,
                      "from": actor, "to": target, "epoch": self.epoch,
                      "context": {"goal": self.task["instruction"],
                                  "task": deepcopy(self.task), "evidence": deepcopy(self.results),
                                  "decisions": ["已读取笔记；错误重试尚无完成记录"],
                                  "unresolved": ["错误重试是否完成"],
                                  "next_action": policy["next_action"],
                                  "allowed_actions": policy["allowed_actions"],
                                  "constraints": policy["constraints"]}}
        self.record("handoff_offered", handoff_id=self.offer["handoff_id"])
        return deepcopy(self.offer)

    def accept_handoff(self, actor, handoff_id, epoch):
        offer = self.offer
        if (offer is None or actor != offer["to"] or handoff_id != offer["handoff_id"]
                or epoch != self.epoch or epoch != offer["epoch"]):
            return self.record("rejected_handoff")
        self.owner = actor
        self.epoch += 1
        self.offer = None
        self.record("handoff_accepted", handoff_id=handoff_id)
        return "handoff_accepted"

    def act(self, actor, epoch, action):
        if actor != self.owner or epoch != self.epoch:
            return self.record("rejected_stale_owner", actor=actor)
        policy = read_fixture("policy.json")
        if action not in policy["allowed_actions"]:
            return self.record("rejected_action", actor=actor)
        evidence = self.results.get("read-notes")
        if evidence is None:
            return self.record("missing_evidence", actor=actor)
        text = evidence["evidence"]["text"]
        missing = [fact for fact in self.task["required_facts"] if fact not in text]
        self.draft = (f"任务 {self.case_id} 要求 {evidence['required']} 条事实，"
                      f"已找到 {evidence['found']} 条，缺少 {evidence['missing']} 条。\n"
                      + text + "待确认：" + ("、".join(missing) if missing else "无") + "。")
        return self.record("draft_created", actor=actor)


async def notes_worker(case, request, bus):
    # One lock protects check + execute + cache from simultaneous duplicate delivery.
    async with bus.worker_lock:
        status = bus.worker_inbox.register(request)
        if status == "conflicting_message":
            raise ValueError("request id reused with different content")
        if status == "duplicate":
            response = deepcopy(bus.worker_cache[request["message_id"]])
            await bus.send(response)
            return response
        bus.worker_executions += 1
        await bus.send(case.response(request, "started", {}))
        document = read_fixture(request["payload"]["snapshot_file"])
        if document["version"] != request["input_version"]:
            response = case.response(request, "failure", {
                "code": "input_version_changed", "retryable": True,
                "message": "笔记内容快照版本已改变，需要重新委派",
                "evidence": {"file": request["payload"]["snapshot_file"],
                             "expected_version": request["input_version"], "actual_version": document["version"]}})
        elif document["status"] != "ready":
            response = case.response(request, "failure", {
                "code": "snapshot_unfound", "retryable": True,
                "message": document["reason"],
                "evidence": {"file": request["payload"]["snapshot_file"], "version": document["version"]}})
        else:
            payload = check_notes(request["payload"]["task"], document)
            payload["evidence"]["file"] = request["payload"]["snapshot_file"]
            response = case.response(request, "result", payload)
        bus.worker_cache[request["message_id"]] = deepcopy(response)
        await bus.send(response)
        return response


async def exchange(case, request, bus):
    await bus.send(request)
    delivered = await bus.receive("notes-reader")
    result = await notes_worker(case, delivered, bus)
    decisions = [case.receive(await bus.receive(request["from"])) for _ in range(2)]
    return result, decisions


def save_run(output, case, bus, extra=None):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    result = {"owner": case.owner, "epoch": case.epoch, "states": case.states,
              "merged": case.merge(["read-notes"]), "draft": case.draft,
              "decisions": case.events, "worker_executions": bus.worker_executions, **(extra or {})}
    (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "messages.jsonl").write_text("".join(canonical(message) + "\n" for message in bus.wire), encoding="utf-8")
    (output / "input.json").write_text(json.dumps({name: read_fixture(name) for name in
        ("task.json", "snapshot-unfound.json", "snapshot-ready.json", "policy.json")},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "draft.md").write_text("# 笔记报告\n\n" + (case.draft or "尚未生成处理草稿。") + "\n", encoding="utf-8")
    lines = ["# 笔记任务通信记录", "", f"负责人：{case.owner}；epoch：{case.epoch}。", "",
             "| 顺序 | 消息 | 接收决定 |", "|---:|---|---|"]
    lines.extend(f"| {event['seq']} | {event['message_id'] or '—'} | {event['decision']} |" for event in case.events)
    lines += ["", "## 笔记摘要", "", case.draft or "尚未生成。"]
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result
