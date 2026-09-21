import tempfile
import unittest
from pathlib import Path
from runtime import Registry, Tool, ToolError, build_registry, execute_python, obj, TEXT


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.registry = build_registry(self.root / "work")

    def call(self, name, **arguments):
        return self.registry.call({"id": "x", "name": name, "arguments": arguments})

    def test_bool_and_extra_arguments_rejected(self):
        for arguments in ({"query": "初始", "limit": True}, {"query": "初始", "limit": 2, "extra": 1}):
            self.assertEqual(self.call("search_docs", **arguments)["error"]["code"], "invalid_arguments")

    def test_path_escape_and_symlink_rejected(self):
        outside = self.root / "secret.txt"
        outside.write_text("not readable", encoding="utf-8")
        (self.root / "work/link").symlink_to(outside)
        for path in ("../secret.txt", "link", str(outside)):
            self.assertEqual(self.call("read_file", path=path)["error"]["code"], "path_denied")

    def test_result_contract(self):
        registry = Registry()
        registry.add(Tool("bad", "bad handler", obj(), obj(text=TEXT), lambda: {"text": 7}))
        result = registry.call({"id": "original-id", "name": "bad", "arguments": {}})
        self.assertEqual(result["call_id"], "original-id")
        self.assertEqual(result["error"]["code"], "invalid_output")

    def test_write_and_read(self):
        self.assertTrue(self.call("write_file", path="result.txt", text="补货")["ok"])
        self.assertEqual(self.call("read_file", path="result.txt")["data"]["text"], "补货")

    def test_missing_and_unknown_tool(self):
        self.assertEqual(self.call("read_file", path="missing")["error"]["code"], "not_found")
        self.assertEqual(self.call("no_tool")["error"]["code"], "unknown_tool")

    def test_child_timeout_and_nonzero(self):
        for source, code in (("import time; time.sleep(1)", "timeout"), ("raise ValueError('fixture')", "process_failed")):
            script = self.root / "case.py"
            script.write_text(source, encoding="utf-8")
            with self.assertRaises(ToolError) as error:
                execute_python(script, "", self.root, timeout=0.05 if code == "timeout" else 2)
            self.assertEqual(error.exception.code, code)

    def test_script_allowlist(self):
        self.assertEqual(self.call("run_python", script="other.py", input_path="demand.csv")["error"]["code"], "script_denied")

    def test_simulation_conserves_inventory(self):
        csv = "day,demand\n1,3\n2,5\n"
        self.call("write_file", path="demand.csv", text=csv)
        result = self.call("simulate_inventory", input_path="demand.csv", initial=4, daily_delivery=2)["data"]
        self.assertEqual(4 + 2 * 2, sum(row["sold"] for row in result["history"]) + result["ending"])
        self.assertEqual(result["lost"], 0)


if __name__ == "__main__":
    unittest.main()
