"""Versioned state, transition validation and atomic compare-and-swap."""
import json
import sqlite3
from pathlib import Path


class VersionConflict(Exception):
    pass


class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, isolation_level=None, timeout=5)
        self.db.execute("CREATE TABLE IF NOT EXISTS snapshots (version INTEGER PRIMARY KEY, state TEXT NOT NULL)")

    def load(self):
        row = self.db.execute("SELECT version,state FROM snapshots ORDER BY version DESC LIMIT 1").fetchone()
        return (row[0], json.loads(row[1])) if row else (0, None)

    def save(self, value, expected_version):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            actual, previous = self.load()
            if actual != expected_version:
                raise VersionConflict(f"expected={expected_version} actual={actual}")
            allowed = {None: {"queued"}, "queued": {"running"},
                       "running": {"running", "completed"}, "completed": {"running"}}
            old_status = previous["status"] if previous else None
            if value["status"] not in allowed[old_status]:
                raise ValueError("invalid transition")
            if value["schema_version"] != 1 or value["budget"] < 0:
                raise ValueError("invalid state")
            self.db.execute("INSERT INTO snapshots VALUES (?,?)",
                            (actual + 1, json.dumps(value, ensure_ascii=False, sort_keys=True)))
            self.db.execute("COMMIT")
            return actual + 1
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def close(self):
        self.db.close()


def initial():
    return {"schema_version": 1, "task_id": "repair-mean", "status": "queued",
            "next_step": "inspect", "budget": 4, "refs": {}, "acceptance": "not_run"}


def complete(state, artifacts):
    """Validate bytes and exact dependency versions before producing completed state."""
    refs = state["refs"]
    for ident in refs.values():
        artifacts.verify(ident)
    for name in ("code", "evidence", "experiment"):
        if artifacts.stale(refs[name], refs):
            raise ValueError(f"stale {name}")
    evidence = json.loads(artifacts.read(refs["evidence"]))
    experiment = json.loads(artifacts.read(refs["experiment"]))
    if not evidence["passed"] or not experiment["passed"]:
        raise ValueError("acceptance failed")
    result = dict(state, status="completed", next_step=None, acceptance="passed")
    return result
