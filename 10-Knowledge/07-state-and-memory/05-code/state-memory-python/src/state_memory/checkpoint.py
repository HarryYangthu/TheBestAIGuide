import json
import sqlite3
from .state import VersionConflict


class CheckpointStore:
    """SQLite snapshots with compare-and-swap, not an external side-effect log."""
    def __init__(self, path: str):
        self.db = sqlite3.connect(path, isolation_level=None, timeout=5)
        self.db.execute("CREATE TABLE IF NOT EXISTS checkpoints (run_id TEXT, version INTEGER, state TEXT NOT NULL, PRIMARY KEY(run_id,version))")

    def save(self, run_id: str, state: dict, expected_version: int = 0) -> int:
        if not run_id or not isinstance(state, dict) or expected_version < 0:
            raise ValueError("run_id, object state and nonnegative version required")
        payload = json.dumps(state, ensure_ascii=False, allow_nan=False)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            current = self.db.execute("SELECT COALESCE(MAX(version),0) FROM checkpoints WHERE run_id=?", (run_id,)).fetchone()[0]
            if current != expected_version:
                raise VersionConflict(f"expected {expected_version}, actual {current}")
            version = current + 1
            self.db.execute("INSERT INTO checkpoints VALUES (?,?,?)", (run_id, version, payload))
            self.db.execute("COMMIT")
            return version
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def load(self, run_id: str) -> tuple[int, dict]:
        row = self.db.execute("SELECT version,state FROM checkpoints WHERE run_id=? ORDER BY version DESC LIMIT 1", (run_id,)).fetchone()
        if row is None:
            return 0, {}
        return row[0], json.loads(row[1])

    def close(self) -> None:
        self.db.close()
