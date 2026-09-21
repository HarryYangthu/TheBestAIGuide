import copy
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from host import ROOT, header, run
from validate_output import check

spec = importlib.util.spec_from_file_location("comparison_script", ROOT / "examples/skills/release-comparison/scripts/compare.py")
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)


class SkillTests(unittest.TestCase):
    def setUp(self):
        load = lambda path: json.loads((ROOT / path).read_text(encoding="utf-8"))
        self.old = load("examples/inputs/v1.json")
        self.new = load("examples/inputs/v2.json")
        self.units = load("examples/skills/release-comparison/references/units.json")

    def test_conversion_and_equal_quantity(self):
        result = comparison.compare(self.old, self.new, "1.0", "2.0", self.units)
        self.assertEqual(result["rows"][0]["new"], 10)
        equal = copy.deepcopy(self.new)
        equal["body"] = equal["body"].replace("10000", "30000")
        equal["fields"]["timeout"].update(value=30000, quote="timeout = 30000 ms")
        result = comparison.compare(self.old, equal, "1.0", "2.0", self.units)
        self.assertFalse(result["rows"][0]["changed"])

    def test_preview_rejected(self):
        self.new["status"] = "preview"
        with self.assertRaisesRegex(ValueError, "release_mismatch"):
            comparison.compare(self.old, self.new, "1.0", "2.0", self.units)

    def test_fabricated_quote_and_missing_field(self):
        self.new["fields"]["timeout"]["quote"] = "timeout = 1 ms"
        with self.assertRaisesRegex(ValueError, "evidence_mismatch"):
            comparison.compare(self.old, self.new, "1.0", "2.0", self.units)
        del self.new["fields"]["timeout"]
        with self.assertRaises(KeyError):
            comparison.compare(self.old, self.new, "1.0", "2.0", self.units)

    def test_dimensions(self):
        self.units["ms"]["canonical"] = "items"
        with self.assertRaisesRegex(ValueError, "incompatible_dimensions"):
            comparison.compare(self.old, self.new, "1.0", "2.0", self.units)

    def test_polish_does_not_load_method(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run(Path(directory) / "polish", task="polish")
            self.assertEqual(result["loaded_files"], ["catalog"])
            self.assertFalse((Path(directory) / "polish/comparison").exists())

    def test_corrupted_artifact_fails_acceptance(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "compare"
            result = run(output)
            self.assertTrue(result["acceptance"])
            artifact = output / "comparison/comparison.json"
            data = json.loads(artifact.read_text(encoding="utf-8"))
            data["rows"][0]["new"] = 10000
            artifact.write_text(json.dumps(data), encoding="utf-8")
            self.assertFalse(check(output / "comparison", self.old, self.new)["passed"])

    def test_unchanged_units_skip_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            new = copy.deepcopy(self.new)
            new["body"] = new["body"].replace("10000 ms", "10 s")
            new["fields"]["timeout"].update(value=10, unit="s", quote="timeout = 10 s")
            source = Path(directory) / "new.json"
            source.write_text(json.dumps(new), encoding="utf-8")
            result = run(Path(directory) / "run", new_path=source)
            self.assertTrue(result["acceptance"])
            self.assertNotIn("references/units.json", result["loaded_files"])

    def test_wrong_report_product_or_version_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            run(output)
            report = output / "comparison/report.md"
            text = report.read_text(encoding="utf-8")
            report.write_text(text.replace("# Pine Example SDK：1.0 → 2.0", "# Other SDK：9 → 10"), encoding="utf-8")
            result = check(output / "comparison", self.old, self.new)
            self.assertFalse(result["passed"])
            self.assertFalse(result["checks"]["report_title"])

    def test_missing_files_bad_json_and_shapes_return_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            self.assertFalse(check(output, self.old, self.new)["passed"])
            (output / "report.md").write_text("# report\n", encoding="utf-8")
            for content in ("not-json", "[]", "{}", '{"old_version":"1.0"}'):
                (output / "comparison.json").write_text(content, encoding="utf-8")
                self.assertFalse(check(output, self.old, self.new)["passed"])

    def test_host_saves_failure_trace_when_artifact_missing_field(self):
        import subprocess
        real_run = subprocess.run

        def corrupt(command, **kwargs):
            result = real_run(command, **kwargs)
            output = Path(command[command.index("--output") + 1])
            artifact = output / "comparison.json"
            data = json.loads(artifact.read_text(encoding="utf-8"))
            del data["new_version"]
            artifact.write_text(json.dumps(data), encoding="utf-8")
            return result

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            with patch("host.subprocess.run", side_effect=corrupt):
                result = run(output)
            self.assertEqual(result["status"], "acceptance_failed")
            for path in ("trace.json", "result.json", "comparison/acceptance.json"):
                self.assertTrue((output / path).exists())


if __name__ == "__main__":
    unittest.main()
