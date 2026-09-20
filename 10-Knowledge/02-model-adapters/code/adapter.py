"""OpenAI Chat Completions -> response dictionaries with explicit failure states."""
from __future__ import annotations
import copy
import json
import os
from pathlib import Path
from urllib.parse import urlparse
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
TOKEN_FIELDS = ("prompt_tokens", "completion_tokens", "total_tokens")


class AdapterError(Exception):
    def __init__(self, code, detail, retryable=False):
        super().__init__(detail)
        self.code, self.retryable = code, retryable
        self.detail = detail

    def record(self):
        return dict(code=self.code, detail=self.detail, retryable=self.retryable)


def settings_from_env():
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env", override=False)
    names = ("OPENAI_BASE_URL", "OPENAI_API_KEY", "OPENAI_MODEL")
    values = [os.getenv(name, "").strip() for name in names]
    missing = [name for name, value in zip(names, values)
               if not value or value in ("your-api-key", "your-model-name")]
    if missing:
        raise AdapterError("configuration", "请配置：" + ", ".join(missing))
    url = urlparse(values[0])
    if url.scheme not in ("http", "https") or not url.netloc or url.username or url.password or url.query or url.fragment:
        raise AdapterError("configuration", "OPENAI_BASE_URL 必须是不含认证信息、查询参数的 HTTP(S) 基础 URL")
    if url.path.rstrip("/").endswith("/chat/completions"):
        raise AdapterError("configuration", "OPENAI_BASE_URL 不要包含 /chat/completions")
    return dict(base_url=values[0], api_key=values[1], model=values[2])


def reject_constant(value):
    raise ValueError(f"JSON 不接受非有限数值：{value}")


def parse_object(text, code="invalid_arguments"):
    try:
        value = json.loads(text, parse_constant=reject_constant)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise AdapterError(code, "内容必须是完整 JSON 对象") from exc
    if not isinstance(value, dict):
        raise AdapterError(code, "JSON 根节点必须是对象")
    return value


def normalized_usage(raw):
    raw = raw or {}
    return {key: raw[key] if type(raw.get(key)) is int and raw[key] >= 0 else None for key in TOKEN_FIELDS}


class UsageLedger:
    def __init__(self):
        self.requests = []

    def add(self, usage):
        self.requests.append(normalized_usage(usage))

    def summary(self):
        return {
            "request_count": len(self.requests),
            "fully_metered_requests": sum(all(value is not None for value in item.values()) for item in self.requests),
            "fields": {key: {
                "known_sum": sum(item[key] for item in self.requests if item[key] is not None),
                "reported_requests": sum(item[key] is not None for item in self.requests),
                "missing_requests": sum(item[key] is None for item in self.requests),
            } for key in TOKEN_FIELDS},
        }


def normalize_message(message, finish_reason, usage=None):
    if message.get("refusal"):
        raise AdapterError("refused", "服务返回 refusal")
    if finish_reason == "length":
        raise AdapterError("output_truncated", "输出达到长度上限")
    if finish_reason == "content_filter":
        raise AdapterError("content_filtered", "服务结束了受过滤的输出")
    if finish_reason not in ("stop", "tool_calls"):
        raise AdapterError("incomplete_response", "没有收到可处理的完成状态")
    calls, ids = [], set()
    for call in message.get("tool_calls") or []:
        function = call.get("function") or {}
        if call.get("type") != "function":
            raise AdapterError("unsupported_tool", "只处理 function 类型工具")
        if not call.get("id") or not function.get("name"):
            raise AdapterError("invalid_tool", "工具调用缺少 id 或 name")
        if call["id"] in ids:
            raise AdapterError("duplicate_tool_id", "一次响应中的工具 ID 必须唯一")
        ids.add(call["id"])
        calls.append(dict(id=call["id"], name=function["name"], arguments=parse_object(function.get("arguments"))))
    if (finish_reason == "tool_calls") != bool(calls):
        raise AdapterError("invalid_finish", "finish_reason 与工具调用列表不一致")
    content = message.get("content")
    if not calls and not content:
        raise AdapterError("empty_response", "服务没有返回文本或工具请求")
    return dict(content=content, tool_calls=calls, finish_reason=finish_reason, usage=normalized_usage(usage))


def normalize_completion(raw):
    choices = raw.get("choices") or []
    if len(choices) != 1 or choices[0].get("index") != 0:
        raise AdapterError("invalid_choices", "本文只接收 index=0 的一个候选")
    return normalize_message(choices[0]["message"], choices[0].get("finish_reason"), raw.get("usage"))


def assistant_message(response):
    item = {"role": "assistant", "content": response["content"]}
    if response["tool_calls"]:
        item["tool_calls"] = [{"id": call["id"], "type": "function", "function": {
            "name": call["name"], "arguments": json.dumps(call["arguments"], ensure_ascii=False)}}
            for call in response["tool_calls"]]
    return item


