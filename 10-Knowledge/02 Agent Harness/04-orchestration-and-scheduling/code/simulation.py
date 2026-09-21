"""Run the actual simulation in a child process; retain its output files."""
import asyncio
import json
import sys
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

async def run_simulation():
    with tempfile.TemporaryDirectory() as temp:
        output = Path(temp) / "simulation"
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-I", str(ROOT / "simulate.py"),
            "--config", str(ROOT / "simulation.json"), "--output", str(output),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            env={"PYTHONIOENCODING": "utf-8"})
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
        finally:
            if process.returncode is None:
                process.kill()
                await process.wait()
        if process.returncode:
            raise RuntimeError("simulation process failed: " + stderr.decode())
        files = {p.name: p.read_text(encoding="utf-8") for p in output.iterdir()}
        metrics = json.loads(files["metrics.json"])
        return {"exit_code": process.returncode, "metrics": metrics, "files": files}

def save_simulation(output, result):
    target = Path(output) / "simulation"
    target.mkdir(parents=True, exist_ok=True)
    for name, content in result["files"].items():
        (target / name).write_text(content, encoding="utf-8")
