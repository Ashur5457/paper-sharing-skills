"""slide_kit: python-pptx helpers for paper-discussion slides.

All coordinates are in a 1920 x 1080 pixel canvas and are scaled to the real slide width,
so the same numbers work for any 16:9 template. Font sizes are given in points on that canvas
(1 px = 0.75 pt, i.e. a 20-inch-wide slide) and are scaled the same way, so a 36 pt callout keeps
the same proportion on a 13.33-inch slide. Every drawing function returns the XML
elements it created (so they can be passed to `dim`), and callout / picture also return
the box they occupy (so arrows and frames can be placed from it).

Requires: python-pptx, Pillow
"""
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from PIL import Image

# colours (override to match your template)
INK = '1A1A1A'
MUTED = '5F5F6E'
BLUE = '005AA0'
RED = 'C83C3C'
GRAYBG = 'F0F0F0'
CALLRED = 'FF5757'
CALLLINE = '99BDD9'
ARROWGRAY = 'C8D0DA'
LATIN_FONT = 'Arial'
EA_FONT = 'Microsoft JhengHei'
RADIUS = 14

_CANVAS_W = 1920


def _scale(slide):
    return slide.part.package.presentation_part.presentation.slide_width / _CANVAS_W


def _px(slide, v):
    return Emu(int(v * _scale(slide)))


def _font_scale(slide):
    return _scale(slide) / 9525   # 9525 EMU per px on a 20-inch-wide slide


def _style_run(r, size, color, bold, italic=False, mono=False, k=1.0):
    f = r.font
    f.size = Pt(size * k)
    f.bold = bold
    f.italic = italic
    f.color.rgb = RGBColor.from_string(color)
    f.name = 'Courier New' if mono else LATIN_FONT
    rPr = r._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {})
        rPr.append(ea)
    ea.set('typeface', EA_FONT)


def text(slide, x, y, w, h, paras, size=24, color=INK, bold=False, align='l', anchor='t', mono=False, italic=False):
    """paras: str | [str, ...] | [[(text, {size, color, bold, italic}), ...], ...]"""
    tb = slide.shapes.add_textbox(_px(slide, x), _px(slide, y), _px(slide, w), _px(slide, h))
    tf = tb.text_frame
    tf.word_wrap = True
    for m in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'):
        setattr(tf, m, 0)
    tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[anchor]
    if isinstance(paras, str):
        paras = [paras]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[align]
        segs = [(para, {})] if isinstance(para, str) else para
        for t, o in segs:
            r = p.add_run()
            r.text = t
            _style_run(r, o.get('size', size), o.get('color', color), o.get('bold', bold), o.get('italic', italic), mono, _font_scale(slide))
    return [tb._element]


def rect(slide, x, y, w, h, fill=GRAYBG, line=None, line_w=1.5, radius=RADIUS, shape=None):
    if shape is None:
        shape = MSO_SHAPE.ROUNDED_RECTANGLE if (radius and min(w, h) >= 24) else MSO_SHAPE.RECTANGLE
    sp = slide.shapes.add_shape(shape, _px(slide, x), _px(slide, y), _px(slide, w), _px(slide, h))
    if shape in (MSO_SHAPE.ROUNDED_RECTANGLE, MSO_SHAPE.ROUND_2_SAME_RECTANGLE):
        sp.adjustments[0] = min(0.5, radius / min(w, h))
    sp.shadow.inherit = False
    if fill:
        sp.fill.solid()
        sp.fill.fore_color.rgb = RGBColor.from_string(fill)
    else:
        sp.fill.background()
    if line:
        sp.line.color.rgb = RGBColor.from_string(line)
        sp.line.width = Pt(line_w * _font_scale(slide))
    else:
        sp.line.fill.background()
    return [sp._element]


def text_width(t, size):
    """approximate rendered width in px of one line at `size` pt (CJK = 1 em, Latin ≈ 0.56 em)."""
    em = size / 0.75
    return sum(em * (0.56 if ord(c) < 0x2E80 else 1.0) for c in t)


def callout(slide, x, y, lines, size=36, w=None, align='c', anchor=None):
    """red bold callout whose box fits its text. anchor='r' makes x the right edge.
    returns (elements, (x, y, w, h))."""
    lh = size / 0.75 * 1.3
    padx, pady = 40, 26
    if w is None:
        w = max(text_width(l, size) for l in lines) + 2 * padx
    h = lh * len(lines) + 2 * pady
    if anchor == 'r':
        x -= w
    els = rect(slide, x, y, w, h, fill=GRAYBG, line=CALLLINE, line_w=1.5, radius=16)
    els += text(slide, x + padx * 0.5, y, w - padx, h, lines, size=size, color=CALLRED, bold=True, align=align, anchor='m')
    return els, (x, y, w, h)


