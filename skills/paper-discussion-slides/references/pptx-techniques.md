# PPTX techniques (python-pptx)

- Duplicate slides from the template PPTX (deep-copy the `spTree` and remap the relationships), then delete the original template slides at the end.
- Embed videos with `add_movie` and a poster frame. If the file is too large, re-encode with ffmpeg (e.g., crf 28, width 1280). When several videos on one slide should be watched together, set them to autoplay and loop together.
- Dimming: add `alphaModFix` to an image's `blip`, and `alpha` to `srgbClr` colours.
- Rounded corners: set the `ROUNDED_RECTANGLE` adjustment from the box size.
- Curved arrows: sample about 30 points of a quadratic Bézier curve and draw them as an open polyline with `build_freeform`; no fill, thick red line (about 10 pt), and add `a:tailEnd type="triangle"` and `cap="rnd"` to `a:ln`. Place the control point at the midpoint, offset perpendicular to the line by about 0.35–0.45 × the distance between the ends.
- Block arrows: `MSO_SHAPE.DOWN_ARROW` / `RIGHT_ARROW` etc., solid light grey-blue, no outline.
- Check every slide by converting to PDF with LibreOffice and rendering pages with pdftoppm.

## Helpers

`scripts/slide_kit.py` implements the techniques above. It works in a 1920×1080 pixel canvas; coordinates, font sizes and line widths are scaled to the real slide width (font sizes are points on a 20-inch-wide slide, so proportions stay the same on a 13.33-inch slide). Install `python-pptx` and `pillow`, then add the `scripts` folder to `sys.path`.

| Function | Purpose |
|---|---|
| `text(slide, x, y, w, h, paras, size, ...)` | Text box; `paras` is a string, a list of strings, or a list of `(text, style)` runs |
| `rect(slide, x, y, w, h, fill, line, radius)` | Rounded rectangle |
| `callout(slide, x, y, lines, size=36, anchor=None)` | Red callout whose box fits its text; with `anchor='r'`, `x` is the right edge; returns `(elements, box)` |
| `frame(slide, x, y, w, h)` | Red frame |
| `sub(box, tl, br, pad)` | Convert fractional coordinates measured on the original asset into slide coordinates |
| `arc_arrow(slide, p0, p1, bend)` | Red curved arrow; the sign of `bend` sets the direction, near 0 is straight |
| `block_arrow(slide, x, y, w, h, direction)` | Solid light grey-blue block arrow |
| `dim(elements, amt)` | Make elements semi-transparent |
| `picture(slide, path, x, y, w, h)` | Fit an image into a box keeping its aspect ratio; returns the box it actually covers (for `sub`) |
| `hbars(slide, x, y, rows, ...)` | Native horizontal bar chart; returns each bar's position (for arrows) |
| `notes(slide, script)` | Write the speaker script |
| `new_deck(template_path=None)` | Open a template PPTX, or create an empty 20 × 11.25 in deck |
| `blank_slide(prs)` | Add a slide on the emptiest layout with its placeholders removed |
| `chrome(slide, title, deck_title, credit, page, total)` | Template header bands, slide title and footer (values from `TEMPLATE`); build steps pass the same `page` |
| `band_text(slide, x, y, w, h, text, size, color, align)` | One line of text vertically centred inside a band (used by `chrome`) |

Other scripts:

| Script | Purpose |
|---|---|
| `build_sample_template.py [out.pptx]` | Rebuild `assets/sample-template.pptx`, the reference deck for the template |
| `render_check.py deck.pptx [out_dir]` | Render pages, a thumbnail sheet, and `footers.png` (every footer at full resolution) |

Example:

```python
import sys
sys.path.insert(0, 'path/to/skills/paper-discussion-slides/scripts')
from slide_kit import *

prs = new_deck()                       # or new_deck('their-template.pptx')
s = blank_slide(prs)
chrome(s, 'The only loss', 'Short Deck Title', 'Author / Institution, 2026', page=9, total=17)
_, r = picture(s, 'chart.png', 72, 222, 1150, 770)
f = sub(r, (0.0, 0.37), (0.95, 0.43), pad=6)      # fractions measured on the original image
frame(s, *f)
_, b = callout(s, 1290, f[1] + f[3] / 2 - 85, ['The only loss:', '80.0 vs 81.3'])
block_arrow(s, f[0] + f[2] + 8, f[1] + f[3] / 2 - 30, b[0] - (f[0] + f[2]) - 16, 60, 'right')
prs.save('out.pptx')
```
