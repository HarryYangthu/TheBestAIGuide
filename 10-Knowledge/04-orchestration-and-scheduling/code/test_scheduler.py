import asyncio
from collections import Counter
from dataclasses import replace
from graphlib import CycleError
import unittest
from order_workflow import OrderWorker, load_inputs, make_plan
from scheduler import Node, Role, Scheduler


class SchedulerTests(unittest.IsolatedAsyncioTestCase):
    async def test_child_self_cancel_is_not_parent_cancel(self):
        async def worker(node, dependencies):
            if node.task_id == "a":
                raise asyncio.CancelledError()
            return {"ok": True}
        scheduler = Scheduler([Node("c", ("b",), "read"), Node("b", ("a",), "read"),
                               Node("a", (), "read"), Node("d", (), "read")], worker)
        await scheduler.run()
        self.assertEqual(scheduler.states, {"a": "cancelled", "d": "succeeded", "b": "blocked", "c": "blocked"})
        self.assertFalse(scheduler.running)
        self.assertEqual(sum(scheduler.role_use.values()), 0)
        self.assertNotIn("parent_cancelled", [event["kind"] for event in scheduler.events])

    async def test_parallel_dependencies_and_role_limits(self):
        scheduler = Scheduler(make_plan(), OrderWorker(load_inputs()), concurrency=3)
        result = await scheduler.run()
        self.assertEqual(result["publish"]["quote"]["total_cents"], 5200)
        self.assertEqual(scheduler.peak_active, 2)  # reader capacity is two
        finished, active = set(), Counter()
        for event in scheduler.events:
            key = event["task_id"]
            if event["kind"] == "start":
                self.assertTrue(set(scheduler.plan[key].dependencies) <= finished)
                active[event["role"]] += 1
                limit = next(role.capacity for role in scheduler.roles if role.name == event["role"])
                self.assertLessEqual(active[event["role"]], limit)
            if event["kind"] == "succeeded":
                finished.add(key)
                role = next(item["role"] for item in scheduler.events
                            if item["kind"] == "start" and item["task_id"] == key)
                active[role] -= 1

    async def test_failure_blocks_only_descendants(self):
        scheduler = Scheduler(make_plan(), OrderWorker(load_inputs("prices-missing.json")))
        await scheduler.run()
        self.assertEqual(scheduler.states["prices"], "failed")
        self.assertEqual(scheduler.states["stock"], "succeeded")
        self.assertEqual(scheduler.states["policy"], "succeeded")
        self.assertEqual({scheduler.states[key] for key in ("quote", "review", "publish")}, {"blocked"})
        self.assertNotIn("publish", scheduler.results)

    async def test_replan_preserves_unaffected_results(self):
        worker = OrderWorker(load_inputs())
        scheduler = Scheduler(make_plan(), worker)
        await scheduler.run()
        worker.inputs = load_inputs("prices-v2.json")
        affected = scheduler.replan(make_plan("2", shipping=True), {"prices"})
        self.assertEqual(affected, ["prices", "publish", "quote", "review", "shipping"])
        await scheduler.run()
        self.assertEqual(scheduler.results["publish"]["quote"]["total_cents"], 6000)
        starts = Counter(event["task_id"] for event in scheduler.events if event["kind"] == "start")
        self.assertEqual(starts["stock"], 1)
        self.assertEqual(starts["policy"], 1)
        self.assertEqual(scheduler.executions, 11)

    async def test_timeout_releases_role(self):
        nodes = [Node("slow", (), "read", timeout=.001), Node("next", (), "read")]
        async def worker(node, dependencies):
            await asyncio.sleep(.01 if node.task_id == "slow" else 0)
            return {"ok": True}
        scheduler = Scheduler(nodes, worker, roles=(Role("r", frozenset({"read"}), 1, 1),))
        await scheduler.run()
        self.assertEqual(scheduler.states["slow"], "failed")
        self.assertEqual(scheduler.states["next"], "succeeded")
        self.assertEqual(scheduler.role_use["r"], 0)

    async def test_cancellation_and_active_replan(self):
        started = asyncio.Event()
        async def worker(node, dependencies):
            started.set()
            await asyncio.Event().wait()
        scheduler = Scheduler([Node("child", (), "read")], worker)
        parent = asyncio.create_task(scheduler.run())
        await started.wait()
        with self.assertRaises(RuntimeError):
            scheduler.replan([Node("child", (), "read")])
        parent.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await parent
        self.assertEqual(scheduler.states["child"], "cancelled")
        self.assertFalse(scheduler.running)
        self.assertIn("cleanup", [event["kind"] for event in scheduler.events])

    async def test_budget_blocks_unfinished_work(self):
        scheduler = Scheduler(make_plan(), OrderWorker(load_inputs()), max_executions=2)
        await scheduler.run()
        self.assertEqual(scheduler.executions, 2)
        self.assertNotIn("publish", scheduler.results)
        self.assertTrue(all(value in {"succeeded", "failed", "blocked"} for value in scheduler.states.values()))

    async def test_context_is_a_copy(self):
        async def worker(node, dependencies):
            if node.task_id == "a":
                return {"values": [1]}
            dependencies["a"]["values"].append(2)
            return {}
        scheduler = Scheduler([Node("a", (), "read"), Node("b", ("a",), "read")], worker)
        await scheduler.run()
        self.assertEqual(scheduler.results["a"], {"values": [1]})

    def test_plan_validation(self):
        for nodes, error in [([Node("a", ("x",), "read")], ValueError),
                             ([Node("a", ("a",), "read")], CycleError),
                             ([Node("a", (), "unknown")], ValueError),
                             ([Node("a", (), "read"), Node("a", (), "read")], ValueError)]:
            with self.assertRaises(error):
                Scheduler(nodes, None)


if __name__ == "__main__":
    unittest.main()
