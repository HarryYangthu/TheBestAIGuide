import copy
import json
from pathlib import Path
import tempfile
import unittest
from contracts import ROOT, ContractError, accept, calculate, execute, prepare, validate
from experiments import run_experiments


class ContractTests(unittest.TestCase):
    def test_saved_result_and_independent_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "run"
            record = execute(ROOT / "examples/task.json", directory)
            self.assertEqual(record["status"], "accepted")
            result = json.loads((directory / "result.json").read_text())
            self.assertEqual((result["count"], result["total_hours"], result["mean_hours"]), (3, 6, 2))
            self.assertEqual(result["completed_ids"], ["T-101", "T-102", "T-104"])
            self.assertEqual((directory / "tickets.json").read_bytes(), (ROOT / "examples/tickets.json").read_bytes())

    def test_runs_are_distinct_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = execute(ROOT / "examples/task.json", Path(tmp) / "a")
            b = execute(ROOT / "examples/task.json", Path(tmp) / "b")
            self.assertEqual(a["task_id"], b["task_id"])
            self.assertNotEqual(a["run_id"], b["run_id"])
            with self.assertRaises(FileExistsError): execute(ROOT / "examples/task.json", Path(tmp) / "a")

    def test_full_failure_matrix(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = run_experiments(Path(tmp) / "cases")
            self.assertTrue(all(row["matched"] for row in rows))
            self.assertEqual(sum(row["accepted"] for row in rows), 1)

    def test_extra_fields_and_bool_rejected(self):
        task, source, rows = prepare(ROOT / "examples/task.json")
        for value in [True, "3"]:
            output = calculate(task, source, rows, "run-a")
            output["count"] = value
            with self.assertRaises(ContractError): validate(output, "result", "output")
        bad = copy.deepcopy(rows)
        bad[0]["secret"] = "unexpected"
        with self.assertRaises(ContractError): validate(bad, "tickets", "input")

    def test_acceptance_detects_identity_count_and_mean(self):
        task, source, rows = prepare(ROOT / "examples/task.json")
        output = calculate(task, source, rows, "run-a")
        output.update(run_id="run-b", count=4, mean_hours=1.5, completed_ids=["T-103"])
        checked = accept(task, source, rows, output, "run-a")
        self.assertFalse(checked["passed"])
        for key in ["run_identity", "count", "mean_hours", "exact_ids"]:
            self.assertFalse(checked["checks"][key])

    def test_missing_input_is_classified(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = execute(Path(tmp) / "absent.json", Path(tmp) / "run")
            self.assertEqual(record["error"]["code"], "input_missing")
            self.assertFalse(record["error"]["retryable"])


if __name__ == "__main__": unittest.main()
