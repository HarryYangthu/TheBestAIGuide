"""Host-owned tools. Input documents are read-only; reports have a separate path."""
import json
from pathlib import Path
from .parallel import read_many
from .planning import update_plan


def function(name, description, properties, required):
    return {"type": "function", "function": {"name": name, "description": description,
            "parameters": {"type": "object", "properties": properties,
                           "required": required, "additionalProperties": False}}}


def schemas(stage):
    string = {"type": "string"}
    result = [
        function("list_files", "列出当前资料目录中的 Markdown 文件", {}, []),
        function("read_file", "读取原文，返回文件名和真实行号。最多读 20 行。",
                 {"path": string, "start": {"type": "integer"}, "limit": {"type": "integer"}}, ["path"]),
        function("write_report", "写出升级清单。每项需要 id、before、after、旧版 old_source 与新版 source。引用含 path、line、quote。",
                 {"changes": {"type": "array", "items": {"type": "object", "properties": {
                     "id": string, "before": string, "after": string,
                     "old_source": {"type": "object"}, "source": {"type": "object"}},
                     "required": ["id", "before", "after", "old_source", "source"],
                     "additionalProperties": False}}}, ["changes"]),
    ]
    if stage >= 5:
        result.append(function("update_plan", "创建或调整计划。状态 pending/doing/done；reason 解释修改依据。",
                               {"steps": {"type": "array", "items": {"type": "object"}}, "reason": string}, ["steps", "reason"]))
    if stage >= 6:
        result.append(function("parallel_read", "并发读取互相独立的资料，最多四份。不是子 Agent。",
                               {"paths": {"type": "array", "items": string}}, ["paths"]))
    return result


class ToolBox:
    def __init__(self, docs, output, stage, report_format="table"):
        self.docs, self.output = Path(docs).resolve(), Path(output).resolve()
        self.stage, self.report_format = stage, report_format
        self.plan = None

    def list_files(self):
        return sorted(p.name for p in self.docs.glob("*.md") if not p.is_symlink())

    def read_file(self, path, start=1, limit=20):
        target = (self.docs / path).resolve()
        if not target.is_relative_to(self.docs) or target.suffix != ".md":
            raise ValueError("path_outside_documents")
        if type(start) is not int or type(limit) is not int or start < 1 or not 1 <= limit <= 20:
            raise ValueError("start >= 1, limit in 1..20")
        if not target.exists():
            raise FileNotFoundError(path)
        if target.stat().st_size > 100_000:
            raise ValueError("document_too_large")
        lines = target.read_text(encoding="utf-8").splitlines()
        selected = [{"line": i + 1, "text": text} for i, text in enumerate(lines)
                    if start <= i + 1 < start + limit]
        if sum(len(item["text"]) for item in selected) > 4000:
            raise ValueError("read_output_too_large: request fewer lines")
        return {"path": str(target.relative_to(self.docs)), "lines": selected,
                "next_start": start + limit if start + limit <= len(lines) else None}

    def write_report(self, changes):
        if not isinstance(changes, list) or not 1 <= len(changes) <= 12:
            raise ValueError("changes must contain 1..12 items")
        for item in changes:
            if not isinstance(item, dict) or set(item) != {"id", "before", "after", "old_source", "source"}:
                raise ValueError("invalid change fields")
            if any(not isinstance(item[k], str) or not item[k].strip() for k in ("id", "before", "after")):
                raise ValueError("id/before/after must be nonempty strings")
            for key in ("source", "old_source"):
                source = item[key]
                if (not isinstance(source, dict) or set(source) != {"path", "line", "quote"}
                        or not isinstance(source["path"], str) or type(source["line"]) is not int
                        or source["line"] < 1 or not isinstance(source["quote"], str)):
                    raise ValueError("citation needs path, positive line and quote")
        report = {"format": self.report_format, "changes": changes}
        if len(json.dumps(report, ensure_ascii=False)) > 16000:
            raise ValueError("report_too_large")
        (self.output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        def clean(value):
            return str(value).replace("|", "\\|").replace("\n", " ")
        lines = ["# Pine SDK v1 → v2 升级清单", "", "教学产品；结论以 acceptance.json 的独立检查为准。", ""]
        if self.report_format == "table":
            lines += ["| 项目 | 旧版 | 新版 | 原文位置（旧 / 新） |", "| --- | --- | --- | --- |"]
        for item in changes:
            old, new = item["old_source"], item["source"]
            location = f"{old['path']}:{old['line']} / {new['path']}:{new['line']}"
            if self.report_format == "table":
                lines.append("| " + " | ".join(clean(x) for x in (item['id'], item['before'], item['after'], location)) + " |")
            else:
                lines.append(f"- {clean(item['id'])}：{clean(item['before'])} → {clean(item['after'])}（{clean(location)}）")
        (self.output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return {"written": ["report.json", "report.md"], "note": "written does not mean verified"}

    def call(self, name, arguments):
        allowed = {tool["function"]["name"] for tool in schemas(self.stage)}
        if name not in allowed:
            raise ValueError("unknown_tool")
        if name == "update_plan":
            self.plan = update_plan(**arguments)
            return self.plan
        if name == "parallel_read":
            return read_many(self.read_file, **arguments)
        return getattr(self, name)(**arguments)
