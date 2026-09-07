#!/usr/bin/env python3
"""Validate explicit article status without treating templates as unfinished work."""
import json
import re
from pathlib import Path
from check_links import ROOT, documents, visible_markdown

def check():
    errors = []
    articles = 0
    for path, text in documents():
        rel = path.relative_to(ROOT)
        if path.suffix != '.md' or 'templates' in rel.parts:
            continue
        text = visible_markdown(text)
        if not re.search(r'^#\s+\S', text, re.M):
            errors.append({'file': str(rel), 'reason': 'missing document title'})
        if rel.parts[0] != '10-Knowledge' or path.name == 'README.md':
            continue
        if not any(part in rel.parts for part in ['01-concepts', '02-patterns', '03-cases']):
            continue
        articles += 1
        status = re.search(r'^>\s*状态[：:]\s*(seed|draft|reviewed|verified)\b', text, re.M)
        if not status:
            errors.append({'file': str(rel), 'reason': 'missing or invalid article status'})
        if status and status.group(1) == 'verified' and not re.search(r'验证|运行|执行', text):
            errors.append({'file': str(rel), 'reason': 'verified needs a stated validation scope'})
    return {'articles_checked': articles, 'errors': errors, 'note': 'This validates metadata, not factual accuracy or human review.'}

if __name__ == '__main__':
    result = check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result['errors']))
