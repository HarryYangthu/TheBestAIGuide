"""模拟外部服务：独立 SQLite 数据库，幂等键与业务效果同事务。"""
import json, sqlite3

def operation_key(run_id, step_id):
    return json.dumps([run_id,step_id], ensure_ascii=False,separators=(",", ":"))

class LocalLedger:
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS charges (key TEXT PRIMARY KEY, amount INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS refunds (key TEXT PRIMARY KEY, amount INTEGER NOT NULL);
        """)

    def close(self): self.db.close()

    def charge(self, key, amount):
        if type(amount) is not int or amount <= 0: raise ValueError("positive integer amount required")
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO charges VALUES(?,?)",(key,amount))
            old=self.db.execute("SELECT amount FROM charges WHERE key=?",(key,)).fetchone()[0]
            if old != amount: raise ValueError("idempotency key reused with different payload")
        return {"key":key,"amount":amount}

    def refund(self,key):
        with self.db:
            row=self.db.execute("SELECT amount FROM charges WHERE key=?",(key,)).fetchone()
            if row is None: raise ValueError("unknown charge")
            self.db.execute("INSERT OR IGNORE INTO refunds VALUES(?,?)",(key,row[0]))
        return {"key":key,"refunded":row[0]}

    def snapshot(self):
        charges=self.db.execute("SELECT COALESCE(SUM(amount),0),COUNT(*) FROM charges").fetchone()
        refunds=self.db.execute("SELECT COALESCE(SUM(amount),0),COUNT(*) FROM refunds").fetchone()
        return {"charged":charges[0],"charge_count":charges[1],"refunded":refunds[0],
                "refund_count":refunds[1],"net":charges[0]-refunds[0]}

def replay(events):
    """只归约已记录的事实；不访问工具、不执行生成代码。"""
    state={}
    for event in events:
        step=state.setdefault(event["step_id"],{})
        if event["event"]=="prepared": step.update(status="pending",amount=event["payload"]["amount"])
        elif event["event"]=="completed": step.update(status="completed",result=event["payload"])
        elif event["event"]=="compensated": step.update(status="compensated",compensation=event["payload"])
    return state
