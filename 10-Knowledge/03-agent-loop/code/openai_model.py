"""使用 OpenAI Python SDK，并将 API 字段整理为本文循环使用的响应字典。"""
import copy
import json
from shared import TransientModelError


def normalize_message(message):
    return {
        "content": message.content,
        "tool_calls": [
            {"id": call.id, "name": call.function.name,
             "arguments": json.loads(call.function.arguments)}
            for call in (message.tool_calls or [])
            if call.type == "function"
        ],
    }


def api_messages(messages):
    result = []
    for message in messages:
        item = {"role": message["role"], "content": message.get("content")}
        if message.get("tool_calls"):
            item["tool_calls"] = [
                {"id": call["id"], "type": "function", "function": {
                    "name": call["name"],
                    "arguments": json.dumps(call["arguments"], ensure_ascii=False)}}
                for call in message["tool_calls"]
            ]
        if message["role"] == "tool":
            item["tool_call_id"] = message["tool_call_id"]
        result.append(item)
    return result


class OpenAIModel:
    def __init__(self, client, model_name):
        self.client, self.model_name = client, model_name
        self.records = []
        self.call_options = []

    @classmethod
    def from_env(cls):
        from config import load_settings, make_client
        settings = load_settings()
        return cls(make_client(settings), settings.model)

    def complete(self, messages, tools=None, **options):
        from openai import APIConnectionError, APIStatusError, RateLimitError
        payload = {"model": self.model_name, "messages": messages, **options}
        if tools:
            payload["tools"] = tools
        record = {"request": copy.deepcopy(payload)}
        self.records.append(record)
        try:
            completion = self.client.chat.completions.create(**payload)
        except (APIConnectionError, RateLimitError) as exc:
            record["error"] = {"type": type(exc).__name__}
            raise TransientModelError(type(exc).__name__) from exc
        except APIStatusError as exc:
            record["error"] = {"type": type(exc).__name__, "status_code": exc.status_code}
            if exc.status_code >= 500:
                raise TransientModelError(f"HTTP {exc.status_code}") from exc
            raise RuntimeError(f"模型请求失败：HTTP {exc.status_code}") from exc
        record["response"] = completion.model_dump(mode="json")
        return completion

    def __call__(self, messages, tools):
        index = len(self.records)
        options = self.call_options[index] if index < len(self.call_options) else {}
        completion = self.complete(
            api_messages(messages),
            [{"type": "function", "function": tool} for tool in tools],
            **options,
        )
        return normalize_message(completion.choices[0].message)
