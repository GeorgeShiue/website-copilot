# 網站爬蟲整合 vote1 LLM 產生 exclude_words：實作日誌

## 實作紀錄

### [T001] 搬移並重新包裝 cleaner
- `git mv src/utils/markdown_cleaner.py src/app/engines/webpage_markdown_cleaner.py`，改寫為 `WebpageMarkdownCleaner`。
- 清理邏輯原樣搬入並改為 staticmethod，新增 `clean_pages`。
- 從實驗腳本搬入：`MIN_WORD_LEN`、`MIN_SAMPLE_PAGES`、`PROMPT`、`sample_pages`、`guard_words`、單次 LLM 呼叫 `_propose_words`；新增 `generate_exclude_words`、`count_word_hits`、`GenerationResult`、`ExcludeWordsGenerationError`。
- 與腳本的差異：prompt 超過上限改拋例外（腳本原為 `SystemExit`）；`raw_words` 不是 list 時視為空；`json` 解析失敗或 `AttributeError` 視為空詞。

### [T002] WebsiteCrawler 改流程
- `_filter_crawl_results` 只做 404／無 markdown／去重，保存原始 `fit_markdown`。
- 新增 `_resolve_exclude_words`（聯集，人工在前、`dict.fromkeys` 去重）與 `_clean_results`；`crawl_website` 依序執行並各自包 `_safe_step`，LLM 步驟失敗回傳 None。
- 新增 `cleaner` 建構參數、`llm_exclude_words` 執行參數，屬性 `generation_result`、`raw_pages`。

### [T003] 設定與 toml 遷移
- `website_crawler_config.py`：新增 `[clean]` section、`CLEAN_KEYS`、欄位（`llm_exclude_words`、`llm_model`、`sample_ratio`、`repeat`、`max_prompt_tokens`、`seed`、`exclude_words`）與驗證；`exclude_words` 移出 `CRAWL_KEYS`。
- 6 個 toml（`default`、`nculab`、`ncucsie`、`test`、`test_nculab`、`test_ncucsie`）以腳本遷移：`exclude_words` 移到新增的 `[clean]` 區塊，並加預設值。已用 `from_toml` 逐一載入確認。
- `save_module_config_as_toml` 已能處理新 section，不需改動。

### [T004] workflow 與落盤
- `workflow.py`：以 `[clean]` 參數建立 `WebpageMarkdownCleaner` 傳入 crawler，傳 `llm_exclude_words`；有 `generation_result` 時呼叫 `save_generated_exclude_words`。
- 落盤函式先寫在 `workflow.py`，依 TODO 移到 `run_persistence.py` 並改為公開名稱；同時清掉 `workflow.py` 中不再使用的 import。

### [T005] 實驗腳本改用共用函式
- `scripts/ab_test_llm_exclude_words.py`：移除 `_RawCapturingCrawler`（改讀 `crawler.raw_pages`）、`sample_pages`、`guard_words`、`propose_exclude_words`、`word_hits`；改呼叫 `WebpageMarkdownCleaner`。報告與指標邏輯不變。
- 改完後未實際執行此腳本。

### [T006] 修正 Pylance 報錯
- `completion()` 回傳型別可能為串流物件：以 `isinstance(response, ModelResponse)` 收斂型別，不符則拋 `TypeError`（被 `generate_exclude_words` 視為單次失敗）。
- `usage` 改用 `getattr(response, "usage", None)`，與 `webpage_image_summarizer.py` 一致；缺欄位記 0。
- `pyright` 對 `src/app` 與新測試檔為 0 錯誤，不需 `type: ignore`。

### [T007] 文件同步
- `README.md`：目錄樹移除 `utils/markdown_cleaner.py`，加入 `engines/webpage_markdown_cleaner.py`。
- `docs/code/runs/config.md`：`crawl` 與新增 `clean` 的鍵列表。
- `docs/code/phase1/modules/data_collect.md` 提到 `exclude_words` 的兩處為型別說明，未改。

