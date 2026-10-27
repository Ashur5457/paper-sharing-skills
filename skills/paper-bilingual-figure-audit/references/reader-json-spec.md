# Reader JSON specification

All text must be JSON, UTF-8. Prefer one manuscript paragraph per `blocks[]` item. The `en` text is the exact original, not a shortened paraphrase. A complete `zh` is mandatory for final output. For a source equation, use the verified source string or renderable text in both languages.

```json
{
  "meta": {"title_zh": "論文標題", "title_en": "Paper title", "authors": "Author list", "version": "2026-10-26", "source": "MS.docx + SI.docx"},
  "sections": [
    {"id": "abstract", "title_zh": "摘要", "title_en": "Abstract", "blocks": [
      {"id": "ms-p001", "type": "paragraph", "zh": "中文完整翻譯。", "en": "The complete source paragraph.", "refs": ["Fig. 1", "Table S1"], "figure_group": "Fig. 1", "subsection_en": "", "subsection_zh": ""
    ]}
  ],
  "figures": [
    {"id": "Fig. 1", "group": "main", "image": "work/ms/fig1.png", "caption_zh": "圖說中文", "caption_en": "Figure 1 caption", "verified": true},
    {"id": "Fig. S1", "group": "si", "image": "work/si/s1.png", "caption_zh": "圖說中文", "caption_en": "Figure S1 caption", "verified": true}
  ],
  "tables": [
    {"id": "Table S1", "title_zh": "電解液性質", "title_en": "Electrolyte properties", "headers_zh": ["組成", "離子導電度"], "headers_en": ["Composition", "Ionic conductivity"], "rows": [["A", "1.5 mS cm−1"]], "rows_zh": [["A", "1.5 mS cm−1"]]}
  ],
  "references": [{"en": "A. Author. Paper title, Journal (2026), DOI ...", "zh_title": "中文題名（選填）"}]
}
```

Notes:
- `refs` may be empty; figure links can also be auto-detected from English/Chinese source text, but explicit links are better.
- `figures[].image` may be omitted for prototype builds only. For a real audit reader, missing images are errors.
- `rows_zh` must have exactly the same dimensions as `rows` if provided.
- If the SI contains substantial prose beyond captions/tables, add it to `sections` with IDs prefixed `si-` and label it as Supporting Information.
- Image `verified=false` means the figure mapping has NOT been visually validated. The builder shows a warning; do not claim figure mapping verified.
- Inline sources may contain `<` and `>`; the renderer escapes them. Do not place arbitrary raw HTML in text.
- Provide translation and figure integrity reports externally if a true 100% audit is required.

## Structural paragraph locator rules (REQUIRED)

- Compact display convention: `P1`, `P2`, etc. mean local paragraph number; never show Chinese numeral labels such as `第二段`. Figure-caption blocks use `Fig. N caption` (singular), not `Figure captions — Fig. N 圖說`.

- Labels count **paragraphs within the most specific original heading**, and reset on changes of original subsections. Use translated English section names in displayed locators, e.g. `Introduction · P2`.
- `Results and discussion` has no subheadings in some manuscripts; set `group_by_main_figure: true` on that section and (preferably) `figure_group: "Fig. 3"` on every block to make grouping explicit. Display `Fig. 3 · P2` for its second paragraph. If unspecified, the renderer infers groups from forward-only main figure citations; verify the grouping and correct `figure_group` as necessary. `Fig. S10` citations **do not** start new groups.
- In `Experimental section`, give blocks the original `subsection_en` / `subsection_zh`, e.g. `Electrochemical Characterization`; label second block `Experimental section — Electrochemical Characterization · P2`. If subsections are separate `sections[]`, supply `parent_title_en: "Experimental section"`.
- Do not create new **scientific** subheadings within original content. Fig. labels are visually marked as reader navigation.
- Keep `id` stable to preserve stored notes. Use the same human-readable label for paragraph headers, figure-panel backlinks, search, and exported notes.