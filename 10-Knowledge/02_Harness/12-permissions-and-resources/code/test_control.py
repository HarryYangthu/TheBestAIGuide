import asyncio
import tempfile
import unittest
from control import Approvals, Budget, Denied, Request, Runtime, principal


class ControlTests(unittest.IsolatedAsyncioTestCase):
    async def test_atomic_reservation(self):
        budget = Budget(units=10, cost_micros=30)
        async def attempt(name):
            try:
                await budget.reserve(name, 8, 24)
                return True
            except Denied:
                return False
        results = await asyncio.gather(attempt("A"), attempt("B"))
        self.assertEqual(sum(results), 1)
        self.assertEqual(budget.snapshot()["reserved_units"], 8)

    async def test_settlement_once_and_negative(self):
        budget = Budget()
        with self.assertRaises(Denied):
            await budget.reserve("bad", -1, 3)
        await budget.reserve("A", 8, 24)
        with self.assertRaises(Denied):
            await budget.settle("A", 9, 27)
        self.assertEqual(budget.snapshot()["reserved_units"], 8)
        await budget.settle("A", 3, 9)
        with self.assertRaises(Denied):
            await budget.settle("A", 3, 9)
        self.assertEqual(budget.spent_units, 3)

    async def test_cost_and_call_limits(self):
        budget = Budget(units=100, cost_micros=2)
        with self.assertRaises(Denied):
            await budget.reserve("A", 1, 3)
        budget = Budget(calls=1)
        await budget.reserve("A", 1, 3)
        await budget.settle("A", 0, 0)
        with self.assertRaises(Denied):
            await budget.reserve("B", 1, 3)

    async def test_unknown_stays_reserved(self):
        budget = Budget(units=10, cost_micros=30)
        await budget.reserve("A", 8, 24)
        await budget.mark_unknown("A")
        with self.assertRaises(Denied):
            await budget.reserve("B", 3, 9)
        await budget.settle("A", 2, 6)
        self.assertEqual(budget.snapshot()["unknown"], [])

    async def test_approval_binding_expiry_and_replay(self):
        approvals = Approvals([])
        actor, request = principal(), Request("r", "publish_record", "a1")
        payload = {"title": "笔记与统计检查结果", "checks_passed": 4}
        token = approvals.grant(actor, request, payload, source="test")
        with self.assertRaises(Denied):
            approvals.check(token, actor, Request("r", "publish_record", "b1"), payload)
        approvals.check(token, actor, request, payload, consume=True)
        with self.assertRaises(Denied):
            approvals.check(token, actor, request, payload)
        expired = approvals.grant(actor, request, payload, ttl=-1, source="test")
        with self.assertRaises(Denied):
            approvals.check(expired, actor, request, payload)

    async def test_approval_binds_content_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime, actor = Runtime(directory), principal()
            request = Request("publish", "publish_record", "a1")
            token = runtime.approvals.grant(actor, request, runtime.project(request), source="test")
            runtime.records["a1"]["checks_passed"] = 999
            result = await runtime.execute(actor, request, deadline=asyncio.get_running_loop().time() + 2, token=token)
            self.assertEqual(result["status"], "approval_mismatch")
            self.assertFalse((runtime.output / "a1.json").exists())
            self.assertEqual(runtime.budget.calls, 0)

    async def test_approval_binds_content_at_write(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime, actor = Runtime(directory), principal()
            request = Request("publish", "publish_record", "a1", delay_ms=20)
            token = runtime.approvals.grant(actor, request, runtime.project(request), source="test")
            task = asyncio.create_task(runtime.execute(actor, request, deadline=asyncio.get_running_loop().time() + 2, token=token))
            while runtime.active == 0:
                await asyncio.sleep(0)
            runtime.records["a1"]["checks_passed"] = 999
            result = await task
            self.assertEqual(result["status"], "approval_content_changed")
            self.assertFalse((runtime.output / "a1.json").exists())
            self.assertEqual(runtime.active, 0)
            self.assertEqual(runtime.budget.snapshot()["reserved_units"], 0)

    async def test_data_scope_and_projection(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = Runtime(directory)
            deadline = asyncio.get_running_loop().time() + 2
            denied = await runtime.execute(principal(), Request("b", "read_record", "b1"), deadline=deadline)
            allowed = await runtime.execute(principal(), Request("a", "read_record", "a1"), deadline=deadline)
            self.assertEqual(denied["status"], "resource_denied")
            self.assertNotIn("private_note", allowed["data"])
            self.assertEqual(runtime.budget.calls, 1)

    async def test_deadline_includes_queue(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = Runtime(directory, concurrency=1)
            await runtime.semaphore.acquire()
            result = await runtime.execute(principal(), Request("r", "read_record", "a1"), deadline=asyncio.get_running_loop().time() + 0.01)
            runtime.semaphore.release()
            self.assertEqual(result["status"], "deadline_exceeded")
            self.assertEqual(runtime.budget.calls, 0)

    async def test_cancellation_after_partial_work_settles(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = Runtime(directory, concurrency=1)
            task = asyncio.create_task(runtime.execute(principal(), Request("r", "read_record", "a1", steps=10, delay_ms=10), deadline=asyncio.get_running_loop().time() + 2))
            await asyncio.sleep(0.035)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
            self.assertGreater(runtime.budget.spent_units, 0)
            self.assertLess(runtime.budget.spent_units, 10)
            self.assertEqual(runtime.active, 0)
            self.assertEqual(runtime.budget.snapshot()["reserved_units"], 0)


if __name__ == "__main__":
    unittest.main()
