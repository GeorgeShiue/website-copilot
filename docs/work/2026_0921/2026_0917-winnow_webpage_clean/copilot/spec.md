# winnow-md 整合比較實驗規格

## Overview

比較 `winnow-md` 的 `clean_many()` 批次清理與現有 `_filter_crawl_results()` 使用 `clean_markdown()` 的清理效果差異。以 nculab 網站為測試目標，評估 token 減少量、內容保留率、雜訊残留率及處理時間，產出比較報告與代碼整合建議。

## Functional Requirements

- FR-001: 建立 AB test 比較腳本，支援 `baseline`（現有 `clean_markdown()`）與 `winnow`（`clean_many()`）兩種清理模式
- FR-002: 腳本需以 nculab 網站作為測試資料來源，執行完整爬取流程
- FR-003: 計算並記錄四項評估指標：token 減少率、內容保留率、雜訊残留率、處理時間
  - token 減少率：`(tokens_before - tokens_after) / tokens_before`
  - 內容保留率：比較清理前後的文字量比例
  - 雜訊残留率：`winnow removed` 區塊中，`clean_markdown` 未處理的比例（即 winnow 多移除的雜訊）
  - 處理時間：各模式的 wall-clock time
- FR-004: 產出 Markdown 比較報告，每頁一行指標，最後加一列彙總（平均/總計）
- FR-005: 提供代碼整合建議，說明如何將 winnow-md 整合至 `WebsiteCrawler` pipeline
- FR-006: 保留兩種清理模式的 Markdown 輸出，供人工比較
  - baseline 版本：`runs/<timestamp>/ab_test_winnow/baseline/<page_title>.md`
  - winnow 版本：`runs/<timestamp>/ab_test_winnow/winnow/<page_title>.md`
  - 每個頁面一個獨立 Markdown 檔案，檔名使用 dedup_key

## User Stories

### US1: 開發者執行 AB test 比較

作為開發者，我希望執行一個腳本即可比較兩種清理模式的效果差異。

**驗收標準：**
- AC1: Given 執行 `uv run python ab_test_winnow.py`，When 腳本完成，Then 產出 `report.md` 比較報告
- AC2: Given 腳本執行完成，Then 輸出每頁一行指標 + 彙總列的統計表
- AC3: Given 腳本執行完成，Then 報告包含各頁面的 token 減少率、內容保留率、雜訊残留率

### US2: 系統管理員評估整合價值

作為系統管理員，我希望透過報告判斷是否值得將 winnow-md 整合至生產環境。

**驗收標準：**
- AC1: Given 閱讀比較報告，When 檢視 token 減少率，Then 能判斷 winnow 是否顯著優於 baseline
- AC2: Given 閱讀比較報告，When 檢視內容保留率，Then 能確認 winnow 不會誤刪重要內容
- AC3: Given 閱讀比較報告，When 檢視整合建議，Then 獲得具體的代碼修改方案

### US3: 開發者人工比較清理效果

作為開發者，我希望能在 AB test 後直接比較兩種清理模式的 Markdown 輸出，以便判斷清理品質。

**驗收標準：**
- AC1: Given 腳本執行完成，When 檢視 `runs/<timestamp>/ab_test_winnow/baseline/` 目錄，Then 包含所有頁面的 baseline 清理後 Markdown
- AC2: Given 腳本執行完成，When 檢視 `runs/<timestamp>/ab_test_winnow/winnow/` 目錄，Then 包含所有頁面的 winnow 清理後 Markdown
- AC3: Given 兩個目錄均已產出，When 比較同名檔案，Then 可直接觀察兩種清理模式的差異

## Edge Cases

- **winnow 未安裝**：腳本需檢查 winnow-md 是否已安裝，未安裝時提示安裝指令
- **爬取失敗**：若 nculab 網站無法連線，腳本需中止並報告錯誤
- **空頁面**：若某頁面清理後為空，指標計算需排除該頁面
- **中文內容**：winnow 詞典以英文為主，需觀察中文頁面的清理效果

## Out of Scope

- 其他網站的比較測試（僅限 nculab）
- winnow-md 的 `model` extra 安裝（僅使用 heuristics 模式）
- 即時串流清理（僅批次處理）
- 修改 `WebsiteCrawler` 生產代碼（僅提供建議）

## Assumptions

- nculab 網站可正常連線且爬取
- winnow-md 可透過 `uv add winnow-md` 安裝
- 現有 `clean_markdown()` 的 `exclude_words` 設定可復用
- 測試環境已安裝 crawl4ai 及相關依賴

## Open Questions

- winnow-md 對中文內容的清理效果是否足夠？（需實驗驗證）
- `aggressiveness` 參數應設定為何值？（建議從預設 0.5 開始）

## Implementation Status

**Date**: 2026-09-17
**Outcome**: ✅ 實驗完成

| Spec Ref | Status | 實際結果 |
|---|---|---|
| FR-001 | ✅ 完成 | AB test 腳本已建立並執行 |
| FR-002 | ✅ 完成 | nculab 網站爬取成功（52 頁，48 有效） |
| FR-003 | ✅ 完成 | 四項指標均已計算 |
| FR-004 | ✅ 完成 | report.md 已產出 |
| FR-005 | ✅ 完成 | 兩種整合建議已提供 |

### 實驗結論

- Token 減少率 13.2%（低於預期 30-40%）：多數頁面未觸發清理
- 內容保留率 87.8%（低於預期 >95%）：部分頁面被過度清理
- 處理速度 1.99x 加速：winnow 批次清理效率優於逐頁清理
- 建議調整 aggressiveness 至 0.2-0.3 以平衡效果
