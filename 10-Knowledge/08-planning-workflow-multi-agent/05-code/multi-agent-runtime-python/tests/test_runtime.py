import asyncio, unittest
from multi_agent import Task, Router, Supervisor, WorkerResult, merge_results, MergeConflict
from multi_agent.fixture import experiment, CANDIDATES, deterministic_baseline

class RuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_baselines_and_concurrency(self):
        result = await experiment()
        self.assertEqual([x["selected"] for x in result["rows"]], ["A", "A", "A"])
        self.assertEqual([x["max_active"] for x in result["rows"][:2]], [1, 2])

    async def test_timeout_partial_failure_and_cleanup(self):
        stopped = asyncio.Event()
        async def slow(t):
            try: await asyncio.sleep(10)
            finally: stopped.set()
        async def good(t): return {"answer": 3}
        r = await Supervisor(Router({"slow": slow, "good": good})).run([
            Task("s", "slow", {}, ("answer",), .02), Task("g", "good", {}, ("answer",))])
        merged = merge_results(r.results)
        self.assertTrue(stopped.is_set())
        self.assertEqual(merged.values, {"answer": 3})
        self.assertFalse(merged.complete)
        self.assertEqual(merged.missing_tasks, ["s"])

    async def test_bad_route_contract_and_input_isolation(self):
        payload = {"nested": [1]}
        async def mutate(t):
            t.payload["nested"].append(2)
            return {"wrong": 0}
        result = await Supervisor(Router({"m": mutate})).run([
            Task("a", "m", payload, ("answer",)), Task("b", "missing", {}, ())])
        self.assertEqual(payload, {"nested": [1]})
        self.assertEqual([r.status for r in result.results], ["error", "error"])

    async def test_external_cancel_propagates(self):
        started, stopped = asyncio.Event(), asyncio.Event()
        async def worker(t):
            started.set()
            try: await asyncio.sleep(10)
            finally: stopped.set()
        supervisor = Supervisor(Router({"slow": worker}))
        parent = asyncio.create_task(supervisor.run([Task("a", "slow", {}, (), 20)]))
        await started.wait()
        parent.cancel()
        with self.assertRaises(asyncio.CancelledError): await parent
        self.assertTrue(stopped.is_set())
        self.assertEqual(supervisor.last_trace[-1]["event"], "cancelled")

    async def test_budget_rejected_before_start(self):
        with self.assertRaises(ValueError):
            await Supervisor(Router({}), max_tasks=1).run([Task("a", "x", {}, ()),Task("b", "x", {}, ())])

    def test_conflict_not_last_write_wins(self):
        with self.assertRaises(MergeConflict):
            merge_results([WorkerResult("a", "ok", {"decision": "A"}), WorkerResult("b", "ok", {"decision": "B"})])
        merged = merge_results([WorkerResult("a", "ok", {"x": 2}), WorkerResult("b", "ok", {"x": 2})])
        self.assertEqual(merged.owners["x"], ["a", "b"])

if __name__ == "__main__": unittest.main()
