# paper-sharing-skills

A set of [Claude](https://claude.ai) skills for sharing research papers, from understanding a paper to presenting it to others. Works in Claude Code, claude.ai and the Claude desktop app.

Every skill follows one principle: **everything serves audience understanding.**

## Skills

| Skill | What it does | Status |
|---|---|---|
| [`paper-project-setup`](skills/paper-project-setup/SKILL.md) | Sets up a project folder for one paper or topic and collects its media (PDF, figures, demo videos, chart data, screenshots) with source attribution: downloads automatically where possible (direct, released files, browser), asks the user only for what truly cannot be fetched, and keeps a manifest of every asset | v0.2.0 |
| [`paper-discussion-slides`](skills/paper-discussion-slides/SKILL.md) | Designs paper-discussion / journal-club decks (PPTX or Canva): defines the problem first, splits a concept into progressive build slides only when it needs step-by-step reasoning, aligns highlight frames precisely, connects every callout to what it explains with an arrow, spells out every term on first use, and budgets time by key points and script length rather than page count | v0.1.0 |

More paper-sharing skills will be added over time.

## Install

### Claude Code

```bash
/plugin marketplace add whats2000/paper-sharing-skills
/plugin install paper-sharing-skills@paper-sharing-skills
```

### Claude desktop app / claude.ai

Download `paper-sharing-skills.plugin` from [Releases](../../releases) and install it in Claude, or upload any folder under `skills/` as an individual skill.

## Usage

Just describe what you need, for example:

- "Make a 30-minute discussion deck for this paper; the audience is students interested in robotics."
- "Build journal club slides for this paper using my template (attached)."
- "Set up a folder for this paper and collect the figures and demo videos from its project page."

If the paper has no project folder yet, Claude first runs `paper-project-setup` to create one and collect the figures, videos and chart data, then follows the slide workflow: define the problem → plan key points and time → build each concept as one slide with a full script → decide which points need a progressive build → check frames, terms, callouts and timing.

Slides and speaker notes are written in whatever language you ask for.

## Repository layout

```
.claude-plugin/
  plugin.json             # plugin metadata
  marketplace.json        # lets Claude Code install this repo as a marketplace
skills/
  paper-project-setup/
    SKILL.md              # folder layout, collection routes, manifest
    references/           # browser extraction snippets
    scripts/asset_tools.py# init / add / shrink / posters / check
  paper-discussion-slides/
    SKILL.md              # core rules (Claude reads this first)
    references/           # detailed examples, template spec example, PPTX techniques
    scripts/slide_kit.py  # python-pptx helpers
```

## Adding a skill

1. Create a folder under `skills/` with a kebab-case name (e.g., `paper-reading-notes`).
2. Add a `SKILL.md` that starts with YAML frontmatter:
   ```markdown
   ---
   name: paper-reading-notes
   description: In the third person, say what the skill does and when to use it, including phrases a user might say.
   ---
   ```
3. Write the body as instructions for Claude. Put long examples and specifications in `references/` and code in `scripts/`.
4. Add the skill to the table above and bump the version in `.claude-plugin/plugin.json` and `marketplace.json`.

Keep the same principle for new skills: every rule should answer "does this make it easier for the audience or reader to understand?"

## 中文說明

論文分享的 Claude skill 集合。`paper-project-setup` 為每篇論文建立專案資料夾並收集圖片、影片、圖表數據（能自動下載就自動，真的抓不到才請使用者幫忙），並記錄每個素材的來源；`paper-discussion-slides` 用來製作以觀眾理解為核心的論文討論簡報：先定義問題、只在需要分步引導時才拆成多頁、紅框精準對齊、用箭頭把重點連到說明框、專有名詞第一次出現就寫全稱並解釋、用要點與講稿估時間。製作簡報前若主題還沒設定，會先執行 `paper-project-setup`。Skill 內容以英文撰寫，簡報可以指定任何語言（例如繁體中文）。

## License

[MIT](LICENSE)
