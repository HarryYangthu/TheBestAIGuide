"""Trusted fixture: read CSV from stdin; return a JSON summary to stdout."""
import csv
import io
import json
import sys

rows = list(csv.DictReader(io.StringIO(sys.stdin.read())))
values = [int(row["demand"]) for row in rows]
print(json.dumps({"days": len(values), "total": sum(values), "maximum": max(values)}))
