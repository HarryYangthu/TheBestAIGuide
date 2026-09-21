"""Evidence-backed persistent memory for repeated checkout release reviews."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_fixture(name):
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def evidence_check(record, sources):
    source = sources.get(record["source_id"])
    if not source:
        return False
    # A recorded reviewer decision plus exact scope and assertion matching is
    # required. A source id, confidence score or recent timestamp alone is not proof.
    assertion_fields = ("kind", "key", "value", "service", "environment", "user", "conditions", "valid_from", "expires_at")
    return source.get("reviewed") is True and all(
        type(record[k]) is type(source[k]) and record[k] == source[k] for k in assertion_fields)


class MemoryStore:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY, key TEXT NOT NULL, kind TEXT NOT NULL,
            service TEXT NOT NULL, environment TEXT NOT NULL, user TEXT NOT NULL,
            status TEXT NOT NULL, body TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            seq INTEGER PRIMARY KEY, memory_id TEXT NOT NULL,
            action TEXT NOT NULL, detail TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS scope_idx ON memories(service, environment, user, status);
        """)

    def close(self):
        self.db.close()

    def rows(self):
        return [{**json.loads(row["body"]), "status": row["status"]}
                for row in self.db.execute("SELECT * FROM memories ORDER BY id")]

    def add(self, record, sources):
        start, end = date.fromisoformat(record["valid_from"]), date.fromisoformat(record["expires_at"])
        if end <= start:
            raise ValueError("expires_at must be later than valid_from")
        if record["kind"] not in {"fact", "preference", "procedure", "failure"}:
            raise ValueError("unknown kind")
        if record["kind"] == "failure" and not record["conditions"]:
            raise ValueError("failure memories require trigger conditions")
        if self.db.execute("SELECT 1 FROM memories WHERE id=?", (record["id"],)).fetchone():
            raise ValueError("memory id already exists; use a new id for a revision")
        verified = evidence_check(record, sources)
        source = sources.get(record["source_id"], {})
        record = {**record, "verified": bool(verified),
                  "source_sha256": hashlib.sha256(canonical(source).encode()).hexdigest()}
        status = "active" if verified else "candidate"
        same = list(self.db.execute(
            "SELECT * FROM memories WHERE key=? AND kind=? AND service=? AND environment=? AND user=? AND status IN ('active','disputed')",
            tuple(record[k] for k in ("key", "kind", "service", "environment", "user"))))
        supersedes = record.get("supersedes", [])
        if supersedes and not verified:
            raise ValueError("unverified record cannot supersede memory")
        if set(supersedes) - {r["id"] for r in same}:
            raise ValueError("supersedes must name existing records with the same scope and key")
        different = [r for r in same if json.loads(r["body"])["value"] != record["value"]]
        unresolved = [r for r in different if r["id"] not in supersedes]
        # The transaction covers old-record status, new record and audit event.
        with self.db:
            if verified and unresolved:
                status = "disputed"
                for old in unresolved:
                    self.db.execute("UPDATE memories SET status='disputed' WHERE id=?", (old["id"],))
            if verified:
                for old_id in supersedes:
                    self.db.execute("UPDATE memories SET status='superseded' WHERE id=?", (old_id,))
            self.db.execute("INSERT INTO memories VALUES (?,?,?,?,?,?,?,?)",
                            (record["id"], record["key"], record["kind"], record["service"],
                             record["environment"], record["user"], status, canonical(record)))
            self.db.execute("INSERT INTO events(memory_id,action,detail) VALUES (?,?,?)",
                            (record["id"], "add", canonical({"status": status, "supersedes": supersedes})))
        return status

    def retrieve(self, task, sources=None):
        today = date.fromisoformat(task["as_of"])
        selected, excluded = [], []
        for record in self.rows():
            reason = None
            if (record["service"], record["environment"]) != (task["service"], task["environment"]):
                reason = "scope_mismatch"
            elif record["user"] not in {"*", task["user"]}:
                reason = "user_mismatch"
            elif record["status"] != "active":
                reason = record["status"]
            elif sources is not None and record["source_sha256"] != hashlib.sha256(canonical(sources.get(record["source_id"], {})).encode()).hexdigest():
                reason = "source_changed"
            elif today < date.fromisoformat(record["valid_from"]):
                reason = "not_yet_valid"
            elif today >= date.fromisoformat(record["expires_at"]):
                reason = "expired"
            elif task.get("requested_keys") is not None and record["key"] not in task["requested_keys"]:
                reason = "not_requested"
            elif record["kind"] == "preference" and record["key"] in task.get("current_instructions", {}):
                reason = "current_instruction_overrides"
            elif any(task.get("signals", {}).get(k) != v for k, v in record["conditions"].items()):
                reason = "trigger_not_met"
            if reason:
                excluded.append({"id": record["id"], "reason": reason})
            else:
                selected.append(record)
        # Explicitly requested keys use the current instruction; retrieved values
        # are evidence/advice, never promoted into system-level instructions.
        effective_preferences = {r["key"]: r["value"] for r in selected if r["kind"] == "preference"}
        effective_preferences.update(task.get("current_instructions", {}))
        return {"selected": selected, "excluded": excluded,
                "effective_preferences": effective_preferences}

    def expire(self, as_of):
        ids = [r["id"] for r in self.rows() if r["status"] in {"active", "disputed"}
               and date.fromisoformat(r["expires_at"]) <= date.fromisoformat(as_of)]
        with self.db:
            for memory_id in ids:
                self.db.execute("UPDATE memories SET status='expired' WHERE id=?", (memory_id,))
                self.db.execute("INSERT INTO events(memory_id,action,detail) VALUES (?,?,?)",
                                (memory_id, "expire", as_of))
        return ids

    def forget(self, memory_id):
        # Physical payload deletion; the audit row retains only id/action.
        with self.db:
            self.db.execute("DELETE FROM memories WHERE id=?", (memory_id,))
            self.db.execute("DELETE FROM events WHERE memory_id=?", (memory_id,))
            self.db.execute("INSERT INTO events(memory_id,action,detail) VALUES (?,?,?)",
                            (memory_id, "forget", "payload_deleted"))


def render_context(result):
    return {
        "current_preferences": result["effective_preferences"],
        "retrieved_evidence": [{"id": r["id"], "kind": r["kind"], "key": r["key"],
                                "value": r["value"], "source_id": r["source_id"],
                                "expires_at": r["expires_at"]} for r in result["selected"]],
    }
