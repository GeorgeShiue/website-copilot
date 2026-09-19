# 動態閾值（threshold_type="dynamic"）功能規格

## Overview

新增 `threshold_type` 參數至 `PruningContentFilter`，支援 `"fixed"`（現有行為）與 `"dynamic"`（自動計算閾值）兩種模式。透過 AB test 比較兩種模式對網頁 Markdown 品質的影響，驗證動態閾值是否能自動適應不同頁面佈局，減少內容遺漏或雜訊殘留。

## Functional Requirements

- FR-001: 在 `WebsiteCrawlerConfig` 中新增 `threshold_type` 欄位，類型為 `str`，預設值為 `"fixed"`
- FR-002: 在 `WebsiteCrawler.__init__()` 中新增 `threshold_type` 參數，預設值為 `"fixed"`
- FR-003: 在 `_crawl_website_async()` 中將 `threshold_type` 傳入 `PruningContentFilter`
- FR-004: 在 `INIT_KEYS` 集合中新增 `"threshold_type"`
- FR-005: 在 TOML 設定檔中新增 `threshold_type` 欄位
- FR-006: 在 `_validate_config()` 中新增 `threshold_type` 驗證邏輯
- FR-007: 在 `WebsiteCrawlerModuleConfig` 中新增 `threshold_type` 欄位以支援 CLI 覆寫
- FR-008: 建立 AB test 腳本，比較 `"fixed"` 與 `"dynamic"` 模式的爬取結果

## User Stories

### US1: 系統管理員配置閾值模式

作為系統管理員，我希望能在 TOML 設定檔中指定 `threshold_type`，以便選擇使用固定閾值或動態閾值。

**驗收標準：**
- AC1: Given 設定檔中 `threshold_type = "fixed"`，When 執行爬取，Then `PruningContentFilter` 使用固定閾值模式
- AC2: Given 設定檔中 `threshold_type = "dynamic"`，When 執行爬取，Then `PruningContentFilter` 使用動態閾值模式
- AC3: Given 設定檔中未指定 `threshold_type`，When 執行爬取，Then 使用預設值 `"fixed"`

### US2: 開發者透過 CLI 覆寫閾值模式

作為開發者，我希望能透過 CLI 參數臨時覆寫 `threshold_type`，以便快速測試不同模式。

**驗收標準：**
- AC1: Given CLI 傳入 `--threshold-type dynamic`，When 執行爬取，Then 使用動態閾值模式
- AC2: Given CLI 傳入 `--threshold-type fixed`，When 執行爬取，Then 使用固定閾值模式

### US3: 自動適應不同頁面佈局

作為使用者，我希望動態閾值能自動適應不同佈局的頁面（如 Google Sites vs 原生 HTML），減少人工調參需求。

**驗收標準：**
- AC1: Given 使用動態閾值模式爬取 Google Sites 頁面，When 比較 `fit_markdown`，Then 內容保留率不低於固定閾值模式
- AC2: Given 使用動態閾值模式爬取 Google Sites 頁面，When 比較 `fit_markdown`，Then 雜訊殘留率不高於固定閾值模式

## Edge Cases

- **無效的 threshold_type 值**：若設定檔中 `threshold_type` 值不是 `"fixed"` 或 `"dynamic"`，應拋出 `ConfigValidationError`
- **混合模式測試**：同一網站中部分頁面適合固定閾值，部分適合動態閾值，動態模式應能自動適應
- **極端頁面佈局**：文字密度極高或極低的頁面，動態模式不應產生異常結果

## Out of Scope

- BM25ContentFilter 二次過濾（第三層功能，另行規劃）
- LLMContentFilter 語義過濾
- 動態閾值的自定義演算法（使用 crawl4ai 內建實現）
- 跨網站的閾值遷移學習

## Assumptions

- crawl4ai 的 `PruningContentFilter` 已支援 `threshold_type="dynamic"` 參數
- 動態閾值模式的內部演算法由 crawl4ai 實現，本專案僅需正確傳遞參數
- 現有的 `exclude_words` 機制仍會在 Markdown 清洗層繼續使用
- AB test 應在同一網站、相同爬取範圍下進行，以確保結果可比較

## Resolved Questions

1. 動態閾值模式不需要額外參數，直接使用 crawl4ai 內建的 `threshold_type="dynamic"` 行為
2. AB test 僅在 nculab 站點上進行測試，使用現有設定（max_depth=2）爬取所有可达頁面
3. 評估指標包含自動指標（內容保留率 + 雜訊殘留率）加上 Verifier Agent 自行進行評估
4. 成功標準：動態模式的內容保留率不低於固定模式，且雜訊殘留率不高於固定模式
5. AB test 結果應以對比表格 + 圖表呈現，記錄於 `docs/work/2026_0921/crawl4ai_clean/dynamic_threshold/ab_test_report.md`
6. 需執行回歸測試，確認 `threshold_type="fixed"` 行為不變

---

## Spec Complete

- **路徑**: `/home/george/website-copilot/docs/work/2026_0921/crawl4ai_clean/dynamic_threshold/spec.md`
- **需求數量**: 8 個功能需求
- **使用者故事數量**: 3 個
- **澄清輪數**: 2 輪（共 7 個問題）
- **未解決問題**: 無
- **規格狀態**: 已確認
- **範圍界定**: 是

---

## Implementation Status

- **實作日期**: 2026-09-16
- **實作狀態**: ✅ 已完成
- **驗證狀態**: ✅ PASS（8/8 FRs, 9/9 ACs）
- **回歸測試**: ✅ 153 passed, 0 failures
- **AB Test 結果**: 動態模式比固定模式減少 0.42% 字元數，執行速度快 8.5%
- **完成任務**: T001–T008 全部完成
