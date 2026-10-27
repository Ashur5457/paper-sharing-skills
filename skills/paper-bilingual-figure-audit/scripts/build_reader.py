#!/usr/bin/env python3
"""Make a fully offline single-file bilingual manuscript / SI figure reader.

Requires Python 3.10+; all dependencies are standard-library.
"""
from __future__ import annotations
import argparse
import base64
import html
import json
import mimetypes
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'references' / 'reader-template.html'


def audit_data(d: dict) -> list[str]:
    errors = []
    meta = d.get('meta', {})
    sections = d.get('sections', [])
    if not meta.get('title_zh') or not meta.get('title_en'):
        errors.append('Missing bilingual title')
    if not sections:
        errors.append('Missing sections')
    for sec in sections:
        if not sec.get('title_zh', '').strip() or not sec.get('title_en', '').strip():
            errors.append(f'Section {sec.get("id")}: missing bilingual heading')
    seen = set()
    blocks = 0
    for sec in sections:
        for b in sec.get('blocks', []):
            blocks += 1
            bid = b.get('id')
            if not bid or bid in seen:
                errors.append(f'Empty or duplicate block id: {bid!r}')
            seen.add(bid)
            if not b.get('en', '').strip():
                errors.append(f'No original English text in {bid}')
            if not b.get('zh', '').strip():
                errors.append(f'Missing Chinese translation in {bid}')
    figids = set()
    for f in d.get('figures', []):
        fid = f.get('id')
        if not fid or fid in figids:
            errors.append(f'Empty/duplicate figure ID: {fid}')
        figids.add(fid)
        if f.get('group') not in ('main', 'si'):
            errors.append(f'{fid}: figure group must be main or si')
        if f.get('verified') is not True:
            print(f'WARNING {fid}: caption/image matching not visually verified', file=sys.stderr)
        if not f.get('image'):
            print(f'WARNING {fid}: missing real image; acceptable only for demo', file=sys.stderr)
    tblids = set()
    for t in d.get('tables', []):
        tid = t.get('id')
        if not tid or tid in tblids:
            errors.append(f'Duplicate or missing table ID: {tid}')
        tblids.add(tid)
        en = t.get('headers_en', [])
        zh = t.get('headers_zh', [])
        if len(en) != len(zh):
            errors.append(f'{tid}: unequal English/Chinese header lengths')
        if any(not str(x).strip() for x in zh):
            errors.append(f'{tid}: untranslated Chinese table header')
        for row in t.get('rows', []):
            if len(row) != len(en):
                errors.append(f'{tid}: row length {len(row)} differs from header length {len(en)}')
        if t.get('rows_zh') is not None:
            if len(t['rows_zh']) != len(t.get('rows', [])):
                errors.append(f'{tid}: unequal bilingual table row counts')
    for sec in sections:
        for b in sec.get('blocks', []):
            for ref in b.get('refs', []):
                normalized = re.sub(r'(?<=\d)[a-z]$', '', str(ref), flags=re.I)
                if normalized not in figids and normalized not in tblids:
                    print(f'WARNING {b.get("id")}: cross-ref {ref} has no figure/table payload', file=sys.stderr)
    print(f'Coverage: {blocks} translated paragraph blocks; figures={len(figids)}; tables={len(tblids)}; references={len(d.get("references", []))}', file=sys.stderr)
    return errors


def inline_images(d: dict, base: pathlib.Path, strict: bool):
    for f in d.get('figures', []):
        path = f.get('image')
        if not path:
            if strict:
                raise ValueError(f'Missing real image for {f.get("id")}')
            f['data_uri'] = None
            continue
        resolved = pathlib.Path(path)
        if not resolved.is_absolute():
            resolved = (base / resolved).resolve()
        if not resolved.is_file():
            msg = f'Missing image {f.get("id")}: {resolved}'
            if strict:
                raise FileNotFoundError(msg)
            print('WARNING '+msg, file=sys.stderr)
            f['data_uri'] = None
            continue
        typ = mimetypes.guess_type(resolved.name)[0] or 'application/octet-stream'
        if typ not in ('image/png','image/jpeg','image/webp','image/gif','image/svg+xml'):
            raise ValueError(f'Unsupported image format ({typ}) for {resolved}')
        f['data_uri'] = f'data:{typ};base64,'+base64.b64encode(resolved.read_bytes()).decode('ascii')
    return d


def build(source: pathlib.Path, output: pathlib.Path, strict: bool):
    data = json.loads(source.read_text('utf-8'))
    problems = audit_data(data)
    if problems:
        raise ValueError('\n'.join(problems))
    inline_images(data, source.parent, strict)
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    template = TEMPLATE.read_text('utf-8')
    assert template.count('__INLINE_READER_DATA__') == 1
    result = template.replace('__INLINE_READER_DATA__', payload).replace('__READER_TITLE__', html.escape(data['meta']['title_zh']))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result, 'utf-8')
    print(f'CREATED {output} ({output.stat().st_size:,} bytes)', file=sys.stderr)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('data', type=pathlib.Path, help='Fully translated reader JSON')
    ap.add_argument('-o', '--output', type=pathlib.Path, required=True)
    ap.add_argument('--allow-missing-images', action='store_true', help='Allow prototype image placeholders only')
    a = ap.parse_args()
    build(a.data, a.output, not a.allow_missing_images)