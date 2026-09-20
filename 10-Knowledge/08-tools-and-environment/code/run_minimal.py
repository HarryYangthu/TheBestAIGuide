from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / "examples/corpus/policy.md"
lines = source.read_text(encoding="utf-8").splitlines()
matches = [f"policy.md:{i}: {line}" for i, line in enumerate(lines, 1) if "初始库存" in line]
output = root / "runs/minimal.txt"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text("\n".join(matches) + "\n", encoding="utf-8")
print("\n".join(matches))
print("saved=runs/minimal.txt")
