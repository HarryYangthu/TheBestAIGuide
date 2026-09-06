#!/usr/bin/env python3
"""Run each teaching project's unittest suite in a separate Python process."""
import json
import os
import subprocess
import sys
from pathlib import Path
from check_links import ROOT, SKIP

def main():
    sources = [str(p) for p in ROOT.rglob('src') if p.is_dir() and not any(x in SKIP for x in p.relative_to(ROOT).parts)]
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(sources))
    suites = sorted({p.parent for p in ROOT.rglob('test_*.py')
                     if not any(x in SKIP for x in p.relative_to(ROOT).parts)})
    failed = 0
    for suite in suites:
        result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(suite), '-v'], cwd=suite, env=env, text=True, capture_output=True)
        print(json.dumps({'suite': str(suite.relative_to(ROOT)), 'returncode':result.returncode}, ensure_ascii=False), flush=True)
        print(result.stdout + result.stderr, flush=True)
        failed += bool(result.returncode)
    examples = [
        '10-Knowledge/14-production-engineering/05-code/production_checks.py',
        '10-Knowledge/16-research-frontiers/05-code/research_checks.py',
    ]
    for example in examples:
        result = subprocess.run([sys.executable, str(ROOT / example)], env=env, text=True, capture_output=True)
        print(json.dumps({'assertion_example': example, 'returncode': result.returncode}), flush=True)
        print(result.stdout + result.stderr, flush=True)
        failed += bool(result.returncode)
    print(json.dumps({'suites':len(suites), 'assertion_examples':len(examples), 'failed_groups':failed}))
    return bool(failed) or not suites

if __name__ == '__main__':
    raise SystemExit(main())
