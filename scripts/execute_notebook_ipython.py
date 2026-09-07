#!/usr/bin/env python3
"""Actual cell execution when socket-based kernels are unavailable.

One process per notebook; deliberately not a full Jupyter kernel protocol test.
Invoked by check_notebooks.py --execute --backend ipython-fallback.
"""
from pathlib import Path
import os
import sys
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output


def main():
    path = Path(sys.argv[1]).resolve()
    os.chdir(path.parent)
    nb = nbformat.read(path, as_version=4)
    shell = InteractiveShell.instance()
    count = 0
    for cell in nb.cells:
        if cell.cell_type != 'code':
            continue
        count += 1
        with capture_output() as captured:
            result = shell.run_cell(cell.source, store_history=True)
        if result.error_before_exec or result.error_in_exec:
            print(captured.stdout, captured.stderr, file=sys.stderr)
            raise result.error_before_exec or result.error_in_exec
        cell.execution_count = count
        cell.outputs = []
        if captured.stdout:
            cell.outputs.append(nbformat.v4.new_output('stream', name='stdout', text=captured.stdout))
        if captured.stderr:
            cell.outputs.append(nbformat.v4.new_output('stream', name='stderr', text=captured.stderr))
        for output in captured.outputs:
            cell.outputs.append(nbformat.v4.new_output('display_data', data=output.data, metadata=output.metadata))
    nb.metadata.setdefault('aiguide', {})['execution_backend'] = 'ipython-fallback'
    nb.metadata['aiguide']['execution_limit'] = 'Cells executed in a fresh process; Jupyter kernel transport not tested.'
    nb.metadata.setdefault('language_info', {})['version'] = sys.version.split()[0]
    nbformat.validate(nb)
    nbformat.write(nb, path)
    print(f'{path.name}: {count} code cells executed through IPython')


if __name__ == '__main__':
    main()
