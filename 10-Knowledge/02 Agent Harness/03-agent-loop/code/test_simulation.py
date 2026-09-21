"""Verify the simulation artifacts, not just the repair declaration."""
import json
import tempfile
import unittest
from shared import FIXED_SOURCE, check_tests, create_workspace, run_python, write_file


class SimulationTests(unittest.TestCase):
    def test_repaired_code_requires_actual_execution(self):
        with tempfile.TemporaryDirectory() as path:
            workspace = create_workspace(path)
            write_file(workspace, "stats.py", FIXED_SOURCE)
            self.assertFalse(check_tests(workspace)["passed"])
            result = run_python(workspace, "simulate.py")
            self.assertEqual(result["exit_code"], 0)
            self.assertTrue(check_tests(workspace)["passed"])
            output = workspace / "runs/simulation"
            metrics = json.loads((output / "metrics.json").read_text())
            self.assertLess(metrics["output_mse"], metrics["input_mse"])
            self.assertEqual(len((output / "samples.csv").read_text().splitlines()), 65)
            # A plausible report cannot disguise tampered numeric evidence.
            metrics["output_mse"] = 0.001
            (output / "metrics.json").write_text(json.dumps(metrics))
            self.assertFalse(check_tests(workspace)["passed"])
            run_python(workspace, "simulate.py")
            rows = (output / "samples.csv").read_text().splitlines()
            rows[1] = "0,0,0.3,999"
            (output / "samples.csv").write_text("\n".join(rows) + "\n")
            self.assertFalse(check_tests(workspace)["passed"])

    def test_config_and_script_are_not_repair_targets(self):
        with tempfile.TemporaryDirectory() as path:
            workspace = create_workspace(path)
            with self.assertRaises(ValueError):
                write_file(workspace, "simulation.json", "{}")
            with self.assertRaises(ValueError):
                run_python(workspace, "other.py")


if __name__ == "__main__":
    unittest.main()
