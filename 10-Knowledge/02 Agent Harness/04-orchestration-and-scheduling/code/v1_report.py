"""Run from the chapter directory; read notes and check the local mean function."""
import json
import asyncio
from simulation import run_simulation, save_simulation
from pathlib import Path
from stats import mean


def main():
    notes = Path("fixtures/notes.txt").read_text(encoding="utf-8")
    cases = json.loads(Path("fixtures/cases-v1.json").read_text(encoding="utf-8"))["cases"]
    passed = sum(mean(c["values"]) == c["expected"] for c in cases)
    output = Path("runs/v1")
    output.mkdir(parents=True, exist_ok=True)
    simulation = asyncio.run(run_simulation())
    save_simulation(output, simulation)
    (output / "result.json").write_text(json.dumps({"passed_checks": passed, "simulation": simulation["metrics"]}) + "\n", encoding="utf-8")
    (output / "report.md").write_text(f"# 检查报告\n\n{notes}\n通过 {passed}/{len(cases)}。\n\n[仿真报告](simulation/report.md)\n", encoding="utf-8")
    print(f"passed_checks={passed}")
    print("artifacts=runs/v1")


if __name__ == "__main__":
    main()
