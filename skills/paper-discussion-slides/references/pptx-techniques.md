# PPTX 製作技術（python-pptx）

- 以模板 PPTX 複製頁面（深拷貝 spTree 並重新對應 rels），最後刪掉原模板頁。
- 影片用 `add_movie` 嵌入並附 poster frame；檔案過大時用 ffmpeg 重新編碼（例如 crf 28、寬 1280）。同頁多段影片要一起看時，設成同時自動播放並循環。
- 半透明：對圖片 blip 加 `alphaModFix`，對顏色 `srgbClr` 加 `alpha`。
- 圓角：`ROUNDED_RECTANGLE` 的 adjustments 依尺寸設定半徑。
- 弧線箭頭：用二次貝茲曲線取約 30 個點，以 `build_freeform` 畫成不封閉的折線，填色設為無、線條設紅色粗線（約 10pt），並在 `a:ln` 加 `a:tailEnd type="triangle"` 和 `cap="rnd"`。控制點取兩端中點沿垂直方向偏移（偏移量約為兩點距離的 0.35–0.45 倍）。
- 方塊箭頭：`MSO_SHAPE.DOWN_ARROW`／`RIGHT_ARROW` 等，實心淺灰藍、無外框。
- 用 LibreOffice 轉 PDF、pdftoppm 轉圖逐頁檢查。

## 工具函式

`scripts/slide_kit.py` 收錄上面這些技術的實作，以 1920×1080 的像素座標操作，座標、字級、線寬都會依投影片實際寬度等比例換算（字級以 20 吋寬投影片的 pt 計，在 13.33 吋投影片上比例相同）。使用前 `pip install python-pptx pillow`，把 scripts 資料夾加到 `sys.path`：

| 函式 | 用途 |
|---|---|
| `text(slide, x, y, w, h, paras, size, ...)` | 文字框；`paras` 可以是字串、字串清單，或 `(文字, 樣式)` 片段清單 |
| `rect(slide, x, y, w, h, fill, line, radius)` | 圓角矩形 |
| `callout(slide, x, y, lines, size=36, anchor=None)` | 紅字說明框，大小自動貼合文字；`anchor='r'` 時 x 是右邊界；回傳 `(元素, 方框座標)` |
| `frame(slide, x, y, w, h)` | 紅框 |
| `sub(rect, tl, br, pad)` | 用比例座標（在原尺寸素材上量）換算成投影片座標 |
| `arc_arrow(slide, p0, p1, bend)` | 紅色弧線箭頭；`bend` 正負決定彎曲方向，接近 0 是直線 |
| `block_arrow(slide, x, y, w, h, direction)` | 淺灰藍實心方塊箭頭 |
| `dim(elements, amt)` | 把元素調成半透明 |
| `picture(slide, path, x, y, w, h)` | 等比例放入方框，回傳圖片實際涵蓋的範圍（給 `sub` 用） |
| `hbars(slide, x, y, rows, ...)` | 原生水平長條圖，回傳每根長條的位置（給箭頭用） |

範例：

```python
from pptx import Presentation
from slide_kit import *

prs = Presentation('template.pptx')
s = prs.slides.add_slide(prs.slide_layouts[6])
_, r = picture(s, 'chart.png', 72, 222, 1150, 770)
f = sub(r, (0.0, 0.37), (0.95, 0.43), pad=6)      # 在原圖上量出的比例
frame(s, *f)
_, b = callout(s, 1290, f[1] + f[3] / 2 - 85, ['唯一沒贏：', '80.0 vs 81.3'])
block_arrow(s, f[0] + f[2] + 8, f[1] + f[3] / 2 - 30, b[0] - (f[0] + f[2]) - 16, 60, 'right')
prs.save('out.pptx')
```
