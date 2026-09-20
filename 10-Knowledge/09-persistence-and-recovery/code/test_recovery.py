import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from experiments import child, hard_timeout
from runtime import Recipient, canonical, connect, init, inspect, request_cancel, run


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name) / "run"
        init(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_process_exit_resumes_after_committed_item(self):
        child(self.root, "--crash", "after_item", expected=71)
        self.assertEqual(inspect(self.root)["next_index"], 1)
        child(self.root)
        actual = inspect(self.root)
        self.assertEqual(actual["item_commits"], 3)
        self.assertTrue(actual["acceptance"])

    def test_effect_exists_before_receipt_then_is_adopted(self):
        child(self.root, "--crash", "after_effect", expected=72)
        before = inspect(self.root)
        self.assertEqual((before["operation_status"], before["effect_count"]), ("inflight", 1))
        child(self.root)
        after = inspect(self.root)
        self.assertEqual((after["attempts"], after["effect_count"]), (1, 1))
        self.assertTrue(after["acceptance"])

    def test_attempt_limit_survives_restart(self):
        child(self.root, "--fail-until", "9")
        child(self.root)
        actual = inspect(self.root)
        self.assertEqual((actual["status"], actual["attempts"], actual["effect_count"]), ("failed", 3, 0))

    def test_hard_timeout_reaps_worker_and_recovery_is_safe(self):
        termination = hard_timeout(self.root)
        self.assertTrue(termination["killed"])
        self.assertEqual(inspect(self.root)["effect_count"], 0)
        child(self.root)
        self.assertTrue(inspect(self.root)["acceptance"])

    def test_cancel_reconciles_without_creating_new_effect(self):
        child(self.root, "--crash", "after_effect", expected=72)
        request_cancel(self.root)
        child(self.root)
        result = inspect(self.root)
        self.assertEqual((result["status"], result["operation_status"], result["effect_count"]),
                         ("cancelled", "confirmed", 1))
        self.assertFalse(result["acceptance"])

    def test_cancel_before_work_has_no_effect(self):
        request_cancel(self.root)
        child(self.root)
        result = inspect(self.root)
        self.assertEqual((result["item_commits"], result["effect_count"]), (0, 0))

    def test_input_drift_is_rejected_before_more_work(self):
        child(self.root, "--crash", "after_item", expected=71)
        (self.root / "input.json").write_text('[{"id":"X","values":[99]}]')
        with self.assertRaisesRegex(ValueError, "input changed"):
            run(self.root)

    def test_key_parameter_conflict_and_new_identity(self):
        recipient = Recipient(self.root / "recipient.sqlite")
        payload = {"value": 3}
        first = recipient.publish("same-key", payload)
        self.assertEqual(first, recipient.publish("same-key", payload))
        with self.assertRaisesRegex(ValueError, "changed payload"):
            recipient.publish("same-key", {"value": 4})
        recipient.publish("new-key", payload)
        self.assertEqual(recipient.db.execute("SELECT count(*) FROM publications").fetchone()[0], 2)
        recipient.close()

    def test_uncommitted_cursor_and_result_roll_back_together(self):
        db = connect(self.root / "runtime.sqlite")
        db.execute("BEGIN IMMEDIATE")
        db.execute("INSERT INTO results VALUES (0,'A',3)")
        db.execute("UPDATE task SET next_index=1 WHERE id=1")
        db.close()  # Closing an uncommitted transaction rolls back both changes.
        result = inspect(self.root)
        self.assertEqual((result["next_index"], result["item_commits"]), (0, 0))


if __name__ == "__main__":
    unittest.main()
