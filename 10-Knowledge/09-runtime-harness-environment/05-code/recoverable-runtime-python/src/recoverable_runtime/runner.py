from .recovery import operation_key, replay

class InjectedCrash(RuntimeError): pass

class Runner:
    """同步、单写者示例；store 和 ledger 独立，故意保留跨系统提交窗口。"""
    def __init__(self,store,ledger): self.store,self.ledger=store,ledger

    def execute(self,run_id,step_id,amount,crash_at=None):
        if not run_id or not step_id or type(amount) is not int or amount<=0:
            raise ValueError("nonempty IDs and positive integer amount required")
        if crash_at not in {None,"before_effect","after_effect","after_checkpoint"}:
            raise ValueError("unknown crash point")
        saved=self.store.prepare(run_id,step_id,amount)
        if saved["status"]=="compensated": raise ValueError("compensated step cannot be executed again")
        if saved["status"]=="completed": return saved["result"]
        self.store.append(run_id,step_id,"attempt",{})
        if crash_at=="before_effect": raise InjectedCrash(crash_at)
        result=self.ledger.charge(operation_key(run_id,step_id),amount)
        if crash_at=="after_effect": raise InjectedCrash(crash_at)
        self.store.finish(run_id,step_id,result)
        if crash_at=="after_checkpoint": raise InjectedCrash(crash_at)
        return result

    def replay(self,run_id): return replay(self.store.events(run_id))

    def compensate(self,run_id,step_id,crash_after_refund=False):
        """补偿已确认动作；不是取消 API，不能用它阻止尚未发生的动作。"""
        saved=self.store.step(run_id,step_id)
        if saved is None or saved["status"]=="pending":
            raise ValueError("pending effect is unknown; execute resumes the action, not cancellation")
        if saved["status"]=="compensated": return self.ledger.snapshot()
        receipt=self.ledger.refund(operation_key(run_id,step_id))
        if crash_after_refund: raise InjectedCrash("after_refund")
        self.store.compensated(run_id,step_id,receipt)
        return self.ledger.snapshot()
