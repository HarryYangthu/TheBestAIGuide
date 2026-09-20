"""读取随章节提供的 notes.txt，并保存一份输入副本。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "notes.txt").read_text(encoding="utf-8")
output = ROOT / "runs" / "input-preview.txt"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(text, encoding="utf-8")
print(text, end="" if text.endswith("\n") else "\n")
print("saved=runs/input-preview.txt")
