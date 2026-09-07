"""Preserve structured blocks and source offsets before retrieval."""
from dataclasses import asdict, dataclass
from hashlib import sha256
import re


@dataclass(frozen=True)
class Block:
    source: str
    version: str
    kind: str
    text: str
    start: int
    end: int
    heading: tuple
    parent: str
    block_id: str


def markdown_blocks(text, source='document', version='1'):
    """A deliberately small block parser: headings, fenced code, pipe tables, prose.

    It preserves code/table units; it is not a full CommonMark AST implementation.
    Oversized atomic blocks are reported intact so the caller chooses a policy.
    """
    lines = text.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    result, heading, i = [], [], 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        begin = i
        h = re.match(r'^(#{1,6})\s+(.*)', lines[i])
        if h:
            depth = len(h[1]); heading = heading[:depth-1] + [h[2].strip()]
            kind = 'heading'; i += 1
        elif re.match(r'^\s{0,3}(`{3,}|~{3,})', lines[i]):
            fence = re.match(r'^\s{0,3}(`{3,}|~{3,})', lines[i])[1]
            kind = 'code'; i += 1
            while i < len(lines):
                close = lines[i].lstrip().startswith(fence); i += 1
                if close: break
        elif lines[i].lstrip().startswith('|'):
            kind = 'table'; i += 1
            while i < len(lines) and lines[i].lstrip().startswith('|'): i += 1
        else:
            kind = 'paragraph'; i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r'^(#{1,6}\s|\s{0,3}```|\s{0,3}~~~|\s*\|)', lines[i]): i += 1
        start, end = offsets[begin], offsets[i]
        parent = '/'.join(heading)
        identity = sha256(f'{source}\0{version}\0{start}\0{end}\0{text[start:end]}'.encode()).hexdigest()[:16]
        result.append(Block(source, version, kind, text[start:end], start, end,
                            tuple(heading), parent, identity))
    return result


def parent_evidence(block, all_blocks):
    return [b for b in all_blocks if (b.source, b.version, b.parent) == (block.source, block.version, block.parent)]


def parse_pdf(path):
    from pypdf import PdfReader
    from pathlib import Path
    path = Path(path)
    digest = sha256(path.read_bytes()).hexdigest()
    reader = PdfReader(str(path))
    return [{'source': path.name, 'sha256': digest, 'page': i + 1,
             'text': page.extract_text() or '', 'parser': 'pypdf',
             'requires_ocr': not bool((page.extract_text() or '').strip())}
            for i, page in enumerate(reader.pages)]


def error_rate(reference, hypothesis, *, characters=False):
    """Edit distance alignment; insertion count may make WER exceed one."""
    a = list(reference) if characters else reference.split()
    b = list(hypothesis) if characters else hypothesis.split()
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1): dp[i][0] = i
    for j in range(len(b) + 1): dp[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1,
                           dp[i-1][j-1] + (a[i-1] != b[j-1]))
    if not a: raise ValueError('empty reference has undefined normalized error')
    return {'edits': dp[-1][-1], 'reference_units': len(a), 'rate': dp[-1][-1] / len(a)}
