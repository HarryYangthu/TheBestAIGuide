#!/usr/bin/env python3
"""Run a module or script with this repository's teaching packages on sys.path."""
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", "node_modules", "__pycache__", "dist", "build"}
for path in sorted(ROOT.rglob("src")):
    if path.is_dir() and not SKIP.intersection(path.relative_to(ROOT).parts):
        sys.path.insert(0, str(path))

if len(sys.argv) < 2:
    raise SystemExit("usage: python scripts/run_python.py [-m module | script.py] [arguments]")
if sys.argv[1] == "-m":
    if len(sys.argv) < 3:
        raise SystemExit("-m requires a module name")
    module = sys.argv[2]
    sys.argv = [module] + sys.argv[3:]
    runpy.run_module(module, run_name="__main__", alter_sys=True)
else:
    sys.argv = sys.argv[1:]
    runpy.run_path(sys.argv[0], run_name="__main__")
