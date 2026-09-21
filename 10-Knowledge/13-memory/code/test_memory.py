import copy
import tempfile
import unittest
from pathlib import Path

from memory import MemoryStore, load_fixture
from run_experiments import run


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "memory.sqlite3"
        self.store = MemoryStore(self.path)
        self.sources = load_fixture("evidence.json")
        self.records = load_fixture("records.json")
        self.task = load_fixture("task-second.json")
        for record in self.records:
            self.store.add(record, self.sources)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_reopen_persists_and_retrieval_filters(self):
        self.store.close()
        self.store = MemoryStore(self.path)
        result = self.store.retrieve(self.task, self.sources)
        self.assertEqual({r["id"] for r in result["selected"]},
                         {"fact-timeout-v3", "failure-permission", "procedure-verification"})
        excluded = {r["id"]: r["reason"] for r in result["excluded"]}
        self.assertEqual(excluded["pref-language"], "current_instruction_overrides")
        self.assertEqual(excluded["other-user-pref"], "user_mismatch")
        self.assertEqual(excluded["rumor-timeout"], "candidate")
        self.assertEqual(excluded["fact-expired"], "expired")

    def test_failure_requires_matching_conditions(self):
        task = {**self.task, "signals": {"phase": "verification"}}
        result = self.store.retrieve(task)
        self.assertNotIn("failure-permission", [r["id"] for r in result["selected"]])

    def test_conflict_then_explicit_revision(self):
        self.assertEqual(self.store.add(load_fixture("conflict.json"), self.sources), "disputed")
        self.assertNotIn("timeout_ms", [r["key"] for r in self.store.retrieve(self.task)["selected"]])
        self.assertEqual(self.store.add(load_fixture("update.json"), self.sources), "active")
        result = self.store.retrieve(load_fixture("task-third.json"))
        self.assertEqual([r["value"] for r in result["selected"] if r["key"] == "timeout_ms"], [2000])

    def test_invalid_supersede_does_not_change_old_memory(self):
        record = load_fixture("update.json")
        record["supersedes"] = ["other-service"]
        before = self.store.rows()
        with self.assertRaises(ValueError):
            self.store.add(record, self.sources)
        self.assertEqual(self.store.rows(), before)

    def test_changed_source_and_time_boundary(self):
        changed = copy.deepcopy(self.sources)
        changed["policy-v3"]["value"] = 9999
        reasons = {r["id"]: r["reason"] for r in self.store.retrieve(self.task, changed)["excluded"]}
        self.assertEqual(reasons["fact-timeout-v3"], "source_changed")
        boundary = {**self.task, "as_of": "2026-10-01"}
        self.assertNotIn("fact-timeout-v3", [r["id"] for r in self.store.retrieve(boundary)["selected"]])

    def test_forget_removes_payload_and_previous_audit_detail(self):
        self.store.forget("pref-language")
        self.assertNotIn("pref-language", [r["id"] for r in self.store.rows()])
        events = self.store.db.execute("SELECT action,detail FROM events WHERE memory_id='pref-language'").fetchall()
        self.assertEqual([tuple(r) for r in events], [("forget", "payload_deleted")])

    def test_transaction_rolls_back_when_audit_write_fails(self):
        self.store.db.execute("CREATE TRIGGER reject_event BEFORE INSERT ON events BEGIN SELECT RAISE(FAIL, 'audit unavailable'); END")
        before = self.store.rows()
        import sqlite3
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.add(load_fixture("conflict.json"), self.sources)
        self.assertEqual(self.store.rows(), before)


if __name__ == "__main__":
    unittest.main()
