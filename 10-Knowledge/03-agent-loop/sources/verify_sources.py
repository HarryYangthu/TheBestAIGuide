"""Verify the bundled original source bytes and exact Markdown excerpts offline."""
from pathlib import Path
import argparse
import hashlib
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--save', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / 'source-manifest.json').read_text())
    paths = {}
    for item in manifest['snapshots']:
        path = root / item['snapshot_file']
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == item['sha256'], path
        git_blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        assert hashlib.sha1(git_blob).hexdigest() == item['git_blob_sha'], path
        paths[item['upstream_path']] = path
    for item in manifest['excerpts']:
        lines = paths[item['upstream_path']].read_bytes().splitlines(keepends=True)
        original = b''.join(lines[item['start_line'] - 1:item['end_line']])
        excerpt = (root / item['excerpt_file']).read_bytes()
        assert original == excerpt, item['id']
        assert hashlib.sha256(excerpt).hexdigest() == item['excerpt_sha256'], item['id']
        document = (root / item['document']).read_text()
        assert document.count(item['begin_marker']) == 1, item['id']
        assert document.count(item['end_marker']) == 1, item['id']
        actual = document.split(item['begin_marker'], 1)[1].split(item['end_marker'], 1)[0]
        assert actual == '\n```python\n' + excerpt.decode() + '```\n', item['id']
    assert hashlib.sha256((root / 'LICENSE.OpenHands').read_bytes()).hexdigest() == manifest['license_sha256']
    print(f"PASS: {len(manifest['snapshots'])} source files; {len(manifest['excerpts'])} excerpts; matching Markdown; MIT license.")
    print('This is local integrity verification, not remote provenance or SDK execution verification.')
    if args.save:
        output = root.parent / 'runs'
        output.mkdir(exist_ok=True)
        audit = {'passed': True, 'source_files': len(manifest['snapshots']),
                 'excerpts': len(manifest['excerpts']),
                 'commit': 'd128a786ee2ee570eb23ff5862ec148b43cfad0b',
                 'checks': ['sha256', 'git_blob_sha', 'excerpt_bytes', 'markdown_excerpt', 'license'],
                 'scope': 'local_source_integrity'}
        (output / 'source-audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        report = ['# 源码校验记录', '', f"提交：`{audit['commit']}`", '',
                  '| 检查项 | 结果 |', '|---|---|',
                  '| 原始文件 | 6 份通过 |', '| 原始切片 | 8 段通过 |',
                  '| 正文摘录 | 与切片一致 |', '| MIT 许可证 | 摘要一致 |', '',
                  '校验范围：本地资料完整性。', '']
        (output / 'source-audit.md').write_text('\n'.join(report), encoding='utf-8')
        print('saved=runs/source-audit.md, runs/source-audit.json')


if __name__ == '__main__':
    main()
