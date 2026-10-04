# 驗證紀錄

各階段 commit 前的驗證結果（共通驗證 C1–C7 與獨特驗證，見 [plan.md](plan.md)「驗證機制」）。

## P0：爬蟲排除文件 URL

### 自動化

- `scripts/check.sh`：ruff、pyright 通過；`pytest tests/unit` 475 passed、1 failed。
  - 失敗的 `test_cli.py::test_serve_command` **與 P0 無關**：在未改動的 HEAD（stash 後）同樣失敗，原因是 `f1d573b` 將 `serve` 改名為 `run_serve` 後測試未同步。未在本階段處理。
- 新增 `tests/unit/test_document_rules.py`（36 個測試）：
  - 副檔名大小寫（`.PDF`、`.Docx`）、帶 query／fragment 仍判為文件；
  - `.php`、`pdf.gif%20`、`doc.gif`、`?file=a.pdf`（副檔名只在 query）不被誤判；
  - `downloadfile` 站點樣式只在提供 `url_patterns` 時命中；
  - `SiteDocumentsConfig` 預設 `[]`，ncucsie 為 `["*Action=downloadfile*"]`、nculab 為 `[]`；
  - `WebsiteCrawler._build_filter_chain()`：文件 URL 不通過，一般頁面通過，無站點過濾時仍排除文件；
  - `success=False` 記錄實際 `error_message`、計入 `error_failed`，不再記為 `no markdown`。

### 實跑（ncucsie，`--run.no-publish`，`runs/20261004_170334/`）

| 指標 | 舊（data/raw_webpages） | 新 |
|---|---|---|
| 頁面數 | 149 | 146 |
| `error_no_markdown` | 47 | 0 |
| `error_failed`（新） | — | 3 |
| `error_404` | — | 6 |
| 導航觸發 `Download is starting` | 約 45 | 1 |

頁面集合差異（舊 149 vs 新 146）：

- 舊有新無 5 筆：
  - `p_406-1013-13291,r375.php`、`p_406-1013-13922,r376.php`：新增公告擠掉舊公告，新有 `p_406-1013-14068,r375.php`、`p_406-1013-14070,r376.php`，屬網站內容變動；
  - `static_file_13_1013_img_222010142.png`、`..._143_hackathon_taiwan.jpg`：圖片 URL，舊次被當成空頁面（fit_markdown 長度 0），這次被 anti-bot 檢查判為 `success=False`（`minimal_text`）而略過，無實質內容損失；
  - `~ypcheng`：舊次為 120 字元的外部個人頁，這次未取得，原因未查（疑為網站或連線波動）。
- 新有舊無 2 筆：即上述公告。

`error_failed` 的 3 筆：兩張圖片（anti-bot）與 `static/file/13/1013/img/681518947`（無副檔名的附件，導航時下載，Unexpected error）。

### 已知限制

- 無副檔名且非站點樣式的附件（如 `681518947`）無法由 URL 規則辨識，仍會被導航一次並記為 `error_failed`；P2a 的 DocumentCollector 以內容判斷格式，屆時再評估是否補站點樣式。

### 費用

exclude words 的 LLM 呼叫（小額，未另行統計）。
