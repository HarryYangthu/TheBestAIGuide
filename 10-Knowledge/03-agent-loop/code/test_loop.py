"""验证反馈传递、停止边界与真实产物，不把脚本替身当作模型能力评测。"""
import io
import json
import tempfile
import unittest
from unittest.mock import patch

from openai_model import OpenAIModel
from scenarios import run_case
from shared import (BUGGY_SOURCE, FIXED_SOURCE, ScriptedModel, TransientModelError,
                    call_response, create_workspace, read_file)
from v1_minimal_loop import run_loop as minimal_loop, run_manual
from shared import text_response
from v4_resilient_loop import run_loop


def demo_model():
    return ScriptedModel([call_response("read-1", "read_file", path="notes.txt"),
                          text_response("本周完成了工具接入与循环日志。")])


class LoopTests(unittest.TestCase):
    def test_manual_and_loop_produce_same_history(self):
        with tempfile.TemporaryDirectory() as path:
            workspace = create_workspace(path)
            manual = run_manual(demo_model(), workspace)
            loop = minimal_loop(demo_model(), workspace)
            self.assertEqual(manual, loop)
            self.assertEqual(json.loads(loop[2]["content"]), read_file(workspace, "notes.txt"))

    def test_observation_enters_next_model_input(self):
        result = run_case("normal")
        self.assertTrue(result["acceptance"]["passed"])
        second_input = result["model_inputs"][1]["messages"]
        self.assertEqual(second_input[-1]["tool_call_id"], "c1")
        observation = json.loads(second_input[-1]["content"])
        self.assertEqual(observation["output"], BUGGY_SOURCE)
        self.assertEqual(len(result["model_inputs"][0]["messages"]), 1)

    def test_tool_error_is_available_to_next_decision(self):
        result = run_case("bad_tool")
        message = result["model_inputs"][1]["messages"][-1]
        self.assertFalse(json.loads(message["content"])["ok"])
        self.assertIn("read_flie", json.loads(message["content"])["error"]["message"])
        self.assertTrue(result["acceptance"]["passed"])

    def test_finish_does_not_imply_acceptance(self):
        result = run_case("early_finish")
        self.assertEqual(result["reason"], "finish")
        self.assertFalse(result["acceptance"]["passed"])

    def test_budget_stop_can_leave_acceptable_artifact(self):
        result = run_case("step_limit")
        self.assertEqual(result["reason"], "step_limit")
        self.assertEqual(result["model_calls"], 2)
        self.assertTrue(result["acceptance"]["passed"])
        self.assertFalse(any(event.get("name") == "check_tests" for event in result["trace"]))

    def test_empty_responses_stop_at_configured_limit(self):
        result = run_case("empty_response")
        self.assertEqual(result["reason"], "empty_response_limit")
        self.assertEqual(result["model_calls"], 2)

    def test_duplicate_id_prevents_second_execution(self):
        result = run_case("duplicate_id")
        self.assertEqual(result["reason"], "duplicate_call_id")
        self.assertEqual(result["artifact_source"], BUGGY_SOURCE)
        tool_messages = [message for message in result["messages"] if message["role"] == "tool"]
        self.assertEqual(len(tool_messages), 1)

    def test_duplicate_ids_within_batch_prevent_all_batch_writes(self):
        response = {"content": None, "tool_calls": [
            {"id": "x", "name": "write_file", "arguments": {"path": "stats.py", "content": FIXED_SOURCE}},
            {"id": "x", "name": "read_file", "arguments": {"path": "stats.py"}},
        ]}
        with tempfile.TemporaryDirectory() as path:
            workspace = create_workspace(path)
            result = run_loop(ScriptedModel([response]), workspace)
            self.assertEqual(result["reason"], "duplicate_call_id")
            self.assertEqual(read_file(workspace, "stats.py"), BUGGY_SOURCE)

    def test_old_pass_does_not_override_final_artifact(self):
        result = run_case("stale_test")
        old_test = next(event["observation"]["output"] for event in result["trace"] if event.get("name") == "check_tests")
        self.assertTrue(old_test["passed"])
        self.assertFalse(result["acceptance"]["passed"])
        self.assertNotEqual(old_test["source_sha256"], result["acceptance"]["source_sha256"])

    def test_tool_success_is_distinct_from_test_success(self):
        result = run_case("failing_test")
        observation = next(event["observation"] for event in result["trace"] if event.get("name") == "check_tests")
        self.assertTrue(observation["ok"])
        self.assertFalse(observation["output"]["passed"])

    def test_transient_failure_retries_identical_model_input(self):
        result = run_case("transient_model")
        self.assertEqual(result["model_inputs"][0], result["model_inputs"][1])
        self.assertEqual(result["model_calls"], 5)
        self.assertTrue(result["acceptance"]["passed"])
        writes = [event for event in result["trace"] if event.get("name") == "write_file"]
        self.assertEqual(len(writes), 1)

    def test_failed_model_attempts_consume_budget_and_retry_allowance(self):
        with tempfile.TemporaryDirectory() as path:
            workspace = create_workspace(path)
            model = ScriptedModel([TransientModelError("retry") for _ in range(4)])
            result = run_loop(model, workspace, max_steps=12, max_model_retries=2)
            self.assertEqual((result["reason"], result["model_calls"]), ("model_retry_limit", 3))
            limited = ScriptedModel([TransientModelError("retry") for _ in range(4)])
            result = run_loop(limited, workspace, max_steps=2, max_model_retries=2)
            self.assertEqual((result["reason"], result["model_calls"]), ("step_limit", 2))

    def test_parameter_failure_is_observed_before_finish(self):
        model = ScriptedModel([
            call_response("c1", "read_file", path=10),
            call_response("c2", "finish", summary="停止实验。"),
        ])
        with tempfile.TemporaryDirectory() as path:
            result = run_loop(model, create_workspace(path))
            self.assertEqual(result["reason"], "finish")
            observation = json.loads(model.inputs[1]["messages"][-1]["content"])
            self.assertFalse(observation["ok"])
            self.assertIn("path", observation["error"]["message"])

    def test_finish_cannot_hide_other_pending_actions(self):
        response = {"content": None, "tool_calls": [
            {"id": "c1", "name": "finish", "arguments": {"summary": "done"}},
            {"id": "c2", "name": "write_file", "arguments": {"path": "stats.py", "content": FIXED_SOURCE}},
        ]}
        with tempfile.TemporaryDirectory() as path:
            workspace = create_workspace(path)
            result = run_loop(ScriptedModel([response]), workspace)
            self.assertEqual(result["reason"], "finish_must_be_alone")
            self.assertEqual(read_file(workspace, "stats.py"), BUGGY_SOURCE)

    def test_file_tool_rejects_path_outside_workspace(self):
        with tempfile.TemporaryDirectory() as path:
            workspace = create_workspace(path)
            with self.assertRaises(ValueError):
                read_file(workspace, "../outside.txt")

    def test_adapter_translates_normalized_request_without_network(self):
        from openai import OpenAI
        import httpx2 as httpx
        response_data = {"choices": [{"message": {"content": None, "tool_calls": [{
            "id": "r1", "type": "function", "function": {"name": "read_file", "arguments": '{"path":"stats.py"}'},
        }]}}]}
        sent = {}
        def handle(request):
            sent.update(json.loads(request.content))
            self.assertEqual(request.url.path, "/v1/chat/completions")
            return httpx.Response(200, json=response_data)
        client = OpenAI(base_url="https://example.invalid/v1", api_key="test-key", max_retries=0,
                        http_client=httpx.Client(transport=httpx.MockTransport(handle)))
        adapter = OpenAIModel(client, "test-model")
        history = [{"role": "assistant", **call_response("c0", "read_file", path="notes.txt")},
                   {"role": "tool", "tool_call_id": "c0", "content": '"notes"'}]
        result = adapter(history, tools=[])
        self.assertEqual(json.loads(sent["messages"][0]["tool_calls"][0]["function"]["arguments"]), {"path": "notes.txt"})
        self.assertEqual(result["tool_calls"][0]["arguments"], {"path": "stats.py"})
        self.assertEqual(len(adapter.records), 1)
        self.assertNotIn("api_key", json.dumps(adapter.records))

    def test_missing_key_does_not_switch_to_fixture(self):
        from config import load_settings
        with patch.dict("os.environ", {}, clear=True), patch("dotenv.load_dotenv"):
            with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
                load_settings()

    def test_run_artifacts_retain_changed_input_and_final_file(self):
        from pathlib import Path
        from artifacts import new_run, save_run
        with tempfile.TemporaryDirectory() as path:
            directory, workspace = new_run("test", path)
            self.assertEqual(read_file(workspace, "notes.txt"),
                             (Path(__file__).resolve().parents[1] / "notes.txt").read_text())
            result = run_case("normal")
            (workspace / "stats.py").write_text(result["artifact_source"])
            result.update(stage="test", execution_mode="fixture")
            save_run(directory, result, [], BUGGY_SOURCE)
            saved = json.loads((directory / "result.json").read_text())
            self.assertTrue(saved["acceptance"]["passed"])
            self.assertIn("return sum(values)", (directory / "changes.diff").read_text())
            self.assertTrue((directory / "report.md").exists())


if __name__ == "__main__":
    unittest.main()
