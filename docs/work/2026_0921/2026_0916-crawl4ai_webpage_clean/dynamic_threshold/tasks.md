# 動態閾值（dynamic threshold）Task List

## Completion Status

- **完成日期**: 2026-09-16
- **所有任務狀態**: ✅ 已完成（9/9 tasks）

## Coverage Matrix

| Spec Ref | Tasks |
|---|---|
| FR-001 | T001 |
| FR-002 | T003 |
| FR-003 | T004 |
| FR-004 | T001 |
| FR-005 | T002 |
| FR-006 | T001 |
| FR-007 | T005 |
| FR-008 | T007, T008, T009 |
| US1/AC1-AC3 | T001, T002, T004 |
| US2/AC1-AC2 | T005, T006 |
| US3/AC1-AC2 | T007, T008 |

---

## Phase 1: Config Layer

- [x] T001: 在 `website_crawler_config.py` 中新增 `INIT_KEYS` 集合成員、`WebsiteCrawlerConfig` 欄位與 `_validate_config()` 驗證邏輯 per FR-001, FR-004, FR-006 [P]
  - Files:
    - 修改: `src/app/configs/website_crawler_config.py`
  - Acceptance:
    - `INIT_KEYS` 集合包含 `"threshold_type"` 字串
    - `WebsiteCrawlerConfig` dataclass 有 `threshold_type: str = "fixed"` 欄位
    - `_validate_config()` 對 `threshold_type` 做白名單驗證，僅允許 `"fixed"` 或 `"dynamic"` 兩個值
    - 傳入無效值（如 `"invalid"`）時，拋出 `ConfigValidationError`
    - `uv run pytest src/test/dev/ -v` 全數通過
  - Depends on: none

- [x] T002: 在 `configs/website_crawler/nculab.toml` 的 `[init]` section 新增 `threshold_type` 設定 per FR-005 [P]
  - Files:
    - 修改: `configs/website_crawler/nculab.toml`
  - Acceptance:
    - `[init]` section 包含 `threshold_type = "fixed"`
    - 透過 `WebsiteCrawlerConfig.from_toml("nculab")` 載入後，`config.threshold_type` 值為 `"fixed"`
  - Depends on: T001

---

## Phase 2: Engine Layer

- [x] T003: 在 `website_crawler.py` 的 `WebsiteCrawler.__init__()` 新增 `threshold_type` 參數並賦值 per FR-002 [P]
  - Files:
    - 修改: `src/app/engines/website_crawler.py`
  - Acceptance:
    - `WebsiteCrawler.__init__()` 簽章包含 `threshold_type: str = "fixed"` 參數
    - `self.threshold_type = threshold_type` 正確賦值
    - `WebsiteCrawler(threshold_type="dynamic")` 實例化成功，`instance.threshold_type == "dynamic"`
    - `WebsiteCrawler()` 不傳入 `threshold_type` 時，預設為 `"fixed"`
  - Depends on: none

- [x] T004: 在 `_crawl_website_async()` 中將 `threshold_type` 傳入 `PruningContentFilter` per FR-003
  - Files:
    - 修改: `src/app/engines/website_crawler.py`
  - Acceptance:
    - `PruningContentFilter(...)` 呼叫包含 `threshold_type=self.threshold_type` 參數
    - 當 `threshold_type="dynamic"` 時，爬取使用動態閾值模式
    - 當 `threshold_type="fixed"` 時，爬取使用固定閾值模式（向後相容）
  - Depends on: T003

---

## Phase 3: CLI Layer

- [x] T005: 在 `workflow_config.py` 的 `WebsiteCrawlerModuleConfig` 新增 `threshold_type` 覆寫欄位 per FR-007
  - Files:
    - 修改: `src/app/configs/workflow_config.py`
  - Acceptance:
    - `WebsiteCrawlerModuleConfig` dataclass 包含 `threshold_type: str | None = None` 欄位
    - CLI 參數 `--module.threshold-type dynamic` 可正確解析至該欄位
    - CLI 參數 `--module.threshold-type fixed` 可正確解析至該欄位
    - 不指定時，欄位值為 `None`（交由 config layer 預設值處理）
  - Depends on: T001

