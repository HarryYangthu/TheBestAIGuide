"""Single-runner durable batch processing with an independently committed recipient."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time

ROOT = Path(__file__).resolve().parents[1]


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def connect(path):
    db = sqlite3.connect(path, isolation_level=None, timeout=5)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA synchronous=FULL")
    return db


@contextmanager
def transaction(db):
    db.execute("BEGIN IMMEDIATE")
    try:
        yield
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise


def event(db, kind, detail):
    db.execute("INSERT INTO events(kind,detail) VALUES (?,?)", (kind, canonical(detail)))


class Recipient:
    """Local report inbox. Effect and idempotency record are the SAME transaction."""
    def __init__(self, path):
        self.db = connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS publications (op_key TEXT PRIMARY KEY, request_hash TEXT NOT NULL, payload TEXT NOT NULL, receipt TEXT NOT NULL)")

    def lookup(self, key):
        row = self.db.execute("SELECT * FROM publications WHERE op_key=?", (key,)).fetchone()
        return dict(row) if row else None

    def publish(self, key, payload):
        request_hash = digest(canonical(payload).encode())
        with transaction(self.db):
            previous = self.lookup(key)
            if previous:
                if previous["request_hash"] != request_hash:
                    raise ValueError("idempotency key reused with changed payload")
                return json.loads(previous["receipt"])
            receipt = {"publication_id": digest(key.encode())[:16], "request_hash": request_hash}
            self.db.execute("INSERT INTO publications VALUES (?,?,?,?)",
                            (key, request_hash, canonical(payload), canonical(receipt)))
            return receipt

    def close(self):
        self.db.close()


def init(root, inputs=ROOT / "fixtures/batches.json", run_id="batch-1", scope="tenant-a/reports/v1", max_attempts=3, ttl=None):
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    raw = Path(inputs).read_bytes()
    batches = json.loads(raw)
    if not batches or any(not item["values"] for item in batches):
        raise ValueError("batches must contain nonempty values")
    (root / "input.json").write_bytes(raw)
    config = {"schema_version": 1, "run_id": run_id, "scope": scope,
              "input_sha256": digest(raw), "code_sha256": digest(Path(__file__).read_bytes()),
              "max_attempts": max_attempts, "expires_at": None if ttl is None else time.time() + ttl}
    db = connect(root / "runtime.sqlite")
    db.executescript("""
    CREATE TABLE task (id INTEGER PRIMARY KEY CHECK(id=1), config TEXT NOT NULL,
                       status TEXT NOT NULL, next_index INTEGER NOT NULL, cancel_requested INTEGER NOT NULL);
    CREATE TABLE results (item_index INTEGER PRIMARY KEY, item_id TEXT NOT NULL, mean REAL NOT NULL);
    CREATE TABLE operation (id INTEGER PRIMARY KEY CHECK(id=1), op_key TEXT NOT NULL, payload TEXT NOT NULL,
                           status TEXT NOT NULL, attempts INTEGER NOT NULL, receipt TEXT);
    CREATE TABLE events (seq INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, detail TEXT NOT NULL);
    """)
    with transaction(db):
        db.execute("INSERT INTO task VALUES (1,?,'running',0,0)", (canonical(config),))
        event(db, "created", {"run_id": run_id})
    db.close()
    Recipient(root / "recipient.sqlite").close()


def checkpoint_item(db, index, item):
    value = sum(item["values"]) / len(item["values"])
    with transaction(db):
        db.execute("INSERT INTO results VALUES (?,?,?)", (index, item["id"], value))
        db.execute("UPDATE task SET next_index=? WHERE id=1", (index + 1,))
        event(db, "item_completed", {"index": index, "mean": value})


def request_cancel(root):
    db = connect(Path(root) / "runtime.sqlite")
    with transaction(db):
        db.execute("UPDATE task SET cancel_requested=1 WHERE id=1")
        event(db, "cancel_requested", {})
    db.close()


def task_row(db):
    return dict(db.execute("SELECT * FROM task WHERE id=1").fetchone())


def finish_status(db, status):
    with transaction(db):
        db.execute("UPDATE task SET status=? WHERE id=1", (status,))
        event(db, status, {})


def save_receipt(db, receipt):
    with transaction(db):
        db.execute("UPDATE operation SET status='confirmed',receipt=? WHERE id=1", (canonical(receipt),))
        event(db, "receipt_saved", receipt)


def validate(root, config):
    if config["schema_version"] != 1:
        raise ValueError("unsupported checkpoint schema")
    if digest((root / "input.json").read_bytes()) != config["input_sha256"]:
        raise ValueError("input changed since checkpoint")
    if digest(Path(__file__).read_bytes()) != config["code_sha256"]:
        raise ValueError("runtime code changed since checkpoint")


def boundary(db, recipient, config):
    """Cancellation/expiry may reconcile a receipt but never initiate publication."""
    task = task_row(db)
    cancelled = bool(task["cancel_requested"])
    expired = config["expires_at"] is not None and time.time() >= config["expires_at"]
    if not cancelled and not expired:
        return False
    op = db.execute("SELECT * FROM operation WHERE id=1").fetchone()
    if op and op["status"] == "inflight":
        found = recipient.lookup(op["op_key"])
        if found:
            save_receipt(db, json.loads(found["receipt"]))
    finish_status(db, "cancelled" if cancelled else "timed_out")
    return True


def crash_if(selected, point, code):
    if selected == point:
        os._exit(code)  # A real child-process exit; no finally or JSON export runs.


def run(root, crash=None, fail_until=0, hang_before_effect=False):
    root = Path(root)
    db, recipient = connect(root / "runtime.sqlite"), Recipient(root / "recipient.sqlite")
    try:
        task = task_row(db)
        config = json.loads(task["config"])
        validate(root, config)
        if task["status"] in {"completed", "cancelled", "timed_out", "failed"}:
            return inspect(root)
        batches = json.loads((root / "input.json").read_text())
        for index in range(task["next_index"], len(batches)):
            if boundary(db, recipient, config):
                return inspect(root)
            checkpoint_item(db, index, batches[index])
            if index == 0:
                crash_if(crash, "after_item", 71)
        if boundary(db, recipient, config):
            return inspect(root)
        op = db.execute("SELECT * FROM operation WHERE id=1").fetchone()
        if op is None:
            payload = [dict(row) for row in db.execute("SELECT * FROM results ORDER BY item_index")]
            key = canonical([config["scope"], config["run_id"], "publish", 1])
            with transaction(db):
                db.execute("INSERT INTO operation VALUES (1,?,?,'prepared',0,NULL)", (key, canonical(payload)))
                event(db, "prepared", {"op_key": key})
            crash_if(crash, "after_prepare", 70)
        while True:
            if boundary(db, recipient, config):
                return inspect(root)
            op = dict(db.execute("SELECT * FROM operation WHERE id=1").fetchone())
            if op["status"] == "confirmed":
                finish_status(db, "completed")
                return inspect(root)
            if op["status"] == "inflight":
                # Previous runner is dead before restart. Lookup is authoritative for this local recipient.
                found = recipient.lookup(op["op_key"])
                if found:
                    if found["request_hash"] != digest(op["payload"].encode()):
                        raise ValueError("recipient payload mismatch")
                    save_receipt(db, json.loads(found["receipt"]))
                    continue
            if op["attempts"] >= config["max_attempts"]:
                finish_status(db, "failed")
                return inspect(root)
            with transaction(db):
                db.execute("UPDATE operation SET status='inflight',attempts=attempts+1 WHERE id=1")
                event(db, "attempt", {"number": op["attempts"] + 1})
            if hang_before_effect:
                (root / "ready").write_text("inflight\n")
                time.sleep(60)
            attempt = op["attempts"] + 1
            if attempt <= fail_until:
                # Explicit fault injection: known failure BEFORE recipient invocation.
                with transaction(db):
                    db.execute("UPDATE operation SET status='retryable' WHERE id=1")
                    event(db, "transient_failure", {"attempt": attempt})
                if attempt < config["max_attempts"]:
                    time.sleep(min(0.01 * 2 ** (attempt - 1), 0.1))
                continue
            receipt = recipient.publish(op["op_key"], json.loads(op["payload"]))
            crash_if(crash, "after_effect", 72)
            save_receipt(db, receipt)
            crash_if(crash, "after_receipt", 73)
    finally:
        db.close()
        recipient.close()


def inspect(root):
    root = Path(root)
    db = connect(root / "runtime.sqlite")
    recipient = Recipient(root / "recipient.sqlite")
    try:
        task = task_row(db)
        op = db.execute("SELECT * FROM operation WHERE id=1").fetchone()
        results = [dict(row) for row in db.execute("SELECT * FROM results ORDER BY item_index")]
        publications = [dict(row) for row in recipient.db.execute("SELECT * FROM publications ORDER BY op_key")]
        events = [dict(row) for row in db.execute("SELECT * FROM events ORDER BY seq")]
        config = json.loads(task["config"])
        identities_match = (config["schema_version"] == 1
                            and digest((root / "input.json").read_bytes()) == config["input_sha256"]
                            and digest(Path(__file__).read_bytes()) == config["code_sha256"])
        batches = json.loads((root / "input.json").read_text())
        expected = [{"item_index": i, "item_id": item["id"], "mean": sum(item["values"]) / len(item["values"])}
                    for i, item in enumerate(batches)]
        passed = (identities_match and task["status"] == "completed" and results == expected and len(publications) == 1
                  and json.loads(publications[0]["payload"]) == expected and op is not None
                  and op["status"] == "confirmed" and op["receipt"] == publications[0]["receipt"])
        result = {"status": task["status"], "next_index": task["next_index"],
                  "operation_status": op["status"] if op else None,
                  "attempts": op["attempts"] if op else 0, "effect_count": len(publications),
                  "item_commits": sum(e["kind"] == "item_completed" for e in events), "acceptance": passed}
        (root / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        (root / "checkpoint.json").write_text(json.dumps({"task": task, "operation": dict(op) if op else None,
                                                           "results": results}, indent=2, sort_keys=True) + "\n")
        (root / "trace.jsonl").write_text("".join(json.dumps(e, sort_keys=True) + "\n" for e in events))
        (root / "publications.json").write_text(json.dumps(publications, indent=2, sort_keys=True) + "\n")
        lines = ["# 持久化与故障恢复", "", "| 字段 | 实际值 |", "|---|---|"]
        lines += [f"| {k} | `{v}` |" for k, v in result.items()]
        (root / "report.md").write_text("\n".join(lines) + "\n")
        return result
    finally:
        db.close()
        recipient.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "run", "cancel", "inspect"])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--crash", choices=["after_item", "after_prepare", "after_effect", "after_receipt"])
    parser.add_argument("--fail-until", type=int, default=0)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--ttl", type=float)
    parser.add_argument("--hang-before-effect", action="store_true")
    args = parser.parse_args()
    if args.action == "init":
        init(args.root, max_attempts=args.max_attempts, ttl=args.ttl)
        print("initialized")
    elif args.action == "cancel":
        request_cancel(args.root)
        print("cancel_requested")
    else:
        result = inspect(args.root) if args.action == "inspect" else run(
            args.root, args.crash, args.fail_until, args.hang_before_effect)
        print(canonical(result))
