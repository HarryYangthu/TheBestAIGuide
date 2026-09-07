"""Network model and explicitly scripted teaching driver share one small interface."""
import json
import os
import urllib.request
import urllib.error


class LiveModel:
    mode = "live"

    def __init__(self):
        self.key = os.environ.get("MINI_AGENT_API_KEY")
        self.model = os.environ.get("MINI_AGENT_MODEL")
        self.base = os.environ.get("MINI_AGENT_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        if not self.key or not self.model:
            raise ValueError("Set MINI_AGENT_API_KEY and MINI_AGENT_MODEL")
        if not self.base.startswith("https://") and not self.base.startswith(("http://localhost:", "http://127.0.0.1:")):
            raise ValueError("use HTTPS or a loopback HTTP model server")

    def respond(self, messages, tools):
        payload = json.dumps({"model": self.model, "messages": messages, "tools": tools,
                              "temperature": 0}).encode()
        request = urllib.request.Request(self.base + "/chat/completions", data=payload,
                   headers={"Authorization": "Bearer " + self.key, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.load(response)
        except urllib.error.HTTPError as error:
            # Do not put response bodies or authentication headers in teaching traces.
            raise RuntimeError(f"model_http_error_{error.code}") from None
        except (urllib.error.URLError, TimeoutError):
            raise RuntimeError("model_transport_error") from None
        message = data["choices"][0]["message"]
        return {"role": "assistant", "content": message.get("content"),
                **({"tool_calls": message["tool_calls"]} if message.get("tool_calls") else {})}, data.get("usage", {})


class DemoModel:
    """A known trajectory for this fixture. It is NOT an LLM or an ability benchmark."""
    mode = "demo"

    def __init__(self, stage):
        self.stage, self.cursor = stage, 0
        self.observed = {}
        self.actions = []
        if stage >= 5:
            self.actions.append(("update_plan", {"steps": [{"task": "查找旧版和新版资料", "status": "doing"},
                                                          {"task": "生成并检查清单", "status": "pending"}], "reason": "先核对资料再写结论"}))
        self.actions += [("list_files", {})]
        if stage >= 2:
            self.actions += [("read_file", {"path": "release-notes.md"})]
        if stage >= 5:
            self.actions += [("update_plan", {"steps": [{"task": "改读目录中存在的 v1.md 与 v2.md", "status": "doing"},
                                                        {"task": "生成并检查清单", "status": "pending"}], "reason": "release-notes.md 不存在，依据目录改用实际文件"})]
        if stage >= 6:
            self.actions += [("parallel_read", {"paths": ["v1.md", "v2.md"]})]
        else:
            self.actions += [("read_file", {"path": "v1.md"}), ("read_file", {"path": "v2.md"})]
        self.actions += [("write_report", None)]
        if stage >= 5:
            self.actions += [("update_plan", {"steps": [{"task": "读取并比较两份正式说明", "status": "done"},
                                                        {"task": "保存升级清单", "status": "done"}], "reason": "清单已保存，是否正确由宿主独立验收"})]

    def respond(self, messages, tools):
        # Read actual tool observations, including when earlier message groups were removed.
        for message in messages:
            if message.get("role") != "tool":
                continue
            result = json.loads(message["content"])
            if result.get("ok"):
                entries = result["result"] if isinstance(result["result"], list) else [result["result"]]
                for entry in entries:
                    if isinstance(entry, dict) and "path" in entry and "lines" in entry:
                        self.observed[entry["path"]] = {line["line"]: line["text"] for line in entry["lines"]}
        if self.cursor >= len(self.actions):
            return {"role": "assistant", "content": "教学轨迹已结束，请查看独立验收报告。"}, {}
        name, arguments = self.actions[self.cursor]
        if name == "write_report":
            # Fixed expected values deliberately make this a reproducible demonstration.
            values = [("auth", "X-API-Key", "Authorization: Bearer", 2),
                      ("timeout", "30 秒", "10 秒", 3), ("retry", "3 次", "0 次", 4)]
            changes = []
            for key, before, after, line in values:
                changes.append({"id": key, "before": before, "after": after,
                                "old_source": {"path": "v1.md", "line": line, "quote": self.observed["v1.md"][line]},
                                "source": {"path": "v2.md", "line": line, "quote": self.observed["v2.md"][line]}})
            arguments = {"changes": changes}
        self.cursor += 1
        return {"role": "assistant", "content": None, "tool_calls": [{"id": f"demo-{self.cursor}", "type": "function",
                  "function": {"name": name, "arguments": json.dumps(arguments, ensure_ascii=False)}}]}, {}
