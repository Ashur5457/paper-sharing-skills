#!/usr/bin/env python3
"""asset_tools: set up and maintain a paper project folder.

  init    <dir> --title T [--url U ...]          create the folder layout, README.md and manifest.json
  add     <dir> <file> --type T --label L --source URL --obtained HOW [--notes N]
  shrink  <video> [--width 1280] [--crf 28]      write <name>_small.mp4 next to it (needs ffmpeg)
  posters <video> --at 0.1 0.5 0.9 [--out DIR]   extract still frames at fractions of the duration (needs ffmpeg)
  check   <dir>                                  verify every manifest file exists and opens

Only the standard library is required; ffmpeg/ffprobe are used for video commands and Pillow,
if installed, to verify images.
"""
import argparse
import datetime as dt
import json
import pathlib
import shutil
import subprocess
import sys

SUBDIRS = ['source', 'figures', 'videos', 'posters', 'data', 'screenshots']
TYPES = ['pdf', 'figure', 'video', 'poster', 'data', 'screenshot']
OBTAINED = ['direct', 'release', 'browser', 'screenshot', 'user']


def _manifest(root):
    p = root / 'manifest.json'
    return p, (json.loads(p.read_text(encoding='utf-8')) if p.exists() else {'title': '', 'sources': [], 'assets': [], 'missing': []})


def _save(p, m):
    p.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def init(a):
    root = pathlib.Path(a.dir)
    for d in SUBDIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    p, m = _manifest(root)
    m['title'] = a.title or m.get('title', '')
    m['sources'] = sorted(set(m.get('sources', []) + (a.url or [])))
    m.setdefault('created', dt.date.today().isoformat())
    _save(p, m)
    readme = root / 'README.md'
    if not readme.exists():
        links = '\n'.join(f'- {u}' for u in m['sources']) or '- (add links)'
        readme.write_text(f"""# {m['title'] or root.name}

**Source type and date:** (peer-reviewed paper / preprint / technical report / blog; date)

## Links
{links}

## Folder
- `source/` paper PDF, saved page text, BibTeX
- `figures/` original figures at full size
- `videos/` original videos (and `_small` compressed copies)
- `posters/` still frames from videos
- `data/` chart data and tables
- `screenshots/` screenshots of things with no downloadable original
- `manifest.json` every asset with its source and how it was obtained

## Collected / missing
(see manifest.json)
""", encoding='utf-8')
    print(f'initialised {root}')


def add(a):
    root = pathlib.Path(a.dir)
    p, m = _manifest(root)
    f = pathlib.Path(a.file)
    rel = f.relative_to(root).as_posix() if f.is_absolute() and root.resolve() in f.resolve().parents else f.as_posix()
    entry = {'file': rel, 'type': a.type, 'label': a.label, 'source_url': a.source, 'obtained': a.obtained, 'notes': a.notes or ''}
    m['assets'] = [e for e in m['assets'] if e['file'] != rel] + [entry]
    _save(p, m)
    print(f'added {rel}')


def _need(tool):
    if not shutil.which(tool):
        sys.exit(f'{tool} not found; install ffmpeg first')


def _duration(video):
    _need('ffprobe')
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(video)],
                         capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def shrink(a):
    _need('ffmpeg')
    v = pathlib.Path(a.video)
    out = v.with_name(v.stem + '_small.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(v), '-vf', f"scale='min({a.width},iw)':-2",
                    '-c:v', 'libx264', '-crf', str(a.crf), '-preset', 'slow', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', str(out)], check=True)
    print(f'{out}  {v.stat().st_size / 1e6:.1f} MB -> {out.stat().st_size / 1e6:.1f} MB')


def posters(a):
    _need('ffmpeg')
    v = pathlib.Path(a.video)
    out_dir = pathlib.Path(a.out) if a.out else v.parent.parent / 'posters'
    out_dir.mkdir(parents=True, exist_ok=True)
    d = _duration(v)
    for frac in a.at:
        out = out_dir / f'{v.stem}_{frac:.2f}.jpg'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{d * frac:.3f}', '-i', str(v), '-frames:v', '1', '-q:v', '2', str(out)], check=True)
        print(out)


def check(a):
    root = pathlib.Path(a.dir)
    _, m = _manifest(root)
    bad = 0
    try:
        from PIL import Image
    except ImportError:
        Image = None
    for e in m['assets']:
        f = root / e['file']
        problem = None
        if not f.exists():
            problem = 'missing'
        elif f.stat().st_size == 0:
            problem = 'empty'
        elif Image and f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.webp'):
            try:
                with Image.open(f) as im:
                    im.verify()
            except Exception as ex:
                problem = f'image does not open ({ex})'
        elif f.suffix.lower() in ('.mp4', '.webm', '.mov') and shutil.which('ffprobe'):
            try:
                _duration(f)
            except Exception:
                problem = 'video does not open'
        elif f.suffix.lower() == '.json':
            try:
                json.loads(f.read_text(encoding='utf-8'))
            except Exception:
                problem = 'invalid JSON'
        if problem:
            bad += 1
            print(f'FAIL {e["file"]}: {problem}')
    listed = {e['file'] for e in m['assets']}
    extra = [p.relative_to(root).as_posix() for d in SUBDIRS for p in (root / d).rglob('*') if p.is_file()]
    for x in sorted(set(extra) - listed):
        print(f'NOTE {x}: not in manifest')
    for miss in m.get('missing', []):
        print(f'MISSING {miss}')
    print(f'{len(m["assets"]) - bad} / {len(m["assets"])} assets OK')
    sys.exit(1 if bad else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('init'); p.add_argument('dir'); p.add_argument('--title', default=''); p.add_argument('--url', nargs='*'); p.set_defaults(fn=init)
    p = sp.add_parser('add'); p.add_argument('dir'); p.add_argument('file')
    p.add_argument('--type', required=True, choices=TYPES); p.add_argument('--label', required=True)
    p.add_argument('--source', required=True); p.add_argument('--obtained', required=True, choices=OBTAINED)
    p.add_argument('--notes'); p.set_defaults(fn=add)
    p = sp.add_parser('shrink'); p.add_argument('video'); p.add_argument('--width', type=int, default=1280); p.add_argument('--crf', type=int, default=28); p.set_defaults(fn=shrink)
    p = sp.add_parser('posters'); p.add_argument('video'); p.add_argument('--at', type=float, nargs='+', default=[0.1, 0.5, 0.9]); p.add_argument('--out'); p.set_defaults(fn=posters)
    p = sp.add_parser('check'); p.add_argument('dir'); p.set_defaults(fn=check)
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
