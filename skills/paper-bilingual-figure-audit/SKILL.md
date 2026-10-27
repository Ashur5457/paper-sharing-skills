---
name: paper-bilingual-figure-audit
description: Creates complete English–Traditional Chinese bilingual research-paper HTML readers for manuscripts and Supporting Information, with original main/SI figures, tables, concise figure-based paragraph locators, source-preserving translation, and coverage audits. Use when asked for full bilingual manuscript translation, figure/SI cross-checking, or an offline paper reader; not for summary-only requests.
---

# Bilingual Scientific Paper × Main Figures × SI Audit Reader

## Objective

Turn an English manuscript and optional Supporting Information (DOCX preferred; PDF also acceptable) into **one self-contained offline HTML**. The core reading behavior is **a complete Traditional Chinese translation ABOVE the exact English original of each paragraph**, with side-by-side access to the corresponding original main figures / SI figures / tables. This skill creates a repeatable workflow, not a fixed Na–S paper: NEVER embed content from another user's paper or substitute previously produced translations.

## Source and preparation

1. Identify exact manuscript/SI filenames, versions, dates and sources. If the user supplies Drive links, use a connected Drive reader to retrieve the exact files and obtain actual DOCX bytes; do not search public web for private manuscripts. Prefer matching MS/SI revision versions. If available, use the appropriate PDF/DOCX skill to inspect source format.
2. From DOCX, run `python scripts/extract_docx.py manuscript.docx --out extracted_ms.json --assets work/assets/ms --role ms` and similarly for SI (`--role si`). `python-docx` is required for extraction. It yields original English text blocks, recovered figures/tables, and a **translation skeleton**. The extractor does NOT translate.
3. Confirm all inline and floating figures. Match them to captions by **document order, figure IDs and visual inspection**. The helper's automated caption-to-image mapping is tentative: verify every pairing. For PDFs, extract genuine figure images or faithfully crop pages with the PDF tool; preserve source figure text as given. DO NOT generate synthetic scientific data/figures.
4. Check editorial comments separately; reviewer annotations and tracked revisions are NOT automatically part of manuscript body. Include only if user requests them, in a clearly separate layer. Do not conflate comments with source claims.

## Full translation requirements — nonnegotiable

- Translate **every manuscript paragraph**, heading, title, abstract, keywords, introduction, results/discussion, conclusion, methods, acknowledgments, declarations, figure captions, TOC and optional SI prose/captions/tables as requested. Include **all original English paragraphs below Chinese**, not behind collapsed accordions by default.
- Preserve text order, subsection hierarchy, references `[1–5]`, Fig./Table identifiers (including panel labels a–f), numerical values, units, uncertainties, chemical formulas, potential reference electrodes, mathematical equations, names and citations. Never skip paragraphs, compress a paragraph into a summary, correct or harmonize scientific claims silently, or invent missing experimental details.
- Use natural Taiwan Traditional Chinese and accurate electrochemistry terminology: SEI/CEI, ionic conductivity, solvation shell, RDF, CN, EIS, CV, LSV, GITT, XPS, Na||Na, Na||Cu, Na||SPAN, etc. Keep technical English when it helps trace original meaning.
- If source math is OOXML `m:oMath`, extract it from Office Math or a verified visual; do not label it absent merely because `python-docx.paragraph.text` missed it. Check merged cells, superscripts/subscripts, embedded captions, tables, and TOC.
- Be precise about fact vs assumption. If a passage is ambiguous, translate faithfully and, where necessary, append a visibly distinct **translator/editorial note**—not an unannounced rewrite. Do not translate reference metadata into a replacement citation; retain the exact reference entry as the canonical source, optionally supply a secondary translated title.
- Preserve any actual contradictions (e.g., different capacities, SET values, temperatures); flag them separately for cross-checking. Do not normalize values to fit a preferred claim.

## Structured intermediate data

Use `references/reader-json-spec.md`. The reusable source JSON supports:
- `meta` — title, version, author list, source details.
- `sections[]` — `id`, `title_zh`, `title_en`, `blocks[]` with `id`, `type` (`paragraph`, `heading`, `equation`), `zh`, `en`, `refs[]`; `refs` contain `Fig. 2`, `Fig. S4`, `Table S1` identifiers; preserve English verbatim. Additional `group_by_main_figure` for Results/Discussion, `blocks[].figure_group` for verified Fig. 1–N grouping, `blocks[].subsection_en` / `subsection_zh` for original subheadings, and `sections[].parent_title_en` for separately listed method subsections.
- `figures[]` — `id`, `group` (`main` or `si`), original `image` filename, `caption_zh`, `caption_en`, `source`, `verified`.
- `tables[]` — `id`, `title_zh`, `title_en`, `headers_zh`, `headers_en`, `rows` holding original text; optional `rows_zh` parallel translation.
- `references[]` — full original `en` and optional `zh_title`.

Avoid losing paragraphs during JSON conversion. Keep paragraph numbering traceable to original document. When a large paper exceeds the generation budget, translate in explicit continued chunks and assemble only after every original paragraph has a Chinese counterpart. Do not claim full completion after partially translating.

## Build the offline reader

Run `python scripts/build_reader.py filled_translation.json -o manuscript_bilingual_figures.html`. It embeds local images in base64, CSS, JS and JSON into a *single HTML file*; no CDN dependencies. Include:

