"""Verify the downloaded, pinned CPython files without network access."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / "manifest.json").read_text())
for entry in manifest["files"]:
    actual = hashlib.sha256((root / entry["local"]).read_bytes()).hexdigest()
    if actual != entry["sha256"]:
        raise SystemExit("hash mismatch: " + entry["local"])
print(f"verified={len(manifest['files'])} tag={manifest['tag']}")
