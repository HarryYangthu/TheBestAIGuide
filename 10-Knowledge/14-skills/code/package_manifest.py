import argparse
import hashlib
import json
from pathlib import Path
from host import ROOT, header

parser = argparse.ArgumentParser()
parser.add_argument("--output", default="runs/package-manifest.json")
args = parser.parse_args()
packages = []
for relative in ("examples/skills-v1/notes-comparison", "examples/skills/notes-comparison"):
    root = ROOT / relative
    files = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in sorted(root.rglob("*")) if path.is_file() and "__pycache__" not in path.parts}
    packages.append({"path": relative, **header(root / "SKILL.md"), "files": files})
output = Path(args.output)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(packages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"packages={len(packages)} artifacts={output.as_posix()}")
