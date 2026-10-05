---
name: progress-report
description: 製作專案進度簡報（Marp）。參考前一份進度簡報的內容與排版，讀取 docs/work/ 最新工作資料夾取得進度，先規劃大綱供使用者審核，核可後產出簡報並驗證版面。當使用者要求「做進度簡報」「規劃進度簡報大綱」「產出 marp 簡報」時使用。
---

# 專案進度簡報製作流程

簡報放在 `docs/progress_report/<YYYY_MMDD>/`，日期為報告日，取 `docs/work/` 底下日期最新的資料夾名稱（例如最新為 `2026_1005`，報告日就是 `2026_1005`，簡報放 `docs/progress_report/2026_1005/`，檔名 `2026_1005_marp.md`）。全程使用繁體中文。

## 1. 參考前一份進度簡報

- 在 `docs/progress_report/` 找日期最新的資料夾（`marp-theme.css` 是共用主題，不是簡報），讀其 `*_marp.md`，必要時看 `flow.mmd`。
- 沿用的內容結構：封面（lead）→ 大綱 → 背景與目標（承接上次進度）→ 各主題（lead 分隔頁 + 表格或流程圖）→ 成果總結 → 後續規劃。
- 沿用的排版：frontmatter（`marp: true`、`theme: default`、`paginate: true`、`size: 16:9`）、`@import url('../marp-theme.css')`、分隔頁的 `<!-- _class: lead -->` 與 scoped `h1 { font-size: 52px; }`、流程圖 `![w:1160](flow.png)`。
- 「背景與目標」要銜接前一份簡報的「後續規劃」。

## 2. 讀取最新的工作進度

- `docs/work/` 下日期最新的資料夾（即報告日資料夾；`todo.md` 等檔案不算），其內每個子資料夾是一項工作，含 `plan.md`、`dev.md`，有時有 `verification.md`。
- 另讀 `docs/work/todo.md` 確認完成與未完成項目（後續規劃的來源）。
- 數字（耗時、花費、數量、前後對照）一律取自這些文件，不憑記憶；兩份文件不一致時以 `verification.md`／`dev.md` 的實測為準。
- 若子資料夾很多，只讀各自 `plan.md` 的 Context 與表格摘要，再針對要用的工作深入。

## 3. 規劃大綱，交使用者審核

- 先列「簡單列點」大綱，再依使用者要求展開成**每頁規劃表**（頁碼、頁面、類型〔lead／條列／表格／圖〕、內容）。
- 若工作項目多，**不要全部塞進簡報**：詢問或提出建議哪些是主軸、哪些省略；使用者常會要求聚焦單一主題，並排除重構、技術債等與主軸無關的內容。
- 標明需要產出的素材（流程圖、哪一頁用）與數字出處。
- **在此停下，等使用者核可後才產出簡報。** 使用者提出修改就更新大綱再送審，不要自行開始實作。

## 4. 產出簡報並驗證

產出：`<日期>_marp.md`、需要的 `flow.mmd`→`flow.png`、`<日期>_marp.pdf`。

```bash
cd docs/progress_report/<日期>
mmdc -i flow.mmd -o flow.png -s 3 -b white
CHROME_PATH=$(ls -d ~/.cache/puppeteer/chrome/*/chrome-linux64/chrome | head -1) \
  npx --yes @marp-team/marp-cli <日期>_marp.md --pdf --allow-local-files --browser-timeout 90 -o <日期>_marp.pdf
```

驗證（缺一不可）：

1. **逐頁看圖**：用 `--images png` 輸出到 scratchpad，讀圖檢查每頁是否溢出、換行是否難看、圖是否過小。表格行數多時優先檢查。
2. **溢出就拆頁或精簡**：把表格依主題分組拆成兩頁，或縮短文字、把次要項目改成表格下方備註；拆頁後同步大綱頁。
3. **數字核對**：簡報中的數字與步驟 2 的來源文件逐項核對。
4. 修改後重新輸出 PDF，並向使用者說明哪些頁有檢查、哪些沒有。

### 已知陷阱

- **marp／mmdc 第一次執行常逾時（exit 143）**：確認檔案是否已寫入，再重跑一次即可；不要用 `pkill -f marp`（會連自己的 shell 一起終止）。
- **用 Python 取代某頁內容時，不要用 `s.index('---', ...)` 找頁尾**：會先比對到表格分隔線 `|------|`，造成殘留片段。改用 `\n---\n` 或直接用 Edit 工具。
- 使用者會自行修改簡報；後續只動被指定的頁面，不要覆蓋其他修改。修改前先重新讀檔。
- 簡報與 `flow.mmd` 的修改要連動：改流程圖後重畫 PNG 並重新輸出 PDF。
- 不主動 git commit，除非使用者要求。