class StreamAccumulator:
    def __init__(self):
        self.content = []
        self.refusal = []
        self.tools = {}
        self.finish_reason = None
        self.usage = None

    def feed(self, chunk):
        # Usage is a request snapshot. Replace it; never add snapshots from the same request.
        if chunk.get("usage") is not None:
            self.usage = chunk["usage"]
        choices = chunk.get("choices") or []
        if not choices:
            return ""  # The final usage-only chunk normally has choices=[].
        if len(choices) != 1 or choices[0].get("index") != 0:
            raise AdapterError("invalid_choices", "流只接收 index=0 的一个候选")
        choice = choices[0]
        delta = choice.get("delta") or {}
        if self.finish_reason is not None and (delta.get("content") or delta.get("tool_calls") or delta.get("refusal")):
            raise AdapterError("invalid_stream", "结束标记之后仍出现内容")
        text = delta.get("content") or ""
        self.content.append(text)
        self.refusal.append(delta.get("refusal") or "")
        for fragment in delta.get("tool_calls") or []:
            index = fragment.get("index")
            if type(index) is not int or index < 0:
                raise AdapterError("invalid_stream", "工具片段缺少非负 index")
            buffer = self.tools.setdefault(index, {"id": None, "type": "function", "function": {"name": "", "arguments": ""}})
            if fragment.get("id"):
                if buffer["id"] and buffer["id"] != fragment["id"]:
                    raise AdapterError("invalid_stream", "同一 index 的工具 ID 改变")
                buffer["id"] = fragment["id"]
            if fragment.get("type"):
                buffer["type"] = fragment["type"]
            function = fragment.get("function") or {}
            buffer["function"]["name"] += function.get("name") or ""
            buffer["function"]["arguments"] += function.get("arguments") or ""
        if choice.get("finish_reason") is not None:
            if self.finish_reason and self.finish_reason != choice["finish_reason"]:
                raise AdapterError("invalid_stream", "流结束状态互相冲突")
            self.finish_reason = choice["finish_reason"]
        return text

    def finish(self):
        return normalize_message({"content": "".join(self.content) or None,
                                  "refusal": "".join(self.refusal) or None,
                                  "tool_calls": [self.tools[key] for key in sorted(self.tools)]},
                                 self.finish_reason, self.usage)


def parse_structured(response, schema):
    if response["finish_reason"] != "stop" or response["tool_calls"]:
        raise AdapterError("invalid_structured_output", "结构化结果必须是完整文本响应")
    value = parse_object(response["content"], "invalid_structured_output")
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(value))
    if errors:
        raise AdapterError("output_schema", errors[0].message)
    return value


class OpenAIAdapter:
    def __init__(self, client, model):
        self.client, self.model = client, model
        self.records, self.ledger = [], UsageLedger()

    @classmethod
    def from_env(cls):
        from openai import OpenAI
        settings = settings_from_env()
        return cls(OpenAI(base_url=settings["base_url"], api_key=settings["api_key"],
                          timeout=30, max_retries=0), settings["model"])

    def request(self, messages, *, stream=False, on_text=None, **options):
        from openai import APIConnectionError, APIStatusError, APITimeoutError, APIError
        payload = dict(model=self.model, messages=messages, **options)
        if stream:
            payload.update(stream=True, stream_options={"include_usage": True})
        record = {"request": copy.deepcopy(payload)}
        self.records.append(record)
        usage = None
        accumulator = StreamAccumulator() if stream else None
        try:
            response = self.client.chat.completions.create(**payload)
            if stream:
                record["chunks"] = []
                with response:
                    for chunk in response:
                        raw = chunk.model_dump(mode="json")
                        record["chunks"].append(raw)
                        text = accumulator.feed(raw)
                        if text and on_text:
                            on_text(text)
                normalized = accumulator.finish()
            else:
                raw = response.model_dump(mode="json")
                record["response"] = raw
                usage = raw.get("usage")
                normalized = normalize_completion(raw)
            record["normalized"] = normalized
            return normalized
        except AdapterError as exc:
            record["error"] = exc.record()
            raise
        except (APITimeoutError, APIConnectionError) as exc:
            error = AdapterError("transport_error", type(exc).__name__, True)
            record["error"] = error.record()
            raise error from exc
        except APIStatusError as exc:
            error = AdapterError("http_error", f"HTTP {exc.status_code}", exc.status_code in (408, 429) or exc.status_code >= 500)
            record["error"] = error.record()
            raise error from exc
        except APIError as exc:
            error = AdapterError("provider_error", type(exc).__name__)
            record["error"] = error.record()
            raise error from exc
        except json.JSONDecodeError as exc:
            error = AdapterError("invalid_protocol_json", "服务返回了不完整的 JSON 事件")
            record["error"] = error.record()
            raise error from exc
        finally:
            if accumulator is not None:
                usage = accumulator.usage
            self.ledger.add(usage)
            record["usage"] = normalized_usage(usage)
