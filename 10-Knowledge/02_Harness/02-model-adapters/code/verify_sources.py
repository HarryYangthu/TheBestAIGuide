"""Verify stored source hashes and equality to the installed pinned SDK."""
import hashlib
from importlib.metadata import distribution
import json
from adapter import ROOT
root = ROOT / "sources"
manifest = json.loads((root / "manifest.json").read_text())
dist = distribution(manifest["distribution"])
assert dist.version == manifest["version"], "SDK 版本与快照不同"
for item in manifest["entries"]:
    local = (root / item["file"]).read_bytes()
    assert hashlib.sha256(local).hexdigest() == item["sha256"]
    assert local == dist.locate_file(item["upstream_path"]).read_bytes(), item["file"]
print(f"sources={len(manifest['entries'])} version={manifest['version']} matched=true")
