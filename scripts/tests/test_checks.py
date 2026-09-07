import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from check_links import check

class LinkChecks(unittest.TestCase):
    def test_missing_target_and_fenced_example_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'README.md').write_text('# Index\n[missing](absent.md)\n```markdown\n[example](template.md)\n```\n[external](https://example.com)\n')
            result=check(root)
            self.assertEqual([e['target'] for e in result['errors']],['absent.md'])
            self.assertEqual(result['external_urls_not_requested'],1)
    def test_relative_target_and_notebook_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            import json
            root=Path(tmp); (root/'chapter').mkdir()
            (root/'README.md').write_text('# Index\n')
            (root/'chapter/a.md').write_text('# A\n[home](../README.md)\n')
            (root/'chapter/lab.ipynb').write_text(json.dumps({'cells':[{'cell_type':'markdown','source':['[home](../README.md)']}]}))
            result=check(root)
            self.assertEqual(result['errors'],[])
            self.assertEqual(result['local_targets_checked'],2)

    def test_unicode_duplicate_and_missing_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'a.md').write_text('# 中文标题\n# 中文标题\n# Code `x`\n')
            (root/'README.md').write_text('[ok](a.md#中文标题)\n[repeat](a.md#中文标题-1)\n[code](a.md#code-x)\n[bad](a.md#不存在)\n')
            result=check(root)
            self.assertEqual([e['target'] for e in result['errors']],['a.md#不存在'])

if __name__ == '__main__': unittest.main()
