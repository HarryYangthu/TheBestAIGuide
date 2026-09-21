"""Explicit Docker path for code execution. Requires a running Docker daemon."""
import argparse
import json
import shutil
import subprocess
import uuid
from pathlib import Path
from runtime import ROOT


def run(image, output):
    if shutil.which("docker") is None:
        raise SystemExit("docker_unavailable: install Docker and start its daemon")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    name = "agent-tools-" + uuid.uuid4().hex[:12]
    command = ["docker", "run", "--rm", "--name", name, "--network=none", "--read-only",
               "--cap-drop=ALL", "--security-opt=no-new-privileges", "--pids-limit=32",
               "--memory=128m", "--cpus=0.5", "--user=65534:65534",
               "--tmpfs=/tmp:rw,noexec,nosuid,size=16m", "--workdir=/tmp",
               "--mount", f"type=bind,src={(ROOT / 'examples').resolve()},dst=/input,readonly",
               "-i", image, "python", "-I", "/input/compute.py"]
    status = "failed"
    try:
        completed = subprocess.run(command, input=(ROOT / "examples/samples.json").read_text(encoding="utf-8"), text=True, encoding="utf-8", capture_output=True, timeout=15)
        status = "passed" if completed.returncode == 0 and json.loads(completed.stdout) == {"count": 2, "mean": 3.0} else "failed"
        result = {"status": status, "image": image, "command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
    except subprocess.TimeoutExpired:
        result = {"status": "timeout", "image": image, "command": command}
    finally:
        # Killing only the docker CLI does not guarantee its container is gone.
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=10)
    (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"container={result['status']} artifacts={output.as_posix()}")
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default="python:3.12-slim")
    parser.add_argument("--output", default="runs/container")
    args = parser.parse_args()
    run(args.image, args.output)
