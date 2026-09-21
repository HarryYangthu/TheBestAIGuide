"""Verify saved source bytes; no network access."""
import hashlib
import json
from pathlib import Path
root = Path(__file__).resolve().parent
manifest = json.loads((root / "manifest.json").read_text())
for record in manifest["files"]:
    actual = hashlib.sha256((root / record["path"]).read_bytes()).hexdigest()
    if actual != record["sha256"]:
        raise SystemExit("hash mismatch: " + record["path"])
print("verified=" + str(len(manifest["files"])))
