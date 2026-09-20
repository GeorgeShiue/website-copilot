# 網站爬蟲整合 vote1 LLM 產生 exclude_words：規劃

## Overview

`survey.md` 的實驗（方案 4）已選定 vote1：對全站原始 fit_markdown 重複 5 次「隨機抽 10% 頁面 → LLM 提議 → 程式端過濾」，取聯集。此流程只存在於 `scripts/ab_test_llm_exclude_words.py`，需接進正式爬蟲流程，讓新站台不必人工貼 `exclude_words`。

## 關鍵限制

`WebsiteCrawler._filter_crawl_results` 原本在去重時就地呼叫 `clean_markdown(exclude_words=...)`，此時尚未有全站頁面，無法先產生詞。必須把「去重」與「清理」拆開：先收齊原始 fit_markdown → 產生詞 → 再清理。

## Architecture Decisions

| Decision | Choice | Rationale | Alternatives Considered |
|---|---|---|---|
| 清理與產生詞的位置 | 新增 `src/app/engines/webpage_markdown_cleaner.py`，類別 `WebpageMarkdownCleaner`；由 `src/utils/markdown_cleaner.py` 以 `git mv` 搬入 | 使用者要求把 cleaner 內容一併重新包裝；風格對齊 `WebpageImageSummarizer` | 另建 `exclude_words_generator.py`，與 cleaner 分開 |
| 類別介面 | 有狀態類別，`clean_markdown`、`promote_empty_heading_line`、`sample_pages`、`guard_words`、`count_word_hits` 為 staticmethod | 腳本可無狀態呼叫；與其他 engines 風格一致 | 保留模組層級 `clean_markdown` |
| 設定位置 | `[clean]` 區塊；`exclude_words` 由 `[crawl]` 搬入 | 使用者要求，清理設定集中 | 只放新參數，`exclude_words` 留 `[crawl]` |
| 參數命名 | 僅 `llm_exclude_words`、`llm_model` 帶 `llm_` 前綴，其餘為 `sample_ratio`、`repeat`、`max_prompt_tokens`、`seed` | 使用者指定 | 全部帶前綴 |
| 預設值 | `llm_exclude_words = false` | 避免現有站台行為改變與意外花費 | 預設開啟 |
| 舊 key 相容 | 不做；一次遷移 6 個 toml | 使用者選擇搬移；相容層增加複雜度 | `[crawl]` 舊 key 過渡期照讀 |
| 人工詞與 LLM 詞 | 取聯集（人工在前、去重），人工清單存在時仍一律呼叫 LLM | 使用者選擇；行為單純 | 人工優先、LLM 取代人工 |
| 失敗處理 | 單次呼叫失敗只略過該次；全部失敗或 prompt 超過 `max_prompt_tokens` 則整個 workflow 失敗 | 使用者選擇；避免未清乾淨的資料被誤用 | 退回人工清單並警告 |
| `generate_exclude_words` 回傳 | 完整：words、votes、seed、samples、runs、raw_runs、usages（`cost_usd` 為屬性） | 可完整重現與審查 | 精簡版、加每詞命中行數 |
| `clean_pages` 回傳 | 只回傳 `dict[str, str]` | 與現有 `fit_markdown` 欄位相容 | 附被刪行明細或字元統計 |
| 落盤與 log | `generated_exclude_words.toml`、`exclude_words_report.json`、rich log 表格（詞、得票、命中行數、成本） | 使用者選擇；不額外保存清理前原文 | 另存原始 markdown |

## 修改範圍

1. **`webpage_markdown_cleaner.py`**：清理邏輯原樣搬入；新增 `sample_pages`、`guard_words`、`_propose_words`、`generate_exclude_words`、`count_word_hits`、`GenerationResult`、`ExcludeWordsGenerationError`。
2. **`website_crawler.py`**：`_filter_crawl_results` 只去重、保存原文；新增 `_resolve_exclude_words`、`_clean_results`；流程為 crawl → filter → clean（含產生詞）→ enrich；新增 `cleaner` 建構參數與 `llm_exclude_words` 執行參數。
3. **`website_crawler_config.py` 與 toml**：新增 `[clean]` 區塊、欄位與驗證；6 個 toml 遷移。
4. **`workflow.py` / `run_persistence.py`**：workflow 依 `[clean]` 建立 cleaner；落盤與 log 由 `run_persistence.py` 的 `save_generated_exclude_words` 負責。
5. **`scripts/ab_test_llm_exclude_words.py`**：改用 cleaner 的共用函式，避免兩份實作。
6. **文件**：`README.md`、`docs/code/runs/config.md`（`docs/work/`、`docs/survey/` 歷史文件不改）。

## 破壞性變更

`exclude_words` 移到 `[clean]` 後，舊 toml 與 `runs/` 內保存的舊 module config 無法直接重用；`[crawl]` 殘留的 `exclude_words` 只會被警告並略過。`[clean]` 區塊必填，缺席時 `load_config_section_from_toml` 拋 `ConfigNotFoundError`（與其他 section 行為一致）。

## 規劃過程中釐清的模糊之處

計畫審查時挑出並由使用者決定：

| 議題 | 決定 |
|---|---|
| 人工清單存在時是否仍呼叫 LLM | 聯集，一律呼叫 |
| LLM 失敗時退回或失敗 | 整個 workflow 失敗 |
| cleaner 介面形式 | 類別加 staticmethod |
| `exclude_words` 是否搬到 `[clean]` | 搬 |

## 驗證計畫

1. 單元測試：`guard_words`、`sample_pages`、`generate_exclude_words`（mock）、失敗處理、`clean_pages`。
2. 回歸：`llm_exclude_words=false` 時 nculab 輸出與舊版逐頁相同。
3. 端到端：nculab 開啟 LLM，確認落盤檔與清理結果；再跑 ncucsie 看詞數與成本。
4. 失敗行為：以極小 `max_prompt_tokens` 觸發，確認 workflow 失敗。

## 已知風險（承接 survey，不在本次處理）

- vote1 聯集會納入只在單次抽樣出現的詞，可能誤刪正文（survey 已見 `Post date:`、`enter image description here`）。
- 人工審核關卡與全站出現比例門檻已決定留待後續；落盤的 `generated_exclude_words.toml` 供事後檢視。

## 後續候選

- 在 `guard_words` 加「詞須命中全站 ≥ X% 頁面」過濾，擋掉泛用詞（見 dev.md 的 ncucsie 結果）。
- CLI 只開放 `--module.max-pages`，`[clean]` 參數需改 toml；可在 `WebsiteCrawlerModuleConfig` 加旗標。
- `cli.py` 不檢查爬取回傳值，失敗時 exit code 仍為 0。
