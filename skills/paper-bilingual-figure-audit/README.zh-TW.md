<div align="center">

# 📖 paper-bilingual-figure-audit

**論文中英逐段對照 × 主圖與 Supporting Information 查核：中文在上、英文原文在下，整合為單一可離線使用的 HTML。**

[English](README.md) · **繁體中文**

</div>

---

## ✨ 功能

這個 Skill 適合檢查英文科研論文（尤其電池、電化學領域）及其 Supporting Information。它以可溯源的原文與完整繁中翻譯，建立可以隨時對照主圖、SI 圖片、表格的互動式閱讀器。

| 功能 | 說明 |
| --- | --- |
| 全文中英對照 | 每段繁中翻譯在上，**英文原文緊接在下**，預設顯示。 |
| 主圖分段導航 | Results and discussion 以 Fig. 1、Fig. 2… 分組，並在組內重新計數。 |
| 精簡定位 | `Introduction · P2`、`Fig. 3 · P2`、`Fig. 1 caption` 等。 |
| 主圖／SI | 擷取原始圖片、雙語圖說與 SI 表格，建立正文交叉引用。 |
| 查核工具 | 全文搜尋、放大、雙圖比較、段落筆記與 Markdown 匯出。 |
| 可離線閱讀 | 所有必要內容內嵌於單一 HTML，不依賴外部網站。 |
| 完整性檢查 | 核對原文與譯文段數、單位、數據、方程式、圖號及表格。 |

> **重要：** Python 腳本負責抽取 Word 原文、原始圖片和表格，並組合 HTML；**不會自動翻譯**。需由模型或譯者逐段翻譯並核對。Word 的圖片與圖說自動配對也必須再人工確認。

## 🚀 使用方式

### 在 ChatGPT 專案中使用

將 [`SKILL.md`](SKILL.md) 放到 Project Files（專案檔案），並在專案指令要求模型於製作論文 HTML 前先閱讀這份 Skill。若工作區支援正式 Skills 安裝，也可使用該安裝入口。提供 MS / SI 檔案後輸入：

> 使用 `paper-bilingual-figure-audit`，完整翻譯這篇論文及 SI，中文在上、英文原文在下，輸出單一離線 HTML，右側可對照 Fig. 1–N、Fig. S1–N 與所有 SI 表格，並檢查段落完整性。

### 在本機產生 HTML

需求：Python 3.10+；擷取 DOCX 時安裝 `python-docx`，HTML 組裝只用標準函式庫。

```bash
python -m pip install python-docx
python scripts/extract_docx.py manuscript.docx --role ms --out work/ms.json --assets work/ms-images
python scripts/extract_docx.py supporting.docx --role si --out work/si.json --assets work/si-images
```

這兩份 JSON 只有抽取後的原文骨架，**不是翻譯完成的資料**。請依 [`reader-json-spec.md`](references/reader-json-spec.md) 完整填入繁中翻譯、確認圖片與圖說配對，再執行：

```bash
python scripts/build_reader.py filled_translation.json -o paper_bilingual_reader.html
```

執行不含私人資料的範例：

```bash
python scripts/build_reader.py examples/demo_reader.json -o demo.html
```

可參考 [範例 HTML](examples/demo_output.html) 和 [通用示意圖](assets/demo-figure.svg)。

## 🧩 段落與圖說格式

| 原稿位置 | 標示 |
| --- | --- |
| Introduction 第二段 | `Introduction · P2` |
| Results 中 Fig. 3 的第二段 | `Fig. 3 · P2` |
| Experimental 的電化學表徵第二段 | `Experimental section — Electrochemical Characterization · P2` |
| 主圖 1 圖說 | `Fig. 1 caption` |
| SI 圖 2 圖說 | `Fig. S2 caption` |
| SI 表 1 表說 | `Table S1 caption` |

`P` 是 *paragraph*（段落）簡寫。主圖分組只是查核用導覽，不代表原稿新增子標題。圖說獨立顯示，不計入 Results 段落數。

## 🔐 正確性與保密

上傳 GitHub 的只有通用工具與虛構示範資料，**不包含未投稿或未公開的 MS/SI、原始圖像與研究結果**。正式論文必須檢查 Word 內嵌公式、浮動圖片、合併儲存格與引用文獻，確實完成段落逐一比對後，才能宣稱全文翻譯完成。不得擅自更改論文原始數據或以模型生成示意圖取代原始實驗圖。