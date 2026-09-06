#!/usr/bin/env python3
"""Check local Markdown/Notebook link targets. Does not request external URLs."""
from __future__ import annotations
import argparse
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'.git', '.venv', 'node_modules', '__pycache__', 'dist', 'build'}

def visible_markdown(text):
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            lines.append('')
        elif fence:
            lines.append('')
        else:
            lines.append(line)
    return '\n'.join(lines)

def documents(root=ROOT):
    for path in sorted(root.rglob('*')):
        if any(part in SKIP for part in path.relative_to(root).parts):
            continue
        if path.suffix == '.md':
            yield path, path.read_text(encoding='utf-8')
        elif path.suffix == '.ipynb':
            notebook = json.loads(path.read_text(encoding='utf-8'))
            yield path, '\n'.join(''.join(c.get('source', [])) for c in notebook['cells'] if c['cell_type'] == 'markdown')

def heading_anchors(text):
    """GitHub-like slugs for this repo's ATX/Setext headings and explicit IDs.

    Raw HTML, punctuation and formatting are removed; Unicode letters/marks,
    numbers, spaces, underscores and hyphens remain. Duplicate suffixes are
    allocated globally, including collisions with already suffixed titles.
    This is intentionally not a complete Markdown renderer.
    """
    text = visible_markdown(text)
    anchors=set(re.findall(r'(?:id|name)=["\']([^"\']+)["\']', text))
    headings=[];lines=text.splitlines()
    for i,line in enumerate(lines):
        m=re.match(r'^ {0,3}#{1,6}\s+(.+?)\s*#*$',line)
        if m:headings.append(m[1])
        elif i and re.fullmatch(r' {0,3}(?:=+|-+)\s*',line) and lines[i-1].strip():headings.append(lines[i-1])
    for title in headings:
        title=re.sub(r'<[^>]*>', '', title)
        title=re.sub(r'!?\[([^\]]+)\]\([^)]*\)',r'\1',title).lower()
        base=''.join(c for c in title if c in ' _-' or unicodedata.category(c)[0] in 'LNM').replace(' ','-')
        slug=base;n=0
        while slug in anchors:n+=1;slug=f'{base}-{n}'
        anchors.add(slug)
    return anchors

def check(root=ROOT):
    errors, checked, external, doc_count = [], 0, set(), 0
    for path, text in documents(root):
        doc_count += 1
        text = visible_markdown(text)
        # Inline destinations plus reference definitions; fenced examples are excluded.
        links = [(m.group(1), text[:m.start()].count('\n')+1) for m in re.finditer(r'!?\[[^\]]*\]\(<?([^\s>)]+)>?(?:\s+"[^"]*")?\)', text)]
        links += [(m.group(1), text[:m.start()].count('\n')+1) for m in re.finditer(r'^\s*\[[^\]]+\]:\s*<?([^\s>]+)>?', text, re.M)]
        for target, line in links:
            url = urlsplit(target)
            if url.scheme or target.startswith('//'):
                if url.scheme in {'http', 'https'}:
                    external.add(target)
                continue
            checked += 1
            dest = path if not url.path else (root / unquote(url.path).lstrip('/') if url.path.startswith('/') else path.parent / unquote(url.path))
            dest = dest.resolve()
            if not dest.is_relative_to(root.resolve()) or not dest.exists():
                errors.append({'file': str(path.relative_to(root)), 'line': line, 'target': target})
            elif url.fragment and dest.suffix == '.md' and unquote(url.fragment) not in heading_anchors(dest.read_text(encoding='utf-8')):
                errors.append({'file':str(path.relative_to(root)), 'line':line, 'target':target, 'reason':'missing_heading'})
    return {'documents': doc_count, 'local_targets_checked': checked, 'external_urls_not_requested': len(external), 'errors': errors}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    result = check(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result['errors']))
