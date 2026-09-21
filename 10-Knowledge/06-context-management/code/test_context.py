import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from context import (crop_contains, crop_tool_result, extract_history, initial_messages,
                     isolate_worker, load_on_demand, measure, pack, read_fixture, validate_summary)
from live_compress import compress
import live_compress
from run_experiments import run


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.task = read_fixture("task.json")
        self.history = read_fixture("history.json")

    def test_worker_has_no_parent_alias_or_unrelated_history(self):
        parent = initial_messages(self.task) + [{"role": "user", "content": "secret-other-task"}]
        before = copy.deepcopy(parent)
        worker = isolate_worker(parent, self.task)
        worker[0]["content"] = "changed"
        self.assertEqual(parent, before)
        self.assertNotIn("secret-other-task", str(worker))

    def test_loading_excludes_stale_and_other_service(self):
        docs = load_on_demand(self.task, read_fixture("index.json"))
        self.assertEqual({d["id"] for d in docs}, {"policy-v3", "dry-run-log"})

    def test_crop_preserves_failure_and_retrieval_metadata(self):
        docs = load_on_demand(self.task, read_fixture("index.json"))
        cropped = crop_tool_result(docs[1])
        self.assertTrue(crop_contains(cropped, "rollback_check=FAILED"))
        self.assertTrue(cropped["truncated"])
        self.assertEqual(len(cropped["source_sha256"]), 64)
        self.assertEqual(cropped["omitted_lines"], [3, 82])

    def test_missing_and_stale_facts_are_rejected(self):
        self.assertFalse(validate_summary(read_fixture("bad-summary.json"), self.history)["accepted"])
        summary = extract_history(self.history)
        self.assertTrue(validate_summary(summary, self.history)["accepted"])
        summary["facts"][0]["value"] = "alpha,beta"
        self.assertFalse(validate_summary(summary, self.history)["accepted"])

    def test_malformed_summary_fields_and_types_are_rejected(self):
        valid = extract_history(self.history)
        candidates = [None, {**valid, "unexpected": "x" * 2000}]
        for field, value in [("key", []), ("event_id", {}), ("value", {"untrusted": "text"})]:
            bad = copy.deepcopy(valid)
            bad["facts"][0][field] = value
            candidates.append(bad)
        for candidate in candidates:
            with self.subTest(candidate=candidate):
                self.assertFalse(validate_summary(candidate, self.history)["accepted"])

    def test_live_invalid_model_json_falls_back_without_network(self):
        valid = extract_history(self.history)
        malformed_key = copy.deepcopy(valid)
        malformed_key["facts"][0]["key"] = []
        for candidate in [malformed_key, {**valid, "unexpected": "x" * 2000}]:
            response = SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(candidate)))],
                model_dump=lambda: {"test_response": candidate},
            )
            client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kw: response)))
            with tempfile.TemporaryDirectory() as tmp, \
                    patch.object(live_compress, "ROOT", Path(tmp)), \
                    patch.object(live_compress, "load_dotenv"), \
                    patch.object(live_compress, "OpenAI", return_value=client), \
                    patch.dict("os.environ", {"OPENAI_BASE_URL": "https://example.invalid/v1",
                                              "OPENAI_API_KEY": "test-only", "OPENAI_MODEL": "test-model"}):
                live_compress.main()
                output = next((Path(tmp) / "runs").iterdir())
                self.assertFalse(json.loads((output / "validation.json").read_text())["accepted"])
                self.assertEqual(json.loads((output / "effective-context.json").read_text()), self.history)

    def test_budget_boundary_and_mandatory_overflow(self):
        messages = initial_messages(self.task)
        n = measure(messages)
        self.assertEqual(pack(messages, [], [], n, 0, 0)["serialized_input_tokens"], n)
        with self.assertRaisesRegex(ValueError, "mandatory_overflow"):
            pack(messages, [], [], n - 1, 0, 0)
        result = pack(messages, [], [{"id": "huge", "body": "很长" * 200}], n + 10, 0, 0)
        self.assertFalse(result["decisions"][0]["included"])

    def test_sdk_request_uses_real_protocol_without_network(self):
        captured = {}
        def create(**kwargs):
            captured.update(kwargs)
            return object()
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        request, _ = compress(client, "configured-model", self.history)
        self.assertEqual(request, captured)
        self.assertEqual(captured["response_format"], {"type": "json_object"})

    def test_artifact_acceptance_and_budget_drop(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as tmp:
            result = run(Path(tmp), 2400)
            self.assertEqual(result["acceptance"]["release_decision"], "BLOCKED")
            mandatory_size = result["budget"]["decisions"][0]["trial_tokens"]
            result = run(Path(tmp), mandatory_size - 1 + 900)
            self.assertEqual(result["acceptance"]["release_decision"], "NEEDS_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