- [x] T006: 在 `workflow.py` 的 `run_website_crawler()` 中將 `threshold_type` 傳遞至 `WebsiteCrawler` per FR-007
  - Files:
    - 修改: `src/app/workflow/workflow.py`（唯讀參考 → 改為修改）
  - Acceptance:
    - `WebsiteCrawler(...)` 呼叫包含 `threshold_type=config.threshold_type` 參數
    - 當 CLI 傳入 `--module.threshold-type dynamic` 時，workflow 完整執行時 `threshold_type` 正確傳遞至 `WebsiteCrawler`
    - 當 CLI 未指定 `threshold_type` 時，使用 TOML 設定或預設值 `"fixed"`
  - Depends on: T003, T005

---

## Phase 4: AB Test & Validation

- [x] T007: 建立 AB test 腳本 `ab_test_dynamic_threshold.py` per FR-008
  - Files:
    - 新增: `dev/crawl4ai/ab_test_dynamic_threshold.py`
    - 唯讀參考: `src/app/configs/website_crawler_config.py`
  - Acceptance:
    - 使用 `WebsiteCrawlerConfig.from_toml("nculab")` 載入設定
    - 分別以 `threshold_type="fixed"` 與 `threshold_type="dynamic"` 執行爬取
    - 比較兩組結果的 `fit_markdown` 長度、頁面數量
    - **逐頁比較 `fit_markdown` 內容，找出有差異的頁面**
    - 輸出對比表格至 `runs/{timestamp}/ab_test_dynamic_threshold/`
    - 產生 `diff_pages.json`（差異頁面摘要）與 `diff_pages/` 目錄（個別頁面 markdown）
    - 產生 `ab_comparison_report.md` 報告，包含對比表格、差異頁面清單與結論
  - Depends on: T001, T003, T004

- [x] T008: 執行 AB test 並記錄結果
  - Files:
    - 唯讀參考: `dev/crawl4ai/ab_test_dynamic_threshold.py`
  - Acceptance:
    - 執行 `uv run python dev/crawl4ai/ab_test_dynamic_threshold.py` 成功完成
    - 產出 `runs/{timestamp}/ab_test_dynamic_threshold/fixed/` 目錄（含爬取結果）
    - 產出 `runs/{timestamp}/ab_test_dynamic_threshold/dynamic/` 目錄（含爬取結果）
    - 產出 `runs/{timestamp}/ab_test_dynamic_threshold/diff_pages.json`（差異頁面摘要）
    - 產出 `runs/{timestamp}/ab_test_dynamic_threshold/diff_pages/` 目錄（個別頁面 markdown）
    - 產出 `runs/{timestamp}/ab_test_dynamic_threshold/ab_comparison_report.md` 報告
    - 報告內容包含兩組模式的 `fit_markdown` 長度比較、頁面數量比較、差異頁面清單
  - Depends on: T007

- [x] T009: Verifier Agent 閱讀差異頁面並分析
  - Files:
    - 唯讀參考: `runs/{timestamp}/ab_test_dynamic_threshold/diff_pages/*.md`
    - 產出: `runs/{timestamp}/ab_test_dynamic_threshold/verifier_analysis.md`
  - Acceptance:
    - 閱讀 5 個顯著差異頁面的 fixed/dynamic markdown 檔案
    - 識別每頁被移除的具體內容（段落、連結）
    - 分類移除內容為「雜訊」或「有意義內容」
    - 產出 `verifier_analysis.md` 差異分析報告
    - 給出動態閾值是否改善/退化/維持內容品質的判斷
  - Depends on: T008

---

## Dependency Graph

```
Phase 1 (Config Layer):
  T001 ──→ T002
    │
Phase 2 (Engine Layer):
  T003 ──→ T004
    │
Phase 3 (CLI Layer):
  T001 ──→ T005 ──→ T006
    │                ↑
  T003 ─────────────┘
    │
Phase 4 (AB Test):
  T001 ──→ T007 ──→ T008 ──→ T009
  T003 ──→
  T004 ──→
```

## Critical Path

```
T001 → T003 → T004 → T007 → T008 → T009
```

## Parallelizable Tasks

| Group | Tasks |
|---|---|
| Config + Engine init | T001 [P], T003 [P] |
| Config file + CLI config | T002 (after T001), T005 (after T001) |

## Summary

- **Total tasks**: 9
- **Phases**: 4
- **Parallelizable tasks**: 2 (T001, T003 — marked [P])
- **Spec coverage**: 8/8 FRs covered
- **Critical path**: T001 → T003 → T004 → T007 → T008 → T009
