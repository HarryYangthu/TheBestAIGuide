"""Meaningful regression cases: corrupted evidence, tool feedback and budget limits."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mini_agent.harness import curriculum
from mini_agent.runtime import run
from mini_agent.providers import DemoModel, LiveModel
from mini_agent.tools import ToolBox, schemas
from mini_agent.evaluate import evaluate
from mini_agent.context import pack
from mini_agent.parallel import read_many
from unittest.mock import patch
from io import BytesIO


class MiniAgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.docs = ROOT / "fixtures/docs"

    def test_curriculum_including_expected_failures(self):
        summary = curriculum(self.root / "all")
        self.assertTrue(summary["passed"])
        self.assertFalse(summary["live_model_validated"])

    def test_incorrect_value_real_quote_is_rejected(self):
        output = self.root / "wrong"
        run(output, self.docs, DemoModel(1))
        report = json.loads((output / "report.json").read_text())
        report["changes"][0]["after"] = "X-Preview-Key"
        (output / "report.json").write_text(json.dumps(report))
        result = evaluate(output, self.docs)
        self.assertFalse(result["passed"])
        self.assertIn({"check": "auth:values", "passed": False}, result["checks"])

    def test_missing_change_rejected(self):
        output = self.root / "missing"
        run(output, self.docs, DemoModel(1))
        report = json.loads((output / "report.json").read_text())
        report["changes"].pop()
        (output / "report.json").write_text(json.dumps(report))
        self.assertFalse(evaluate(output, self.docs)["passed"])

    def test_early_model_finish_does_not_pass(self):
        class Early:
            mode = "demo"
            def respond(self, messages, tools):
                return {"role": "assistant", "content": "All done"}, {}
        result = run(self.root / "early", self.docs, Early())
        self.assertEqual(result["status"], "completed")
        self.assertFalse(result["passed"])

    def test_bad_json_and_unknown_tool_return_feedback(self):
        class Faults:
            mode = "demo"
            count = 0
            def respond(self, messages, tools):
                self.count += 1
                if self.count < 3:
                    return {"role": "assistant", "tool_calls": [{"id": str(self.count), "function":
                            {"name": "missing", "arguments": "{" if self.count == 1 else "{}"}}]}, {}
                return {"role": "assistant", "content": "done"}, {}
        output = self.root / "faults"
        run(output, self.docs, Faults(), stage=2)
        state = json.loads((output / "run.json").read_text())
        self.assertEqual(state["tool_errors"], 2)
        self.assertEqual(state["model_calls"], 3)

    def test_paths_and_symlinks_cannot_escape(self):
        box = ToolBox(self.docs, self.root, 7)
        with self.assertRaises(ValueError):
            box.read_file("../expected.json")
        docs = self.root / "docs"
        docs.mkdir()
        (self.root / "secret.md").write_text("secret")
        try:
            (docs / "link.md").symlink_to(self.root / "secret.md")
        except OSError:
            self.skipTest("symlink not permitted on this host")
        with self.assertRaises(ValueError):
            ToolBox(docs, self.root, 7).read_file("link.md")

    def test_context_does_not_split_multiple_tool_calls(self):
        prefix = [{"role": "system", "content": "rules"}, {"role": "user", "content": "task"}]
        recent = [{"role": "assistant", "tool_calls": [{"id": "a"}, {"id": "b"}]},
                  {"role": "tool", "tool_call_id": "a", "content": "one"},
                  {"role": "tool", "tool_call_id": "b", "content": "two"}]
        old = [{"role": "assistant", "content": "x" * 3000}]
        packed, stats = pack(prefix + old + recent, 1000)
        self.assertEqual(packed[-3:], recent)
        self.assertEqual(stats["removed_groups"], 1)
        with self.assertRaises(ValueError):
            pack(prefix + recent, 10)

    def test_existing_output_is_not_overwritten(self):
        with self.assertRaises(ValueError):
            run(self.root, self.docs, DemoModel(1))

    def test_parallel_order_and_limits(self):
        self.assertEqual(read_many(lambda x: x.upper(), ["b", "a"]), ["B", "A"])
        with self.assertRaises(ValueError):
            read_many(str, ["a", "a"])

    def test_subagents_have_isolated_contexts_and_real_read_receipts(self):
        from mini_agent.subagents import delegate
        output = self.root / "children"
        result = delegate(self.docs, output)
        self.assertTrue(result["passed"])
        first = json.loads((output / "v1.md.trace.json").read_text())
        second = json.loads((output / "v2.md.trace.json").read_text())
        self.assertIn("v1.md", first["messages"][1]["content"])
        self.assertNotIn("v2.md", first["messages"][1]["content"])
        self.assertIn("v2.md", second["messages"][1]["content"])

    def test_live_transport_serialization_without_external_request(self):
        # A local mock verifies the wire contract, NOT a real model's ability.
        payload = {"choices": [{"message": {"role": "assistant", "content": "hello"}}],
                   "usage": {"total_tokens": 5}}
        with patch.dict("os.environ", {"MINI_AGENT_API_KEY": "test-only", "MINI_AGENT_MODEL": "test-model"}):
            model = LiveModel()
            with patch("urllib.request.urlopen", return_value=BytesIO(json.dumps(payload).encode())) as request:
                message, usage = model.respond([{"role": "user", "content": "hello"}], schemas(1))
        self.assertEqual(message["content"], "hello")
        self.assertEqual(usage["total_tokens"], 5)
        wire = json.loads(request.call_args.args[0].data)
        self.assertEqual(wire["model"], "test-model")
        self.assertEqual(len(wire["tools"]), 3)


if __name__ == "__main__":
    unittest.main()
