"""Verify saved standard-library files against their recorded SHA-256."""
import hashlib
import json
from pathlib import Path
root = Path(__file__).resolve().parent
manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
for name, expected in manifest["files"].items():
    actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"hash mismatch: {name}")
print(f"verified={len(manifest['files'])} runtime={manifest['runtime']}")
