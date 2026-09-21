"""Run the shared signal simulation from this chapter directory."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    core = root / "simulation_core.py"
    if not core.is_file():
        core = root.parent / "_shared" / "simulation_core.py"
    runpy.run_path(str(core))["main"](script_dir=root)
