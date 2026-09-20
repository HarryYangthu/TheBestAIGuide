"""Scoped factual memory; caller supplies trusted subject and explicit clock."""
from dataclasses import dataclass
import json
import math
import sqlite3
from typing import Any
from .state import MemoryConflict


@dataclass(frozen=True)
class Memory:
    subject: str
    key: str
    value: Any
    source: str
    updated_at: float
    expires_at: float | None
    version: int


class MemoryStore:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path, isolation_level=None, timeout=5)
        self.db.execute("""CREATE TABLE IF NOT EXISTS memories (
            subject TEXT, key TEXT, value TEXT, source TEXT, updated_at REAL,
            expires_at REAL, version INTEGER, deleted INTEGER DEFAULT 0,
            PRIMARY KEY(subject,key))""")

    @staticmethod
    def _clock(now: float) -> None:
        if not isinstance(now, (float, int)) or not math.isfinite(now):
            raise ValueError("now must be a finite timestamp")

    def put(self, subject: str, key: str, value: Any, source: str, now: float,
            ttl: float | None = None, expected_version: int | None = None) -> Memory:
        self._clock(now)
        if not subject or not key or not source:
            raise ValueError("subject, key and source are required")
        if ttl is not None and (not math.isfinite(ttl) or ttl <= 0):
            raise ValueError("ttl must be positive and finite")
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False)
        expiry = now + ttl if ttl is not None else None
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute("SELECT version,updated_at FROM memories WHERE subject=? AND key=?", (subject, key)).fetchone()
            version = row[0] if row else 0
            expected = 0 if expected_version is None else expected_version
            if version != expected:
                raise MemoryConflict(f"expected {expected}, actual {version}")
            if row and now < row[1]:
                raise ValueError("a stale timestamp cannot overwrite a newer fact")
            record = (subject, key, encoded, source, now, expiry, version + 1, 0)
            self.db.execute("INSERT OR REPLACE INTO memories VALUES (?,?,?,?,?,?,?,?)", record)
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        return Memory(subject, key, value, source, now, expiry, version + 1)

    @staticmethod
    def _decode(row) -> Memory:
        return Memory(row[0], row[1], json.loads(row[2]), row[3], row[4], row[5], row[6])

    def get(self, subject: str, key: str, now: float) -> Memory | None:
        self._clock(now)
        row = self.db.execute("SELECT * FROM memories WHERE subject=? AND key=? AND deleted=0 AND (expires_at IS NULL OR expires_at>?)", (subject, key, now)).fetchone()
        return self._decode(row) if row else None

    def retrieve(self, subject: str, query: str, now: float, limit: int = 5) -> list[Memory]:
        """Hard subject/expiry filters, then simple key/value substring relevance."""
        self._clock(now)
        if limit < 0:
            raise ValueError("limit cannot be negative")
        rows = self.db.execute("SELECT * FROM memories WHERE subject=? AND deleted=0 AND (expires_at IS NULL OR expires_at>?) ORDER BY updated_at DESC, key", (subject, now)).fetchall()
        matches = [self._decode(r) for r in rows if query.casefold() in (r[1] + " " + r[2]).casefold()]
        return matches[:limit]

    def forget(self, subject: str, key: str) -> bool:
        # Retain key/version tombstone to prevent stale writes resurrecting data.
        # Deleted content/source are cleared; DB backups require separate retention.
        result = self.db.execute("UPDATE memories SET value=NULL,source=NULL,deleted=1,version=version+1 WHERE subject=? AND key=? AND deleted=0", (subject, key))
        return result.rowcount > 0

    def close(self) -> None:
        self.db.close()
