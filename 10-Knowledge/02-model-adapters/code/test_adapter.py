import copy
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import httpx2 as httpx
from openai import OpenAI
from openai.types.chat import ChatCompletionChunk
from adapter import (ROOT, AdapterError, OpenAIAdapter, StreamAccumulator, UsageLedger,
                     assistant_message, normalize_completion, normalize_message, parse_structured, settings_from_env)
from experiments import experiment, replay
from live import SCHEMA, run, tool_result


def completion(content="完成了工具接入与循环日志", usage=None):
    return {"id": "fixture-completion", "object": "chat.completion", "created": 0, "model": "fixture",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
            "usage": usage}


def chunks():
    return [json.loads(line) for line in (ROOT / "examples/stream-tools.jsonl").read_text().splitlines()]


class AdapterTests(unittest.TestCase):
    def test_interleaved_fragments_are_not_parsed_early(self):
        acc = StreamAccumulator()
        source = chunks()
        for raw in source[:3]:
            # Exercise actual SDK field types, then the same dump used by request().
            acc.feed(ChatCompletionChunk.model_validate(raw).model_dump(mode="json"))
        self.assertEqual(acc.tools[0]["function"]["arguments"], '{"path":')
        with self.assertRaises(AdapterError) as error: acc.finish()
        self.assertEqual(error.exception.code, "incomplete_response")
        for raw in source[3:]: acc.feed(raw)
        response = acc.finish()
        self.assertEqual([call["id"] for call in response["tool_calls"]], ["call_a", "call_b"])
        self.assertEqual([call["arguments"] for call in response["tool_calls"]], [{"path": "notes.txt"}] * 2)
        self.assertEqual(response["usage"]["total_tokens"], 10)

    def test_usage_snapshot_not_double_counted_and_missing_not_zero(self):
        acc = StreamAccumulator()
        for raw in chunks(): acc.feed(raw)
        acc.feed(chunks()[-1])
        ledger = UsageLedger()
        ledger.add(acc.finish()["usage"])
        ledger.add(None)
        ledger.add({"prompt_tokens": 4, "completion_tokens": True})
        value = ledger.summary()
        self.assertEqual(value["request_count"], 3)
        self.assertEqual(value["fully_metered_requests"], 1)
        self.assertEqual(value["fields"]["total_tokens"], {"known_sum": 10, "reported_requests": 1, "missing_requests": 2})
        self.assertEqual(value["fields"]["prompt_tokens"]["known_sum"], 12)

    def test_raw_tools_round_trip_and_tool_boundary(self):
        response = replay(chunks())
        message = assistant_message(response)
        self.assertIsInstance(message["tool_calls"][0]["function"]["arguments"], str)
        self.assertEqual(tool_result(response["tool_calls"][0], "笔记")["tool_call_id"], "call_a")
        bad = copy.deepcopy(response["tool_calls"][0]); bad["arguments"]["path"] = "../secret"
        with self.assertRaises(AdapterError): tool_result(bad, "笔记")
        bad["name"] = "write_file"
        with self.assertRaises(AdapterError): tool_result(bad, "笔记")

    def test_completion_rejects_refusal_length_empty_duplicate_and_array(self):
        cases = [({"content": "x", "refusal": "no"}, "stop", "refused"),
                 ({"content": "x"}, "length", "output_truncated"),
                 ({"content": None}, "stop", "empty_response"),
                 ({"content": "x"}, "content_filter", "content_filtered")]
        for message, finish, code in cases:
            with self.subTest(code=code), self.assertRaises(AdapterError) as error:
                normalize_message(message, finish)
            self.assertEqual(error.exception.code, code)
        raw = assistant_message(replay(chunks()))
        raw["tool_calls"][1]["id"] = "call_a"
        with self.assertRaises(AdapterError) as error: normalize_message(raw, "tool_calls")
        self.assertEqual(error.exception.code, "duplicate_tool_id")
        raw["tool_calls"] = raw["tool_calls"][:1]
        raw["tool_calls"][0]["function"]["arguments"] = "[]"
        with self.assertRaises(AdapterError) as error: normalize_message(raw, "tool_calls")
        self.assertEqual(error.exception.code, "invalid_arguments")

    def test_structured_parse_shape_and_content_validation(self):
        good = normalize_completion(completion('{"completed":["工具接入","循环日志"],"pending":["错误重试"]}'))
        self.assertEqual(parse_structured(good, SCHEMA)["pending"], ["错误重试"])
        for content in ['{"completed":[]}', '```json\n{}\n```', '{"completed":[],"pending":4}']:
            with self.assertRaises(AdapterError): parse_structured(normalize_completion(completion(content)), SCHEMA)

    def test_sdk_http_transport_serialization(self):
        captured = []
        def handler(request):
            captured.append(json.loads(request.content))
            return httpx.Response(200, json=completion(usage={"prompt_tokens": 8, "completion_tokens": 2, "total_tokens": 10}))
        client = OpenAI(api_key="fixture-key", base_url="https://fixture.invalid/v1", max_retries=0,
                        http_client=httpx.Client(transport=httpx.MockTransport(handler)))
        with client:
            adapter = OpenAIAdapter(client, "fixture-model")
            response = adapter.request([{"role": "user", "content": "周报"}])
        self.assertEqual(captured[0]["model"], "fixture-model")
        self.assertEqual(response["usage"]["total_tokens"], 10)
        self.assertNotIn("fixture-key", json.dumps(adapter.records))
        self.assertEqual(adapter.ledger.summary()["request_count"], 1)

    def test_sdk_sse_stream_and_usage_only_event(self):
        events = "".join("data: " + json.dumps(raw) + "\n\n" for raw in chunks()) + "data: [DONE]\n\n"
        captured = []
        def handler(request):
            captured.append(json.loads(request.content))
            return httpx.Response(200, text=events, headers={"content-type": "text/event-stream"})
        with OpenAI(api_key="fixture", base_url="https://fixture.invalid/v1", max_retries=0,
                    http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
            adapter = OpenAIAdapter(client, "fixture")
            value = adapter.request([{"role": "user", "content": "读笔记"}], stream=True)
        self.assertEqual(len(value["tool_calls"]), 2)
        self.assertEqual(captured[0]["stream_options"], {"include_usage": True})
        self.assertEqual(adapter.ledger.summary()["fields"]["total_tokens"]["known_sum"], 10)

    def test_http_failure_is_counted_and_not_retried(self):
        calls = []
        def handler(request):
            calls.append(request)
            return httpx.Response(429, json={"error": {"message": "fixture", "type": "rate_limit"}})
        with OpenAI(api_key="fixture", base_url="https://fixture.invalid/v1", max_retries=0,
                    http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
            adapter = OpenAIAdapter(client, "fixture")
            with self.assertRaises(AdapterError) as error: adapter.request([{"role": "user", "content": "x"}])
        self.assertTrue(error.exception.retryable)
        self.assertEqual(len(calls), 1)
        self.assertEqual(adapter.ledger.summary()["fields"]["total_tokens"]["missing_requests"], 1)

    def test_configuration_failure_is_saved_without_fallback(self):
        with patch.dict(os.environ, {}, clear=True), patch("dotenv.load_dotenv", return_value=False), tempfile.TemporaryDirectory() as tmp:
            result = run("text", Path(tmp) / "run")
        self.assertEqual(result["error"]["code"], "configuration")
        self.assertEqual(result["status"], "failed")
        self.assertNotIn("usage", result)

    def test_interrupted_stream_records_unknown_usage(self):
        class BrokenStream(httpx.SyncByteStream):
            def __iter__(self):
                yield ("data: " + json.dumps(chunks()[0]) + "\n\n").encode()
                raise httpx.ReadError("fixture interrupted")
        def handler(request):
            return httpx.Response(200, stream=BrokenStream(), headers={"content-type": "text/event-stream"})
        with OpenAI(api_key="fixture", base_url="https://fixture.invalid/v1", max_retries=0,
                    http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
            adapter = OpenAIAdapter(client, "fixture")
            with self.assertRaises(AdapterError) as error:
                adapter.request([{"role": "user", "content": "x"}], stream=True)
        self.assertEqual(error.exception.code, "transport_error")
        self.assertNotIn("normalized", adapter.records[0])
        self.assertEqual(len(adapter.records[0]["chunks"]), 1)
        self.assertEqual(adapter.ledger.summary()["fields"]["total_tokens"]["missing_requests"], 1)

    def test_five_live_modes_with_explicit_mock_transport(self):
        for mode in ["text", "tool", "stream", "stream-tools", "structured"]:
            with self.subTest(mode=mode):
                captured = []
                def handler(request):
                    payload = json.loads(request.content)
                    captured.append(payload)
                    is_tool = bool(payload.get("tools")) and payload.get("tool_choice") != "none"
                    if payload.get("stream"):
                        events = chunks() if is_tool else [
                            {"id": "fixture", "object": "chat.completion.chunk", "created": 0, "model": "fixture", "choices": [{"index": 0, "delta": {"content": "周报"}, "finish_reason": None}]},
                            {"id": "fixture", "object": "chat.completion.chunk", "created": 0, "model": "fixture", "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]},
                        ]
                        text = "".join("data: " + json.dumps(raw) + "\n\n" for raw in events) + "data: [DONE]\n\n"
                        return httpx.Response(200, text=text, headers={"content-type": "text/event-stream"})
                    if is_tool:
                        raw = completion()
                        raw["choices"][0] = {"index": 0, "finish_reason": "tool_calls", "message": assistant_message(replay(chunks()))}
                    elif mode == "structured":
                        raw = completion('{"completed":["工具接入","循环日志"],"pending":["错误重试"]}')
                    else: raw = completion()
                    return httpx.Response(200, json=raw)
                client = OpenAI(api_key="fixture", base_url="https://fixture.invalid/v1", max_retries=0,
                                http_client=httpx.Client(transport=httpx.MockTransport(handler)))
                adapter = OpenAIAdapter(client, "fixture")
                with patch.object(OpenAIAdapter, "from_env", return_value=adapter), tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
                    result = run(mode, Path(tmp) / "run")
                    self.assertEqual(result["status"], "completed")
                    self.assertTrue((Path(tmp) / "run/requests-and-responses.json").exists())
                expected_calls = 2 if mode in ["tool", "stream-tools"] else 1
                self.assertEqual(len(captured), expected_calls)
                if expected_calls == 2:
                    self.assertEqual([m["tool_call_id"] for m in captured[1]["messages"] if m["role"] == "tool"], ["call_a", "call_b"])
                if mode == "structured": self.assertTrue(result["acceptance"]["passed"])

    def test_replay_matrix(self):
        with tempfile.TemporaryDirectory() as tmp: result = experiment(Path(tmp) / "run")
        self.assertTrue(all(row["matched"] for row in result["scenarios"]))
        self.assertFalse(result["structured_acceptance"]["passed"])


if __name__ == "__main__": unittest.main()