def frame(slide, x, y, w, h, color=CALLRED, width=6):
    """red frame around part of an image."""
    return rect(slide, x, y, w, h, fill=None, line=color, line_w=width, radius=16)


def sub(box, tl, br, pad=6):
    """box = (x, y, w, h) covered by an image; tl / br = fractions measured on the ORIGINAL asset."""
    x, y, w, h = box
    return (x + tl[0] * w - pad, y + tl[1] * h - pad, (br[0] - tl[0]) * w + 2 * pad, (br[1] - tl[1]) * h + 2 * pad)


def picture(slide, path, x, y, w, h, alt=''):
    """place an image inside (x, y, w, h) keeping its aspect ratio ('contain').
    returns (elements, box actually covered by the image)."""
    with Image.open(path) as im:
        r = im.width / im.height
    if w / h > r:
        nw = h * r
        X, Y, W, H = x + (w - nw) / 2, y, nw, h
    else:
        nh = w / r
        X, Y, W, H = x, y + (h - nh) / 2, w, nh
    pic = slide.shapes.add_picture(path, _px(slide, X), _px(slide, Y), _px(slide, W), _px(slide, H))
    pic._element.find('.//' + qn('p:cNvPr')).set('descr', alt)
    return [pic._element], (X, Y, W, H)


def arc_arrow(slide, p0, p1, bend=0.35, color=CALLRED, width=10, n=32):
    """curved red arrow from p0 to p1 (px). bend > 0 bows to the left of the travel direction; ~0 is straight."""
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    cx, cy = mx - dy * bend, my + dx * bend
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1,
                    (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1))
    fb = slide.shapes.build_freeform(_px(slide, pts[0][0]), _px(slide, pts[0][1]), scale=1.0)
    fb.add_line_segments([(_px(slide, a), _px(slide, b)) for a, b in pts[1:]], close=False)
    sp = fb.convert_to_shape()
    sp.fill.background()
    sp.shadow.inherit = False
    sp.line.color.rgb = RGBColor.from_string(color)
    sp.line.width = Pt(width * _font_scale(slide))
    ln = sp._element.find('.//' + qn('a:ln'))
    ln.set('cap', 'rnd')
    ln.append(ln.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'}))
    return [sp._element]


def block_arrow(slide, x, y, w, h, direction='down', fill=ARROWGRAY):
    """solid block arrow for a direct 'this → so' link."""
    shp = {'down': MSO_SHAPE.DOWN_ARROW, 'right': MSO_SHAPE.RIGHT_ARROW,
           'left': MSO_SHAPE.LEFT_ARROW, 'up': MSO_SHAPE.UP_ARROW}[direction]
    sp = slide.shapes.add_shape(shp, _px(slide, x), _px(slide, y), _px(slide, w), _px(slide, h))
    sp.fill.solid()
    sp.fill.fore_color.rgb = RGBColor.from_string(fill)
    sp.line.fill.background()
    sp.shadow.inherit = False
    return [sp._element]


def dim(elements, amt=30000):
    """make elements semi-transparent (pictures, fills, lines, text). amt: 0–100000 opacity."""
    for el in elements:
        if el is None:
            continue
        for b in el.iter(qn('a:blip')):
            if b.find(qn('a:alphaModFix')) is None:
                b.insert(0, b.makeelement(qn('a:alphaModFix'), {'amt': str(amt)}))
        for c in el.iter(qn('a:srgbClr')):
            if c.find(qn('a:alpha')) is None:
                c.append(c.makeelement(qn('a:alpha'), {'val': str(amt)}))
    return elements


def hbars(slide, x, y, rows, label_w=560, bar_w=760, vmax=100, bar_h=60, gap=34, size=26, track=False):
    """native horizontal bar chart. rows: [(label, value, colour, value_text), ...].
    returns {label: (bar_x, bar_y, bar_w, bar_h, value_text_right_edge)}."""
    out = {}
    for i, (lab, v, col, vt) in enumerate(rows):
        yy = y + i * (bar_h + gap)
        text(slide, x, yy, label_w - 24, bar_h, lab, size=size, align='r', anchor='m')
        bx = x + label_w
        if track:
            rect(slide, bx, yy, bar_w, bar_h, fill='E6E6EC', radius=0)
        bw = max(4, bar_w * v / vmax)
        rect(slide, bx, yy, bw, bar_h, fill=col, radius=0)
        vx = bx + (bar_w if track else bw) + 18
        text(slide, vx, yy, 260, bar_h, vt, size=size + 2, bold=True, anchor='m')
        out[lab] = (bx, yy, bw, bar_h, vx + text_width(vt, size + 2))
    return out


def notes(slide, script):
    """speaker notes (write the full spoken script here)."""
    slide.notes_slide.notes_text_frame.text = script
