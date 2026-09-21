import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from artifacts import Artifacts
from demo import conflict, versions
from state import Store, complete, initial


class StateTests(unittest.TestCase):
    def test_actual_parallel_conflict_and_merge(self):
        with TemporaryDirectory() as root:
            result = conflict(Path(root))
            self.assertEqual(result["conflict"], "expected=1 actual=2")
            self.assertEqual((result["cas_next_step"], result["budget"]), ("verify", 3))
            self.assertEqual(result["unversioned_next_step"], "inspect")

    def test_change_invalidates_old_passed_evidence(self):
        with TemporaryDirectory() as root:
            root = Path(root)
            versions(root)
            objects = Artifacts(root / "objects")
            state = json.loads((root / "state.json").read_text())
            state["refs"]["code"] = objects.put("code", "def mean(x): return 0\n", ".py",
                                                {"plan": state["refs"]["plan"]})
            with self.assertRaisesRegex(ValueError, "stale evidence"):
                complete(state, objects)

    def test_tamper_is_detected_even_with_same_path(self):
        with TemporaryDirectory() as root:
            objects = Artifacts(root)
            ident = objects.put("code", "original", ".py")
            (Path(root) / ident / "payload.py").write_text("changed")
            with self.assertRaisesRegex(ValueError, "payload mismatch"):
                objects.read(ident)

    def test_reject_invalid_transition_without_new_snapshot(self):
        with TemporaryDirectory() as root:
            store = Store(Path(root) / "state.sqlite")
            state = initial()
            store.save(state, 0)
            state["status"] = "completed"
            with self.assertRaisesRegex(ValueError, "invalid transition"):
                store.save(state, 1)
            self.assertEqual(store.load()[0], 1)
            store.close()


if __name__ == "__main__":
    unittest.main()
