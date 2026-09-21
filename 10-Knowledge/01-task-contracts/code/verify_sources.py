"""Compare stored excerpts to the installed, pinned dependency."""
import hashlib
import importlib
from importlib.metadata import version
import inspect
import json
from contracts import ROOT
root = ROOT / "sources"
manifest = json.loads((root / "manifest.json").read_text())
assert version(manifest["distribution"]) == manifest["version"], "依赖版本与快照不同"
for item in manifest["entries"]:
    local = (root / item["file"]).read_bytes()
    current = inspect.getsource(getattr(importlib.import_module(item["module"]), item["symbol"])).encode()
    assert hashlib.sha256(local).hexdigest() == item["sha256"]
    assert local == current, item["file"]
print(f"sources={len(manifest['entries'])} version={manifest['version']} matched=true")
