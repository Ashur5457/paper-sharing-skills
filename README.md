# paper-sharing-skills

論文分享的 skill 集合，給 Claude（Claude Code、claude.ai、Claude 桌面版）使用：從讀懂一篇論文，到把它講給別人聽。

所有 skill 都依同一個原則設計：**一切以「觀眾更好理解」為方向。**

## Skills

| Skill | 用途 | 狀態 |
|---|---|---|
| [`paper-discussion-slides`](skills/paper-discussion-slides/SKILL.md) | 製作論文討論／讀書會簡報（PPTX 或 Canva）：先定義問題、只在需要分步引導時才拆成多頁、紅框精準對齊、用箭頭把重點連到說明框、專有名詞第一次出現就寫全稱並解釋、用要點與講稿估時間 | v0.1.0 |

之後會陸續加入其他論文分享相關的 skill。

## 安裝

### Claude Code

```bash
/plugin marketplace add whats2000/paper-sharing-skills
/plugin install paper-sharing-skills@paper-sharing-skills
```

### Claude 桌面版／claude.ai

到 [Releases](../../releases) 下載 `paper-sharing-skills.plugin`，在 Claude 裡上傳安裝；或把 `skills/` 底下的資料夾個別上傳成 skill。

## 使用方式

安裝後直接說出需求，例如：

- 「幫我把這篇論文做成 30 分鐘的分享簡報，觀眾是對機器人有興趣的學生」
- 「用我的模板（附檔）做這篇 paper 的 journal club slides」

Claude 會依 skill 的流程：讀原文抓素材 → 定義問題 → 規劃要點與時間 → 每個概念先做單頁、寫講稿 → 判斷哪些要點需要分步講 → 檢查紅框、名詞、說明框與時間。

## 目錄結構

```
.claude-plugin/
  plugin.json           # plugin 資訊
  marketplace.json      # 讓 Claude Code 可以用 marketplace 安裝
skills/
  paper-discussion-slides/
    SKILL.md            # 核心規則（Claude 會先讀這份）
    references/         # 詳細範例、模板規格範例、PPTX 技術
    scripts/slide_kit.py# python-pptx 工具函式
```

## 新增 skill

1. 在 `skills/` 底下建立新資料夾，名稱用 kebab-case（例如 `paper-reading-notes`）。
2. 放一份 `SKILL.md`，開頭是 YAML frontmatter：
   ```markdown
   ---
   name: paper-reading-notes
   description: 用第三人稱寫清楚這個 skill 做什麼、什麼情況該用（附上使用者可能說的話）。
   ---
   ```
3. 內文寫給 Claude 看的指示；較長的範例與規格放進 `references/`，程式放進 `scripts/`。
4. 更新本頁的 Skills 表格，並在 `.claude-plugin/plugin.json` 與 `marketplace.json` 調升版本號。

設計新 skill 時，沿用同一個總原則：每條規則都要能回答「這樣做，觀眾或讀者會不會更容易理解？」

## English summary

A collection of Claude skills for sharing research papers. The first skill, `paper-discussion-slides`, designs paper-discussion / journal-club decks that put audience understanding first: define the problem before the results, split a concept across progressive build slides only when it needs step-by-step reasoning, align highlight frames precisely, connect every callout to what it explains with an arrow, spell out every term on first use, and budget time by key points and script length rather than page count. Skill content is written in Traditional Chinese.

## License

[MIT](LICENSE)
