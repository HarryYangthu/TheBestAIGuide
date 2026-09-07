import tempfile
from pathlib import Path
import unittest
from state_memory import CheckpointStore, MemoryConflict, MemoryStore, VersionConflict


class StateMemoryTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = str(Path(self.folder.name) / "state.db")

    def tearDown(self):
        self.folder.cleanup()

    def test_checkpoint_resume_and_conflict(self):
        first = CheckpointStore(self.path)
        self.assertEqual(first.load("r"), (0, {}))
        self.assertEqual(first.save("r", {"step": 1}), 1)
        second = CheckpointStore(self.path)
        self.assertEqual(second.load("r"), (1, {"step": 1}))
        with self.assertRaises(VersionConflict):
            second.save("r", {"step": 9}, expected_version=0)
        self.assertEqual(first.load("r"), (1, {"step": 1}))
        self.assertEqual(second.save("r", {"step": 2}, expected_version=1), 2)
        first.close(); second.close()

    def test_scoped_reads(self):
        store = MemoryStore(self.path)
        store.put("alice", "budget", 1000, "user:1", 100)
        store.put("bob", "budget", 2000, "user:2", 100)
        self.assertEqual(store.get("alice", "budget", 100).value, 1000)
        self.assertEqual([m.value for m in store.retrieve("bob", "budget", 100)], [2000])
        store.close()

    def test_ttl_conflict_and_delete(self):
        store = MemoryStore(self.path)
        memory = store.put("alice", "budget", 1000, "user:1", 100, ttl=10)
        self.assertIsNone(store.get("alice", "budget", 110))
        with self.assertRaises(MemoryConflict):
            store.put("alice", "budget", 500, "user:2", 111)
        newer = store.put("alice", "budget", 500, "user:2", 111, expected_version=memory.version)
        self.assertEqual(newer.version, 2)
        self.assertTrue(store.forget("alice", "budget"))
        self.assertFalse(store.forget("alice", "budget"))
        self.assertEqual(store.retrieve("alice", "budget", 112), [])
        with self.assertRaises(MemoryConflict):
            store.put("alice", "budget", 600, "stale-writer", 113, expected_version=2)
        self.assertIsNone(store.db.execute("SELECT value FROM memories").fetchone()[0])
        store.close()

    def test_bad_data_does_not_commit(self):
        store = MemoryStore(self.path)
        with self.assertRaises(ValueError):
            store.put("alice", "x", float("nan"), "fixture", 100)
        self.assertIsNone(store.get("alice", "x", 100))
        store.close()


if __name__ == "__main__":
    unittest.main()
