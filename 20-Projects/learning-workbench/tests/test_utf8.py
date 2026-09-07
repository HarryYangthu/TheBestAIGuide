"""Teaching fixtures and saved reports must not depend on the OS locale."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class UTF8FilesTests(unittest.TestCase):
    def test_cli_reads_chinese_fixtures_without_utf8_mode(self):
        root = next(p for p in Path(__file__).resolve().parents if (p / 'scripts/run_python.py').is_file())
        env = dict(os.environ, PYTHONUTF8='0', PYTHONCOERCECLOCALE='0', LC_ALL='C')
        with tempfile.TemporaryDirectory(prefix='aiguide-utf8-') as output:
            for task in ['memory', 'documents']:
                result = subprocess.run(
                    [sys.executable, '-X', 'utf8=0', str(root / 'scripts/run_python.py'),
                     '-m', 'learning_workbench.cli', task, '--output', output],
                    cwd=root, env=env, capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', errors='replace'))
                report = Path(json.loads(result.stdout.decode('ascii'))['report'])
                self.assertTrue(json.loads(report.read_text(encoding='utf-8')))


if __name__ == '__main__':
    unittest.main()
