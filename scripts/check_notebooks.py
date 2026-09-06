#!/usr/bin/env python3
"""Validate notebooks; optionally execute in clean kernels and save real outputs."""
import argparse
import json
import sys
import subprocess
from pathlib import Path
from check_links import ROOT, SKIP

def run(execute=False, selected=None, backend='jupyter'):
    import nbformat
    from nbclient import NotebookClient
    paths = [Path(p).resolve() for p in selected] if selected else sorted(ROOT.rglob('*.ipynb'))
    results = []
    for path in paths:
        if any(part in SKIP for part in path.relative_to(ROOT).parts):
            continue
        item = {'file': str(path.relative_to(ROOT))}
        try:
            nb = nbformat.read(path, as_version=4)
            nbformat.validate(nb)
            code = [c for c in nb.cells if c.cell_type == 'code' and any(line.strip() and not line.lstrip().startswith('#') for line in c.source.splitlines())]
            if not code:
                raise ValueError('No executable code cells')
            if execute:
                if backend == 'ipython-fallback':
                    subprocess.run([sys.executable, str(ROOT / 'scripts/execute_notebook_ipython.py'), str(path)],
                                   check=True, timeout=600, capture_output=True, text=True)
                    nb = nbformat.read(path, as_version=4)
                else:
                    client = NotebookClient(nb, timeout=180, kernel_name='python3', resources={'metadata': {'path': str(path.parent)}})
                    client.execute()
                    nb.metadata.setdefault('aiguide', {})['execution_backend'] = 'jupyter-nbclient'
                    nbformat.write(nb, path)
                code = [c for c in nb.cells if c.cell_type == 'code' and c.source.strip()]
            error_cells = [i for i,c in enumerate(nb.cells) if c.cell_type == 'code' and any(o.output_type == 'error' for o in c.outputs)]
            if error_cells:
                raise ValueError(f'Error outputs in cells {error_cells}')
            item.update(status='executed' if execute else 'format-valid', code_cells=len(code), executed_code_cells=sum(c.execution_count is not None for c in code))
            if execute:
                item['backend'] = backend
        except Exception as exc:
            item.update(status='failed', error=f'{type(exc).__name__}: {exc}')
        results.append(item)
        print(json.dumps(item, ensure_ascii=False), flush=True)
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--backend', choices=['jupyter', 'ipython-fallback'], default='jupyter',
                        help='Explicit fallback executes cells in a fresh IPython process without kernel sockets')
    parser.add_argument('paths', nargs='*')
    args = parser.parse_args()
    results = run(args.execute, args.paths, args.backend)
    raise SystemExit(any(r['status']=='failed' for r in results))
