# winnow-md 整合比較實驗任務清單

**完成日期**：2026-09-17

## 覆蓋矩陣

| Spec Ref | Tasks |
|---|---|
| FR-001 | T001, T002, T003, T004 |
| FR-002 | T002 |
| FR-003 | T005 |
| FR-004 | T006 |
| FR-005 | T006 |
| FR-006 | T008 |
| US1/AC1 | T002, T007 |
| US1/AC2 | T006 |
| US1/AC3 | T005, T006 |
| US2/AC1 | T006 |
| US2/AC2 | T006 |
| US2/AC3 | T006 |
| US3/AC1 | T008 |
| US3/AC2 | T008 |
| US3/AC3 | T008 |
| Edge Cases | T007 |

---

## Phase 1: Setup

- [x] T001: 建立 ab_test_winnow.py 腳本骨架 per FR-001
  - Files: `scripts/ab_test_winnow.py`
  - Acceptance:
    - Given 腳本已建立，When 以 `uv run python scripts/ab_test_winnow.py --help` 執行，Then 不產生 ImportError
    - Given 腳本已建立，When 檢視檔案結構，Then 包含必要的 import 語句（`time`、`os`、`winnow`、`utils.markdown_cleaner.clean_markdown`、`app.engines.website_crawler.WebsiteCrawler`、`app.configs.WebsiteCrawlerConfig`）
    - Given 腳本已建立，When 檢視常數定義，Then 包含 `AGGRESSIVENESS = 0.5` 及 `CONFIG_NAME = "nculab"`
  - Depends on: none

## Phase 2: Core Implementation

- [x] T002: 實現 nculab 網站爬取邏輯 per FR-002
  - Files: `scripts/ab_test_winnow.py`
  - Acceptance:
    - Given 腳本載入 nculab 設定，When 呼叫 `WebsiteCrawlerConfig.from_toml("nculab")`，Then 回傳有效的設定物件且 `site_id == "nculab"`
    - Given 設定已載入，When 建立 `WebsiteCrawler` 並呼叫 `crawl_website()`，Then 回傳非空的 `dict[str, dict]` 結果
    - Given 爬取結果已取得，When 檢視結果結構，Then 每筆包含 `url`、`fit_markdown` 欄位
  - Depends on: T001

- [x] T003: 實現 baseline 清理邏輯（復用 clean_markdown）per FR-001
  - Files: `scripts/ab_test_winnow.py`
  - Acceptance:
    - Given 已取得爬取結果，When 逐頁呼叫 `clean_markdown(fit_markdown, exclude_words)`，Then 每頁產生清理後的文字
    - Given baseline 清理完成，When 檢視輸出結構，Then 回傳 `dict[page_title, str]` 格式（title 為 dedup_key，value 為清理後 Markdown 文字）
    - Given 設定檔含 `exclude_words`，When 執行 baseline 清理，Then `exclude_words` 正確傳入 `clean_markdown()`
  - Depends on: T002

- [x] T004: 實現 winnow 清理邏輯（使用 clean_many）per FR-001
  - Files: `scripts/ab_test_winnow.py`
  - Acceptance:
    - Given 已取得爬取結果，When 建立 `Winnow(aggressiveness=0.5)` 實例，Then 實例成功建立且 aggressiveness 為 0.5
    - Given 已收集所有頁面的 `(fit_markdown, url)` tuple，When 呼叫 `w.clean_many(pages)`，Then 回傳與頁面數量相同的結果列表
    - Given winnow 清理完成，When 檢視每個結果物件，Then 可存取 `.markdown`（清理後文字）、`.removed`（移除區塊列表）、`.stats`（統計資訊）
    - Given winnow 清理完成，When 檢視輸出結構，Then 回傳 `dict[page_title, str]` 格式（title 為 dedup_key，value 為清理後 Markdown 文字）
  - Depends on: T002

## Phase 3: Metrics & Report

