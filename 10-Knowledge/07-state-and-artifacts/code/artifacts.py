"""Content-addressed files and dependency metadata; Python standard library only."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Artifacts:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, kind, data, suffix=".json", dependencies=None):
        if isinstance(data, str):
            data = data.encode()
        meta = {"schema_version": 1, "kind": kind, "payload": "payload" + suffix,
                "sha256": sha(data), "dependencies": dependencies or {}}
        ident = sha(canonical(meta))
        target = self.root / ident
        staging = Path(tempfile.mkdtemp(prefix=".staging-", dir=self.root))
        try:
            (staging / meta["payload"]).write_bytes(data)
            (staging / "meta.json").write_bytes(canonical(meta))
            try:
                os.rename(staging, target)
            except OSError:
                if not target.is_dir():
                    raise
                # A same-content concurrent writer may have published first.
                self.verify(ident)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
        return ident

    def metadata(self, ident):
        # IDs come from metadata, never accept paths supplied by tools.
        if len(ident) != 64 or any(c not in "0123456789abcdef" for c in ident):
            raise ValueError("invalid artifact id")
        return json.loads((self.root / ident / "meta.json").read_text())

    def verify(self, ident, seen=None):
        seen = set() if seen is None else seen
        if ident in seen:
            return
        meta = self.metadata(ident)
        if sha(canonical(meta)) != ident:
            raise ValueError("metadata mismatch")
        path = self.root / ident / meta["payload"]
        if sha(path.read_bytes()) != meta["sha256"]:
            raise ValueError("payload mismatch")
        seen.add(ident)
        for dependency in meta["dependencies"].values():
            self.verify(dependency, seen)

    def read(self, ident):
        self.verify(ident)
        meta = self.metadata(ident)
        return (self.root / ident / meta["payload"]).read_bytes()

    def stale(self, ident, current):
        """Return changed direct dependencies, not a claim about semantic validity."""
        meta = self.metadata(ident)
        return sorted(name for name, ref in meta["dependencies"].items()
                      if name in current and current[name] != ref)
