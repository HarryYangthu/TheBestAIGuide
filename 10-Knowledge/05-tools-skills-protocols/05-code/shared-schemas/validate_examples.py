"""Run from this folder: python validate_examples.py (jsonschema required)."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator

root = Path(__file__).parent
count = 0
for path in sorted(root.glob("*.schema.json")):
    name = path.name.removesuffix(".schema.json")
    schema = json.loads(path.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    for kind in ["valid", "invalid"]:
        sample = json.loads((root / "examples" / f"{name}.{kind}.json").read_text())
        valid = validator.is_valid(sample)
        assert valid == (kind == "valid"), (name, kind)
        count += 1
print(f"Python JSON Schema checks passed: {count}")