- [x] T005: 實現四項評估指標計算 per FR-003
  - Files: `scripts/ab_test_winnow.py`
  - Acceptance:
    - Given baseline 與 winnow 清理結果已取得，When 計算 token 減少率，Then 使用公式 `(tokens_before - tokens_after) / tokens_before`（使用 winnow `result.stats` 中的 token 計算）
    - Given 兩種清理結果已取得，When 計算內容保留率，Then 使用公式 `len(winnow_text) / len(baseline_text)`（以字元數計）
    - Given winnow `result.removed` 已取得，When 計算雜訊殘留率，Then 統計 `removed` 區塊中 baseline 未處理的比例（即 winnow 多移除的雜訊佔比）
    - Given 清理流程已執行，When 計算處理時間，Then 使用 `time.perf_counter()` 記錄各模式的 wall-clock time
    - Given 某頁面清理後文字為空，When 計算指標，Then 該頁面被排除不納入統計
  - Depends on: T003, T004

- [x] T006: 實現 Markdown 比較報告產出 per FR-004, FR-005
  - Files: `scripts/ab_test_winnow.py`
  - Acceptance:
    - Given 指標已計算完成，When 產出報告，Then 檔案路徑為 `runs/<timestamp>/ab_test_winnow/report.md`（timestamp 格式 `YYYYMMDD_HHMMSS`）
    - Given 報告已產出，When 檢視報告內容，Then 包含表頭列：`| Page | Baseline Chars | Winnow Chars | Token Reduction % | Content Retention % | Noise Residual % | Time (s) |`
    - Given 報告已產出，When 檢視報告內容，Then 每頁佔一行，數據與指標計算結果一致
    - Given 報告已產出，When 檢視報告最後一列，Then 包含 `**Average**` 彙總列，數值為各頁面的平均值
    - Given 報告已產出，When 檢視報告內容，Then 包含代碼整合建議章節（說明如何將 winnow-md 整合至 `WebsiteCrawler` pipeline）
    - Given 報告已產出，When 檢視報告中的百分比欄位，Then 格式為 `XX.X%`（一位小數）
  - Depends on: T005

## Phase 4: Execution & Validation

- [x] T007: 執行腳本並驗證報告輸出 per FR-004, US1/AC1, US1/AC2
  - Files: `scripts/ab_test_winnow.py`, `runs/<timestamp>/ab_test_winnow/report.md`
  - Acceptance:
    - Given 腳本所有功能已實作完成，When 以 `uv run python scripts/ab_test_winnow.py` 執行，Then 腳本成功完成且不產生例外
    - Given 腳本執行完成，When 檢查 `runs/<timestamp>/ab_test_winnow/` 目錄，Then `report.md` 檔案存在
    - Given report.md 已產出，When 檢視報告統計表，Then 包含所有 nculab 頁面的數據（無遺漏）
    - Given report.md 已產出，When 檢視彙總列，Then token 減少率約在 30-40% 範圍內、內容保留率 >95%
    - Given winnow-md 已安裝，When 腳本執行，Then 不出現 winnow 未安裝的錯誤提示
    - Given nculab 網站可連線，When 腳本執行，Then 爬取流程成功完成（無 404 或連線失敗導致的中止）
  - Depends on: T006

## Phase 5: Additional Features

- [x] T008: 實現 Markdown 輸出保存（FR-006）per FR-006, US3/AC1, US3/AC2, US3/AC3
  - Files: `scripts/ab_test_winnow.py`
  - Acceptance:
    - Given 腳本執行完成，When 檢視 `runs/<timestamp>/ab_test_winnow/baseline/` 目錄，Then 包含所有頁面的 baseline 清理後 Markdown
    - Given 腳本執行完成，When 檢視 `runs/<timestamp>/ab_test_winnow/winnow/` 目錄，Then 包含所有頁面的 winnow 清理後 Markdown
    - Given 兩個目錄均已產出，When 比較同名檔案，Then 可直接觀察兩種清理模式的差異
  - Depends on: T006

---

## 任務依賴圖

```
T001 (Setup)
  └─> T002 (Crawl)
        ├─> T003 (Baseline cleanup)
        │     └─> T005 (Metrics) ─> T006 (Report) ─> T007 (Execute & Validate)
        │                                └─> T008 (Save Markdown outputs)
        └─> T004 (Winnow cleanup) ┘
```

## 平行化機會

| 可平行任務 | 說明 |
|---|---|
| T003 + T004 | baseline 與 winnow 清理邏輯可同步實作（均僅依賴 T002） |
