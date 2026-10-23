---
name: paper-project-setup
description: Sets up a project folder for one paper or topic and collects its media assets (paper PDF, figures, demo videos, chart data, screenshots) with source attribution, downloading automatically wherever possible and asking the user to download only what truly cannot be fetched. Use before preparing a paper talk, or when asked to "set up a folder for this paper", "collect the figures and videos from the project page", "download the assets", or 建立論文資料夾／收集素材.
---

# Paper Project Setup

Create one tidy, self-describing folder per paper or topic and fill it with the original media the talk will need. This skill prepares material; designing the slides is the job of `paper-discussion-slides`.

Principle: **collect originals, record where everything came from, and make the user do as little as possible.** Try every automatic route before asking the user to download anything, and when asking, make the request precise enough to finish in one pass.

---

## 1. Identify the sources

From the user's link or title, find every place the paper's material lives, and record each URL:

- the paper itself (arXiv / publisher PDF, or the technical report)
- the project page or blog (figures, demo videos, interactive charts)
- code and data (GitHub, Hugging Face) for released logs, figures or result tables
- supplementary material and video hosts (YouTube, Vimeo, CDN links)

Note what kind of source each is (peer-reviewed paper, preprint, technical report, blog) and its date; the talk will need to say this.

## 2. Create the project folder

Ask where projects live if it is not known (e.g., a `Paper/` folder on the user's computer); otherwise use the location the user names. Create one folder per topic with a short kebab-case name, and run `scripts/asset_tools.py init <dir> --title "<paper title>" --url <each source page>` (the title is required; add `meta <dir> --source-type <type> --date <date>` too) to lay out:

```
<topic>/
  README.md          # what the paper is, links, source type, date, folder guide
  manifest.json      # one entry per asset (see section 5)
  source/            # paper PDF, saved page text / HTML, BibTeX
  figures/           # original images at full size (never only thumbnails)
  videos/            # original videos (+ compressed copies if needed)
  posters/           # still frames extracted from videos
  data/              # chart data (CSV / JSON) and tables
  screenshots/       # page or chart screenshots when no original exists
```

Keep originals untouched; write derived files (crops, compressed videos, redrawn charts) next to them with a suffix such as `_small.mp4` or `_redrawn.png`.

## 3. Collect assets automatically: try routes in this order

Before downloading, list what you plan to collect (count, types, rough size) in one message; the user's request to collect assets is the go-ahead for that list. Ask again before anything outside it.

1. **Direct download** in the workspace (`curl`, `wget`, Python `requests`) for PDFs, images, videos and data files with public URLs. Stop after the first refusal from a host: proxy and allowlist blocks are not fixed by retrying with another command.
2. **Released files**: GitHub repositories, Hugging Face datasets / Spaces, and arXiv source tarballs often contain the original figures and result data in higher quality than the web page.
3. **A browser** (the built-in browser or Claude in Chrome, whichever is available) when the host is blocked for the shell or the page renders media with JavaScript:
   - read the page and list every image, video and data URL with a script (see `references/browser-extraction.md`);
   - let the browser download them (they land in the user's Downloads folder), then move them into the project folder;
   - for interactive charts, read the underlying data from the page's scripts (often `data.js` or embedded JSON) and save it to `data/` instead of screenshotting the chart;
   - screenshot only what has no downloadable original (e.g., an interactive figure), at full resolution, into `screenshots/`.
4. **Ask the user** only for what all routes above failed to fetch (section 4).

Never bypass a paywall, a login the user has not set up, or a site's refusal. Download only publicly available material, for the user's own talk, and keep attribution.

## 4. When the user has to help

Ask once, with a complete checklist the user can finish in one pass:

- file name to save as, exact URL, and what it is (e.g., "Fig. 3, loss curves")
- where to put it (the exact project subfolder) or "anywhere, I'll move it"
- how to get it if not obvious (e.g., "right-click the video → Save video as")

Continue with everything else while waiting. When the files arrive, move them into place, rename them to the manifest names, and update the manifest.

## 5. Record every asset in the manifest

Add each asset with `scripts/asset_tools.py add` (or edit `manifest.json`). Each entry has:

| Field | Meaning |
|---|---|
| `file` | path inside the project folder |
| `type` | `pdf` (a PDF), `text` (saved page text or notes: .md / .txt / .bib), `page` (saved HTML / JS of a web page), `figure`, `video`, `poster`, `data`, `screenshot`; `add` refuses a type that does not match the file extension |
| `label` | what it is, e.g., "Fig. 1 benchmark results", "demo: pour bolts" |
| `source_url` | where it came from (page URL and, if different, the direct file URL) |
| `obtained` | `direct`, `release`, `browser`, `screenshot`, `user` |
| `notes` | caption, figure number, licence or attribution notes, anything odd |

Also record the assets you could not get and why with `asset_tools.py missing <dir> "what" --source URL --reason "why"`, so the gap is visible. `check` warns when the manifest has no title or sources, or an asset's type does not match its file.

## 6. Prepare assets for slides

- **Videos:** keep the original. If a file is too large for where it is going (e.g., an upload limit), make a compressed copy with `scripts/asset_tools.py shrink` (H.264, ~1280 px wide, CRF 28). Extract poster frames at a few points with `posters` so slides can show a still and highlight frames can be measured on it.
- **Figures:** keep full-size originals; highlight frames must be measured on the original, not on a thumbnail.
- **Charts:** prefer the underlying numbers in `data/` so charts can be redrawn cleanly and frames placed from exact coordinates.
- **Text:** save the page text or PDF so numbers can be checked against the source later.

## 7. Finish

1. Check every manifest file exists and opens (images load, videos play, data parses); `scripts/asset_tools.py check` does this.
2. Update the project `README.md`: paper title, authors, source type and date, links, and a short list of what was collected and what is missing.
3. Tell the user in a few lines: where the folder is, what was collected, anything that still needs their help.

## Final checklist

- [ ] One folder per topic with the standard layout; originals untouched
- [ ] Every source URL recorded; source type and date noted
- [ ] Every automatic route tried before asking the user; at most one consolidated request to the user
- [ ] Chart data saved as data where available, not only as screenshots
- [ ] Every asset in `manifest.json` with its source and how it was obtained; missing assets listed
- [ ] Large videos have compressed copies; poster frames extracted
- [ ] `check` passes
