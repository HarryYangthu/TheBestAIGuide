"""Read numeric samples from stdin and check the same mean operation as Agent Loop."""
import json
import sys


def mean(values):
    if not values:
        raise ValueError("values must not be empty")
    return sum(values) / len(values)


values = json.loads(sys.stdin.read())
print(json.dumps({"count": len(values), "mean": mean(values)}))
