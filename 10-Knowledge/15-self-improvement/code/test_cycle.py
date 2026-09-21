import tempfile
import unittest
import shutil
from pathlib import Path
from unittest.mock import patch
from cycle import BASELINE, ROOT, gate, load_version, propose, read_json, rollback, run_active, run_cycle, write_json


class CycleTests(unittest.TestCase):
    def test_candidate_is_generated_only_for_supported_evidence(self):
        unchanged, changes = propose(BASELINE, [{"reason": "unclassified"}])
        self.assertEqual(unchanged, BASELINE)
        self.assertEqual(changes, [])
        candidate, changes = propose(BASELINE, [{"reason": "unrecognized_status"}])
        self.assertTrue(candidate["normalize_status"])
        self.assertEqual(candidate["invalid_value"], "reject")
        self.assertEqual(len(changes), 1)

    def test_adopt_then_rollback_changes_real_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "cycle"
            decision = run_cycle(run)
            self.assertTrue(decision["adopted"])
            self.assertTrue(run_active(run, "whitespace", run / "adopted-probe")["accepted"])
            rollback(run, "test")
            self.assertEqual(read_json(run / "active.json")["version"], decision["baseline"])
            self.assertFalse(run_active(run, "whitespace", run / "rollback-probe")["accepted"])

    def test_regression_is_rejected_even_with_higher_total(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "cycle"
            decision = run_cycle(run, negative_filter=True)
            self.assertFalse(decision["adopted"])
            self.assertFalse(decision["checks"]["dev_no_regressions"])
            self.assertTrue(decision["checks"]["dev_has_improvement"])
            self.assertEqual(read_json(run / "active.json")["version"], decision["baseline"])

    def test_modified_version_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "cycle"
            decision = run_cycle(run)
            write_json(run / "versions" / decision["candidate"] / "policy.json", BASELINE)
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                load_version(run, decision["candidate"])

    def test_missing_pair_is_not_removed_from_denominator(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "cycle"
            decision = run_cycle(run)
            rows = {}
            for split in ("dev", "holdout"):
                rows[split] = {name: [read_json(p) for p in (run / "evaluations" / split / decision[name]).glob("*/result.json")] for name in ("baseline", "candidate")}
            rows["dev"]["candidate"].pop()
            with self.assertRaisesRegex(ValueError, "incomplete"):
                gate(rows)

    def test_budget_can_block_otherwise_passing_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "cycle"
            decision = run_cycle(run)
            rows = {}
            for split in ("dev", "holdout"):
                rows[split] = {name: [read_json(p) for p in (run / "evaluations" / split / decision[name]).glob("*/result.json")] for name in ("baseline", "candidate")}
            rows["holdout"]["candidate"][0]["tool_calls"] = 2
            self.assertFalse(gate(rows)["passed"])

    def test_missing_input_keeps_failures_and_blocks_adoption(self):
        with tempfile.TemporaryDirectory() as tmp:
            chapter = Path(tmp) / "chapter"
            shutil.copytree(ROOT / "fixtures", chapter / "fixtures")
            (chapter / "fixtures/whitespace.csv").unlink()
            run = Path(tmp) / "cycle"
            with patch("cycle.ROOT", chapter):
                with self.assertRaisesRegex(ValueError, "missing input hash"):
                    run_cycle(run)
            # Each version still has all 4 tasks x 2 trials, including the missing file.
            for version_dir in (run / "evaluations/dev").iterdir():
                rows = [read_json(p) for p in version_dir.glob("*/result.json")]
                self.assertEqual(len(rows), 8)
                for row in rows:
                    if row["task_id"] == "whitespace":
                        self.assertFalse(row["accepted"])
                        self.assertIsNone(row["input_sha256"])
                        self.assertEqual(row["tool_calls"], 0)
                        self.assertEqual(row["error_type"], "FileNotFoundError")
            failure = next(f for f in read_json(run / "failures.json") if f["task_id"] == "whitespace")
            self.assertEqual(failure["reason"], "unclassified")
            self.assertEqual(len((run / "history.jsonl").read_text().splitlines()), 1)
            current = read_json(run / "active.json")["version"]
            self.assertEqual(read_json(run / "versions" / current / "manifest.json")["evidence"]["role"], "baseline")

    def test_one_missing_hash_cannot_count_as_a_candidate_win(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "cycle"
            decision = run_cycle(run)
            rows = {}
            for split in ("dev", "holdout"):
                rows[split] = {name: [read_json(p) for p in (run / "evaluations" / split / decision[name]).glob("*/result.json")] for name in ("baseline", "candidate")}
            failed = next(r for r in rows["dev"]["baseline"] if r["task_id"] == "whitespace")
            failed["input_sha256"] = None
            with self.assertRaisesRegex(ValueError, "missing input hash"):
                gate(rows)


if __name__ == "__main__":
    unittest.main()
