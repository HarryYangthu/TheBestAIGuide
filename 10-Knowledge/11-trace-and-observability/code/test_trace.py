import copy
import json
import tempfile
import unittest
from pathlib import Path
from trace_demo import Recorder, union_ms, validate


class TraceTests(unittest.TestCase):
    def sample(self, tmp):
        rec = Recorder(Path(tmp) / "trace.jsonl")
        with rec.span("root", "task", "batch") as root:
            with rec.span("child", "task", "east", root, "batch"):
                pass
        return [json.loads(s) for s in rec.path.read_text().splitlines()]

    def test_nested_trace_and_parent_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = self.sample(tmp)
            self.assertEqual(len(validate(rows)), 2)
            child = next(r for r in rows if r["parent_span_id"])
            self.assertEqual(child["parent_task_id"], "batch")

    def test_orphan_and_bad_interval_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = self.sample(tmp)
            broken = copy.deepcopy(rows)
            broken[0]["parent_span_id"] = "missing"
            with self.assertRaises(ValueError):
                validate(broken)
            rows[0]["end_ms"] = rows[-1]["end_ms"] + 1
            with self.assertRaises(ValueError):
                validate(rows)

    def test_interval_union_avoids_double_count(self):
        self.assertEqual(union_ms([(0, 10), (5, 12), (20, 23)]), 15)
        self.assertEqual(union_ms([]), 0)

    def test_origin_preserved_during_propagation(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = Recorder(Path(tmp) / "trace.jsonl")
            with self.assertRaises(ValueError):
                with rec.span("root", "task", "batch") as root:
                    with rec.span("tool", "tool", "batch", root):
                        raise ValueError("bad amount")
            rows = [json.loads(s) for s in rec.path.read_text().splitlines()]
            validate(rows)
            self.assertEqual(sum(r["error"]["is_origin"] for r in rows), 1)
            self.assertEqual(rows[0]["error"]["origin_span_id"], rows[1]["error"]["origin_span_id"])


if __name__ == "__main__":
    unittest.main()
