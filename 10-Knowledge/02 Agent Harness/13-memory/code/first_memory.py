"""The smallest complete write-close-reopen memory example."""
import sqlite3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "runs/first/memory.sqlite3"
path.parent.mkdir(parents=True, exist_ok=True)
db = sqlite3.connect(path)
db.execute("CREATE TABLE IF NOT EXISTS facts (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
db.execute("INSERT OR REPLACE INTO facts VALUES (?,?)", ("timeout_ms", "3000"))
db.commit()
db.close()
next_session = sqlite3.connect(path)
print(next_session.execute("SELECT value FROM facts WHERE key=?", ("timeout_ms",)).fetchone()[0])
next_session.close()
print("artifacts=runs/first/memory.sqlite3")
