import tempfile
import unittest
from pathlib import Path
from evaluation import accept, cases, run_one, summarize, write_json


class EvaluationTests(unittest.TestCase):
    def test_accept_reads_changed_artifact(self):
        expected = cases()[0]["expected"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.json"
            write_json(path, expected)
            self.assertTrue(accept(path, expected)["accepted"])
            write_json(path, {**expected, "total": 0})
            self.assertFalse(accept(path, expected)["accepted"])

    def test_missing_and_non_object_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.json"
            self.assertFalse(accept(path, {})["accepted"])
            write_json(path, [])
            self.assertFalse(accept(path, {})["accepted"])

    def test_boolean_is_not_integer(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.json"
            write_json(path, {"valid_rows": True})
            self.assertFalse(accept(path, {"valid_rows": 1})["accepted"])

    def pair(self, tmp):
        case = next(c for c in cases() if c["id"] == "invalid")
        return [run_one(case, variant, 0, Path(tmp) / variant) for variant in ("baseline", "candidate")]

    def test_failures_retained_and_unknown_cost_is_null(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = summarize(self.pair(tmp), ["invalid"], 1)
            for value in result["variants"].values():
                self.assertEqual(value["denominator"], 1)
                self.assertEqual(value["successes"], 0)
                self.assertIsNone(value["total_cost_usd"])
                self.assertEqual(value["cost_coverage"], 0)

    def test_missing_or_duplicate_pair_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = self.pair(tmp)
            for broken in (rows[:1], rows + rows[:1]):
                with self.assertRaises(ValueError):
                    summarize(broken, ["invalid"], 1)

    def test_changed_pair_input_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = self.pair(tmp)
            rows[1]["input_sha256"] = "different"
            with self.assertRaises(ValueError):
                summarize(rows, ["invalid"], 1)


if __name__ == "__main__":
    unittest.main()
