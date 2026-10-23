"""Render a PPTX for checking: full pages, a thumbnail sheet, and a zoomed footer strip sheet.

    python render_check.py deck.pptx [out_dir] [--dpi 110]

Writes out_dir/page-NN.png, out_dir/sheet.png (layout only) and out_dir/footers.png, which
stacks the bottom 7% of every page at full resolution so you can confirm that footer text
is vertically centred inside its band on every slide. Requires LibreOffice (soffice) and
pdftoppm (poppler) and Pillow.
"""
import glob
import os
import subprocess
import sys

from PIL import Image


def render(pptx, out, dpi=110):
    os.makedirs(out, exist_ok=True)
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', out, pptx],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
    pdf = os.path.join(out, os.path.splitext(os.path.basename(pptx))[0] + '.pdf')
    for f in glob.glob(os.path.join(out, 'page-*.png')):
        os.remove(f)
    subprocess.run(['pdftoppm', '-r', str(dpi), '-png', pdf, os.path.join(out, 'page')], check=True)
    pages = sorted(glob.glob(os.path.join(out, 'page-*.png')))
    ims = [Image.open(p).convert('RGB') for p in pages]
    if not ims:
        return pages
    w, h = ims[0].size
    cols = 4
    tw, th = w // 4, h // 4
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw, rows * th), 'white')
    for i, im in enumerate(ims):
        sheet.paste(im.resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
    sheet.save(os.path.join(out, 'sheet.png'))
    sh = int(h * 0.07)
    strip = Image.new('RGB', (w, sh * len(ims)), 'white')
    for i, im in enumerate(ims):
        strip.paste(im.crop((0, h - sh, w, h)), (0, i * sh))
    strip.save(os.path.join(out, 'footers.png'))
    return pages


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dpi = int(sys.argv[sys.argv.index('--dpi') + 1]) if '--dpi' in sys.argv else 110
    if '--dpi' in sys.argv:
        args.remove(str(dpi))
    deck = args[0]
    out = args[1] if len(args) > 1 else os.path.splitext(deck)[0] + '_render'
    print('\n'.join(render(deck, out, dpi)))
