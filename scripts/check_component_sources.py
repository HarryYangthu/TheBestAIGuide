#!/usr/bin/env python3
"""Run the source-snapshot checks shipped with the current component chapters."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    checks = []
    for chapter in sorted((ROOT / "10-Knowledge").glob("[0-9][0-9]-*")):
        for relative in ("code/verify_sources.py", "sources/verify_sources.py"):
            script = chapter / relative
            if not script.is_file():
                continue
            result = subprocess.run(
                [sys.executable, str(script)], cwd=chapter,
                text=True, capture_output=True, timeout=60,
            )
            checks.append({"chapter": chapter.name, "script": relative,
                           "returncode": result.returncode,
                           "output": (result.stdout + result.stderr).strip()})
    print(json.dumps({"checks": checks, "failed": sum(bool(c["returncode"]) for c in checks)},
                     ensure_ascii=False, indent=2))
    return not checks or any(c["returncode"] for c in checks)


if __name__ == "__main__":
    raise SystemExit(main())