- Three-column desktop: left section & figure index, center full bilingual paper, right sticky figure/SI/table viewer.
- **MANDATORY paragraph citations**: Never show `原稿第 23 段`, `MS 原稿第 N 段`, `§23`, or raw source paragraph ids as user-facing locators. Use local counts within each original heading: `Introduction · P2`; within an experimental subsection: `Experimental section — Electrochemical Characterization · P2`. The long original `Results and discussion` (no native subheadings) MUST be grouped into **Fig. 1, Fig. 2, …** by the main figure primarily discussed, with paragraph numbering reset per figure (`Fig. 3 · P2`). Use the same locator in paragraph labels, figure-panel **正文直接引用／此主圖對應段落** backlinks, search, and exported audit notes. Keep stable machine ids/note keys internally for persistence.
- Results/Discussion figure headings are **navigation labels, not part of the source manuscript**. Place `Fig. N｜中文圖組名稱` before each group. Text referencing only SI Fig./Table stays in its current main-Fig group; backward references must not restart earlier figure groups. Verify main-figure boundaries from context and not just first occurrence of `Fig. Sxx` or every inline figure citation. Use compact labels: `P1`, `P2`, etc. mean **paragraph 1, paragraph 2** and reset within the original section/subsection or each Results main-figure group. Do not write `第 N 段`. For each figure-caption paragraph, use singular `Fig. N caption` (e.g. `Fig. 1 caption`) without the redundant `Figure captions —` prefix; the source figure-captions heading can remain as a normal section title.
- Mobile layout: usable navigation and images without horizontal overflow.
- Every center paragraph: clear **繁體中文翻譯**, then **ENGLISH ORIGINAL** immediately underneath, both visible. Provide global hide/show English for user choice, with show as default.
- Search both languages; clickable Fig./Table cross references; main/SI/table tabs; prior/next navigation; image enlargement; optional pin-and-compare two figures; journal references; figure/table bilingual captions; editable per-paragraph notes + Markdown export.
- Offline: no network requests or external font/image/script imports. Images must genuinely match their source captions. Do not downsample away text needed for checking.
- State whether SI body is translated or only original images/captions/tables are embedded; avoid an ungrounded 'SI 全文翻譯' claim.

## Canonical user-facing locator format (mandatory)

Use the following **short, consistent labels** everywhere a paragraph or caption is identified:

| Content | Label | Meaning |
| --- | --- | --- |
| Introduction, second paragraph | `Introduction · P2` | Second paragraph inside Introduction |
| Results and discussion, second paragraph related to Figure 3 | `Fig. 3 · P2` | Second paragraph in Figure 3's thematic group |
| Electrochemical Characterization, second paragraph | `Experimental section — Electrochemical Characterization · P2` | Second paragraph of this original methods subsection |
| Main Figure 1 caption | `Fig. 1 caption` | Figure 1's original caption, **not** a Results paragraph |
| Supporting Figure 2 caption | `Fig. S2 caption` | Supporting figure caption |
| Supporting Table 1 caption | `Table S1 caption` | Supporting table caption |

**Do not concatenate a figure-group paragraph identifier and a caption identifier.** For example, `Fig. 1 · P1Figure captions — Fig. 1 圖說` is invalid. Captions are independent blocks. Do not use `Fig1 captions` (missing period and plural caption), `Figure captions — Fig. 1 圖說`, or global `原稿第 N 段` anywhere in visible UI, figure backlinks, search hits, copied text, or exported notes. The heading `Figure captions` may remain in the document's outline, but is **not** prefixed to individual caption locators. Use identical conventions for user manuscripts of any field, not just Na–S papers.

## Required quality checks

1. **Coverage**: count nonempty source paragraph blocks and nonempty Chinese paired blocks. All manuscript blocks translated (100%); no blank or duplicated translations. Check each paragraph’s English against original; `extract_docx.py` may split paragraphs differently in equations or tables.
2. **Figure integrity**: all `Fig. 1–N` and `Fig. S1–N` IDs exist, original image is embedded, the figure numbering and captions match visual labels. Check SI figures may be missing, duplicated, or merged as multiple images.
3. **Table integrity**: every Table Sxx exists and every cell retains the original numerical value/units; for translated tables, retain source cells next to translations or selectable original.
4. **Consistency**: scan numeric strings, units, cross-references, special characters, sub/superscripts, equations. Preserve conflicting source values and create separate warning notes if useful.
5. **Interactive QA**: open HTML in headless Chromium or a real browser if available, inspect desktop/mobile screenshots, exercise search, English toggle, figure selection, reference click, image zoom, notes and offline functionality. Correct runtime JS errors.
6. **Delivery**: link the exact generated HTML path. Summarize grounded counts and disclose any unmapped or missing figures/paragraphs explicitly. Avoid declaring 100% complete without auditing.

## Script commands

```bash
python -m pip install python-docx
python scripts/extract_docx.py MS.docx --role ms --out extracted_ms.json --assets work/ms
python scripts/extract_docx.py SI.docx --role si --out extracted_si.json --assets work/si
# Translate and merge extracted source content into one filled_translation.json; verify pairs and mappings.
python scripts/build_reader.py filled_translation.json -o paper_bilingual_reader.html
```

The JSON example is `examples/demo_reader.json`; it is generic sample data, not a scientific claim. Images are optional in the demo. The final manuscript HTML must use images from the user's source files.

## Explicit invocation

After the skill is installed, the user may invoke `@paper-bilingual-figure-audit` in ChatGPT (select from the `@` menu), or ask naturally: **「使用論文中英主圖 SI 對照 Skill，把這份 MS 和 SI 全文翻成繁中 HTML；中文在上、英文原文緊接在下」**. Do not imply that preparing a ZIP file automatically installs the skill into the user's account.