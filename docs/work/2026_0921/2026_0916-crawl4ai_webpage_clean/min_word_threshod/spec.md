# Crawl4AI 網頁清洗改善 — 第一層：min_word_threshold

## Overview

透過在 `PruningContentFilter` 新增 `min_word_threshold` 參數，自動移除短文本雜訊（如 `更多`、`前一頁`、`第一頁` 等 2~5 字的導覽元素），減少人工維護 `exclude_words` 的負擔。改動範圍小（~10 行代碼）、零風險、不影響主要內容。

## Functional Requirements

- **FR-001**: `PruningContentFilter` 必須接收 `min_word_threshold` 參數，低於該字數門檻的 HTML 區塊直接移除
- **FR-002**: `WebsiteCrawlerConfig` dataclass 必須新增 `min_word_threshold: int` 欄位，預設值為 `10`
- **FR-003**: `WebsiteCrawler.__init__` 必須新增 `min_word_threshold` 參數，並傳入 `PruningContentFilter`
- **FR-004**: `INIT_KEYS` 必須包含 `min_word_threshold`，使其可從 TOML 設定檔載入
- **FR-005**: `configs/website_crawler/default.toml` 的 `[init]` section 必須新增 `min_word_threshold = 10`
- **FR-006**: `configs/website_crawler/nculab.toml` 的 `[init]` section 必須新增 `min_word_threshold = 10`
- **FR-007**: `override_init_config` 必須支援覆寫 `min_word_threshold`
- **FR-008**: `_validate_config` 必須驗證 `min_word_threshold` 為正整數
- **FR-009**: 實作完成後，必須以 nculab 站點分別執行「無 `min_word_threshold`」與「`min_word_threshold=10`」兩次爬取，產出 `fit_markdown` 並產生差異比較報告，作為功能驗收依據

## User Stories

- US1: 作為開發者，我希望透過設定 `min_word_threshold` 自動過濾短文本雜訊，這樣我就不用逐一將 `更多`、`前一頁` 等雜訊加入 `exclude_words`

### Acceptance Criteria

- **AC1**: Given `min_word_threshold=10`，When 爬取 nculab 網站，Then `fit_markdown` 中不應包含低於 10 字的孤立文本區塊（如 `更多`、`前一頁`、`第一頁`）
- **AC2**: Given `min_word_threshold=10`，When 爬取 nculab 網站，Then 主要內容（正文段落、成員介紹、研究方向）必須完整保留
- **AC3**: Given 未設定 `min_word_threshold`，When 爬取網站，Then 使用預設值 `10`（向後相容）
- **AC4**: Given `min_word_threshold` 設為非整數或負數，When 載入設定檔，Then 拋出 `ConfigValidationError`
- **AC5**: Given 實作完成，When 以 nculab 站點分別執行無 `min_word_threshold` 與 `min_word_threshold=10` 兩次爬取，Then 產生 `fit_markdown` 差異比較報告，其中可觀察到短文本雜訊（如 `更多`、`前一頁`、`第一頁`）被移除且主要內容保留

## Verification: A/B Markdown 比較

### 目的

以量化方式驗證 `min_word_threshold` 的實際效果，確保短文本雜訊被移除且主要內容不受影響。

### 執行步驟

1. **Baseline（無 min_word_threshold）**：以 nculab 設定檔爬取，不傳入 `min_word_threshold`（使用 crawl4ai 預設行為）
2. **實驗組（min_word_threshold=10）**：以 nculab 設定檔爬取，傳入 `min_word_threshold=10`
3. **差異比較**：
   - 逐頁比較兩份 `fit_markdown` 的行數差異
   - 列出被移除的行（預期為低於 10 字的短文本區塊）
   - 確認被移除的行不包含主要內容（正文段落、成員介紹、研究方向）
4. **輸出報告**：將比較結果記錄至 `runs/` 目錄，供人工審核

### 預期結果

| 指標 | 預期 |
|------|------|
| 被移除行的字數 | 全部 < 10 字 |
| 主要內容保留率 | 100%（正文段落不應被移除） |
| 雜訊移除率 | 可觀測到 `更多`、`前一頁` 等短文本消失 |

## Edge Cases

- `min_word_threshold=0`：不應允許（應改為 1 或以上，避免無意義過濾）
- `min_word_threshold` 過高（如 100）：可能誤刪較短但有意义的內容（如標題、列表項）
- 混合語言內容：中文字數計算以字元為單位（非詞組），與 crawl4ai 內部邏輯一致

## Out of Scope

- 第二層 `threshold_type="dynamic"` 動態閾值（不實作）
- 第三層 BM25 二次過濾（不實作）
- `exclude_words` 邏輯變更（保持現有行為）
- 其他站點（ncucsie 等）的 TOML 設定更新（後續批次處理）

## Assumptions

- crawl4ai 的 `PruningContentFilter` 已支援 `min_word_threshold` 參數（已確認 API）
- `min_word_threshold` 的字數計算以字元為單位（與 crawl4ai 內部邏輯一致）
- 現有 `WebsiteCrawler` 的 `__init__` 參數變更為向後相容（新增可選參數，不影響現有調用）

## Open Questions

- 無
