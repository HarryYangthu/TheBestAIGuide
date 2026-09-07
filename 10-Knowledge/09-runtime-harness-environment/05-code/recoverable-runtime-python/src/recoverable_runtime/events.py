"""单写者教学事件库。每次调用独立提交，Checkpoint 和完成事件同事务。"""
import json, sqlite3

class EventStore:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS steps (
          run_id TEXT, step_id TEXT, amount INTEGER, status TEXT, result TEXT,
          PRIMARY KEY(run_id,step_id));
        CREATE TABLE IF NOT EXISTS events (
          seq INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT,step_id TEXT,event TEXT,payload TEXT);
        """)

    def close(self): self.db.close()

    def step(self, run_id, step_id):
        row = self.db.execute("SELECT amount,status,result FROM steps WHERE run_id=? AND step_id=?",
                              (run_id, step_id)).fetchone()
        return None if row is None else {"amount": row[0], "status": row[1], "result": json.loads(row[2]) if row[2] else None}

    def _append(self, run_id, step_id, event, payload):
        self.db.execute("INSERT INTO events(run_id,step_id,event,payload) VALUES (?,?,?,?)",
                        (run_id,step_id,event,json.dumps(payload,sort_keys=True)))

    def prepare(self, run_id, step_id, amount):
        prior = self.step(run_id,step_id)
        if prior:
            if prior["amount"] != amount: raise ValueError("step key reused with different amount")
            return prior
        with self.db:
            self.db.execute("INSERT INTO steps VALUES(?,?,?,'pending',NULL)",(run_id,step_id,amount))
            self._append(run_id,step_id,"prepared",{"amount": amount})
        return self.step(run_id,step_id)

    def append(self, run_id, step_id, event, payload):
        with self.db: self._append(run_id,step_id,event,payload)

    def finish(self, run_id, step_id, result):
        with self.db:
            self.db.execute("UPDATE steps SET status='completed',result=? WHERE run_id=? AND step_id=?",
                            (json.dumps(result,sort_keys=True),run_id,step_id))
            self._append(run_id,step_id,"completed",result)

    def compensated(self, run_id, step_id, receipt):
        with self.db:
            self.db.execute("UPDATE steps SET status='compensated' WHERE run_id=? AND step_id=?",(run_id,step_id))
            self._append(run_id,step_id,"compensated",receipt)

    def events(self, run_id):
        return [{"seq":r[0],"step_id":r[1],"event":r[2],"payload":json.loads(r[3])}
                for r in self.db.execute("SELECT seq,step_id,event,payload FROM events WHERE run_id=? ORDER BY seq",(run_id,))]
