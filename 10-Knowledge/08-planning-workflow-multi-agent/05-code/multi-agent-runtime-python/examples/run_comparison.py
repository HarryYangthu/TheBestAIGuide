"""在工程目录执行 PYTHONPATH=src python examples/run_comparison.py。"""
import asyncio
import json
from multi_agent.fixture import experiment

if __name__ == "__main__":
    print(json.dumps(asyncio.run(experiment()), ensure_ascii=False, indent=2))