## 單元測試

新增 `src/test/dev/test_webpage_markdown_cleaner.py`（8 個）：`guard_words` 規則、`sample_pages` 下限與可重現、`generate_exclude_words` 聯集與得票順序、單次失敗略過與全部失敗拋例外、prompt 超限不呼叫 API、串流型別被拒、`clean_pages`、`save_generated_exclude_words` 落盤內容。

測試 mock 需改用真的 `litellm.ModelResponse`（T006 加入型別檢查後，`SimpleNamespace` 會被擋）。

結果：`uv run pytest src/test/dev` 共 167 個通過；`ruff check` 通過。

## 端到端驗證

指令：`uv run python src/cli.py website-crawler-cli --run.config-name <config>`。CLI 只開放 `--module.max-pages`，`[clean]` 參數需改 toml，因此 LLM 測試以臨時 toml（拿掉人工詞、`seed = 42`），測完刪除。

### 1. 回歸（test_nculab，`llm_exclude_words=false`）
- 9 頁成功（1 頁重複）。舊版 `clean_markdown`（取自 git HEAD）與新版逐頁輸出完全相同；人工詞無殘留；沒有產生 `generated_exclude_words.toml`；`module_config.toml` 含 `[clean]`。

### 2. LLM 產生（nculab）
- 5 次呼叫成功，成本 $0.0046；產生 6 個詞，每個 5/5 票、命中 9 行，與人工清單的英文 6 詞一致。
- 與人工清單輸出比對：4 頁看似不同，正規化 Google 圖片簽章 URL 後 9 頁全相同。

### 3. 失敗行為
- `max_prompt_tokens = 50`：拋出 `ExcludeWordsGenerationError`（prompt ≈ 4629 tokens），log 顯示 "Website Crawling Failed"；API 呼叫前即擋下，未花費。
- **exit code 仍為 0**：`cli.py` 不檢查 `run_website_crawler` 回傳值（既有行為）。

### 4. ncucsie 與 nculab 比較（各 9 頁，seed=42，基準為關閉 LLM 的人工清單輸出）

| | test_nculab | test_ncucsie |
|---|---|---|
| LLM 詞數（5 次聯集） | 6 | 45 |
| 各次穩定度（交集/聯集） | 6/6 | 2/45 |
| 成本 | $0.0046 | $0.0108 |
| 輸出字元（人工 → LLM） | 23100 → 23100 | 36434 → 37317 |
| 殘留雜訊行（LLM 沒刪、人工有刪） | 0 | 32 行（25 種） |
| 多刪行（LLM 刪、人工沒刪） | 0 | 38 行（11 種） |

ncucsie 觀察：
- **殘留**：新聞類別標籤（`得獎訊息`、`徵才訊息`、`招生快訊`、`演講公告`、`活動快訊`、`課程訊息`、`系辦公告`）各 2 行，及首頁 `![slide_N…]`。這類內容只在少數頁出現，樣本常抽不到。
- **誤刪正文**：`大學部`、`碩士班`、`博士班`、`外籍生`、`在職班` 各只得 1 票，卻刪掉 `## 大學部`、`## 碩士班` 等正文標題與含這些詞的句子。這是 vote1 聯集的已知風險。
- `* * *` 分隔線被刪 18 行，屬視覺分隔，影響可忽略。
- 每次抽樣只有 2 頁（最低頁數），遠小於 survey 的 21 頁；全站規模下結果可能不同，此處只反映小樣本。

## 未驗證項目

- 全站規模（204 頁）的 ncucsie 未跑。
- `repeat` 次中部分失敗、部分成功的情況只有 mock 測試，未用真實 API 驗證。
- 實驗腳本 `scripts/ab_test_llm_exclude_words.py` 改用共用函式後未實際執行。
- 只測了單一模型 `gpt-5.6-luna`。
