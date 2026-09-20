# LLM 產生 exclude_words 整合正式流程：規劃

> 統合兩個階段的規劃：(1) 將 survey 選定的 vote1 接進正式爬蟲；(2) 補上全站行覆蓋率驗證，並移除人工 `exclude_words`，網頁清理改為全自動。執行紀錄見 [dev.md](dev.md)，方案調查與實驗見 [../survey/survey.md](../survey/survey.md)。

## 目標

網頁清理的雜訊移除核心是 `exclude_words` 行級過濾，原本由人工看爬取結果挑詞、貼進 `configs/website_crawler/<site>.toml`，每個新站台都要重做。目標：

1. 新站台不需人工挑詞，一律由 LLM 從樣本頁提議詞。
2. 以全站行覆蓋率驗證剔除會誤傷正文的詞，達到 survey 的最佳方案「vote1 + 全站行覆蓋率驗證」。
3. 完整工作流程（爬蟲 → 圖片摘要 → RAG build → Server）能以單一指令針對指定站台跑通。

## 最終流程

```
爬取全站（保留原始 fit_markdown）
 → 頁數 < 2：跳過 LLM，不過濾
 → 重複 repeat 次（預設 5）：隨機抽 sample_ratio（預設 10%，至少 2 頁）→ LLM 提議
   → guard_words（長度 ≥ 2、去重、逐字出現在 ≥ 2 個樣本頁）
 → 聯集（vote1）
 → 全站行覆蓋率驗證：命中次數中落在低覆蓋行（覆蓋率 < 5%）的比例 > 0.1 的詞剔除
 → 逐頁 clean_markdown（exclude_words 行級過濾 → 其餘既有清理步驟）
```

## 關鍵限制

`WebsiteCrawler._filter_crawl_results` 原本在去重時就地呼叫 `clean_markdown(exclude_words=...)`，此時尚未有全站頁面，無法先產生詞。必須把「去重」與「清理」拆開：先收齊原始 fit_markdown → 產生詞 → 再清理。

## 架構決策

| 決策 | 最終選擇 | 理由 | 曾考慮／已改變 |
|---|---|---|---|
| 清理與產生詞的位置 | `src/app/engines/webpage_markdown_cleaner.py` 的 `WebpageMarkdownCleaner`（由 `src/utils/markdown_cleaner.py` `git mv` 搬入） | 風格對齊 `WebpageImageSummarizer`；產生詞與清理共用一個類別 | 另建 `exclude_words_generator.py` |
| 類別介面 | 有狀態類別；`clean_markdown`、`promote_empty_heading_line`、`sample_pages`、`guard_words`、`count_word_hits`、`normalize_line`、`line_coverage`、`word_stats` 為 staticmethod；`validate_words` 為實例方法 | 實驗腳本可無狀態呼叫共用函式 | 保留模組層級函式 |
| 設定位置 | `[clean]` 區塊；`exclude_words` 已從 `[crawl]` 移除 | 清理設定集中 | 只放新參數 |
| **人工 `exclude_words`** | **移除**，一律由 LLM 產生 | 使用者要求盡可能自動化（原先是與 LLM 詞取聯集） | 聯集；人工優先 |
| **`llm_exclude_words` 開關** | **移除**，無關閉旗標（僅頁數 < 2 自動跳過） | 全自動化；原預設 `false` 是為了避免行為改變 | 預設關閉；`repeat = 0` 表示關閉 |
| 失敗處理 | 單次呼叫失敗只略過該次；全部失敗或 prompt 超過 `max_prompt_tokens` 則整個爬取失敗（`_safe_step`） | 全自動下沒有人工詞可退回，寧可失敗也不輸出未清理資料 | 退回不過濾並警告 |
| 驗證 | 固定啟用；`LOW_COVERAGE`、`MIN_WORD_LEN`、`MIN_SAMPLE_PAGES` 為程式常數，只有 `max_low_occ_ratio` 是 cleaner 參數（預設 0.1）且**不進 toml** | 門檻只有單一資料點，先不對外暴露；使用者逐一挑選後認為只有 `[clean]` 直觀參數需要保留 | 四個驗證參數都進 toml；只保留 `max_low_occ_ratio` 進 toml（已再撤銷） |
| 空詞清單 | 照常繼續並記 warning，等同不做行級過濾 | 小站或本來就沒雜訊的站很常見 | 視為失敗 |
| 頁數 < 2 | 跳過 LLM 與驗證，`generation_result` 為 `None` | 樣本頁保護永遠無法通過，避免白花成本 | 照常呼叫 |
| `generate_exclude_words` 回傳 | `GenerationResult | None`：words（驗證後）、votes、seed、samples、runs、raw_runs、usages、rejected、stats | 可完整重現與審查；被剔除的詞與比例可事後檢視 | 精簡版 |
| 落盤與 log | `generated_exclude_words.toml`（驗證後的詞）、`exclude_words_report.json`（含 `low_occ_ratio` 與 `rejected`）、rich log 表格與被剔除詞 | 事後檢視與除錯 | 另存原始 markdown |
| 人工基準清單 | 從 toml 移到 `survey/manual_baseline/<site>.toml`，實驗腳本以 `--manual-toml` 讀取 | 保留評測基準，不依賴 git 歷史 | 只靠 git 歷史 |
| RAG 向量庫發布 | `run_rag_build` 在有 `data_manager` 時發布向量庫與 run 元資料；`RAG.milvus_uri` 記錄實際路徑 | 見「工作流整合補強」 | `main.py` 改 `save_vector_store_to_runs=False` 直接寫 `data/` |

### 最終 `[clean]` 參數

```toml
[clean]
llm_model = "gpt-5.6-luna"
sample_ratio = 0.1
repeat = 5
max_prompt_tokens = 200000
# seed = 42   # 選填，不設則隨機
```

程式常數（`webpage_markdown_cleaner.py`）：`MIN_WORD_LEN = 2`、`MIN_SAMPLE_PAGES = 2`、`LOW_COVERAGE = 0.05`；cleaner 參數 `max_low_occ_ratio = 0.1`。

## 修改範圍

1. **`webpage_markdown_cleaner.py`**：清理邏輯搬入；新增 `sample_pages`、`guard_words`、`_propose_words`、`generate_exclude_words`、`count_word_hits`、`GenerationResult`、`ExcludeWordsGenerationError`；再新增 `normalize_line`、`line_coverage`、`word_stats`、`validate_words`。
2. **`website_crawler.py`**：`_filter_crawl_results` 只去重、保存原文；`_clean_results` 產生詞後清理；流程為 crawl → filter → clean → enrich；移除 `exclude_words`、`llm_exclude_words` 屬性與參數。
3. **`website_crawler_config.py` 與 6 個 toml**：新增 `[clean]`；移除 `exclude_words`、`llm_exclude_words`；一次遷移，不做舊 key 相容。
4. **`workflow.py` / `run_persistence.py`**：workflow 依 `[clean]` 建立 cleaner；落盤與 log 由 `save_generated_exclude_words` 負責；`run_rag_build` 補發布。
5. **`scripts/`**：兩支實驗腳本改用 cleaner 共用函式，並改讀 `manual_baseline`。
6. **`main.py` / `workflow_config.py`**：`MainRunConfig`、`MainCLI`，以 `--run.config-name` 指定站台；輸出主流程運行時間。
7. **文件**：`README.md`、`docs/code/runs/config.md`、`docs/code/runs/workflow.md`、`docs/code/phase1/modules/data_collect.md`（`docs/work/`、`docs/survey/` 歷史文件不改）。

## 工作流整合補強

驗證完整工作流時發現：RAG build 階段不會發布向量庫。commit `18a0bc2` 重構時刪掉了 `publish_vector_store` 的呼叫，重構後沒有補回；`main.py` 又使用 `save_vector_store_to_runs=True`，向量庫只寫在 `runs/`，Server 讀的仍是 `data/rag/<site>/` 的舊庫。決定補回 publish：先建在 `runs/`、成功後才複製到 `data/`，失敗不會破壞舊資料。

## 破壞性變更

- `[clean]` 移除 `exclude_words`、`llm_exclude_words`：舊 toml 與 `runs/` 內保存的舊 module config 含這兩個鍵時會被未知鍵檢查擋下。
- `[clean]` 區塊必填，缺席時拋 `ConfigNotFoundError`（與其他 section 行為一致）。
- 所有爬取都會呼叫 LLM（需 API key），每站約 $0.005–0.05。
- 移除人工詞後，無法手動補救殘留（如首頁 `焦點新聞` 區塊）。

## 規劃過程中釐清的決策

| 議題 | 決定 |
|---|---|
| cleaner 介面形式 | 類別加 staticmethod |
| `exclude_words` 是否搬到 `[clean]` | 搬（後來整個移除） |
| 人工清單存在時是否仍呼叫 LLM | 先定為聯集，後改為移除人工清單 |
| LLM 失敗時退回或失敗 | 整個爬取失敗，維持不變 |
| 空詞清單 | 照常繼續並記 warning |
| 頁數 < 2 | 跳過 LLM，不過濾 |
| `max_prompt_tokens` | 保留在 `[clean]`（曾考慮改常數） |
| 驗證門檻是否進 toml | 只有 `max_low_occ_ratio` 曾短暫進 toml，最後撤銷，全部為程式常數／cleaner 參數 |
| 人工基準清單位置 | 一律搬到 docs 實驗目錄 |
| `main.py` 是否恢復 CLI 參數 | 恢復，用 tyro `--run.config-name`（推翻先前「不保留參數」的 D7 決策） |
| Server 階段的 config | 固定使用 `default`（Agent config 是多站共用的，沒有各站的檔案） |
| 少頁站台的驗證 | 不設頁數下限，照常驗證，於文件註明限制 |

## 驗證計畫

1. 單元測試：`guard_words`、`sample_pages`、`generate_exclude_words`（mock）、失敗處理、`clean_pages`、`line_coverage`／`word_stats`／`validate_words`、`run_rag_build` publish。
2. 回歸：開關關閉時 nculab 輸出與舊版逐頁相同（第一階段）。
3. 端到端：nculab、ncucsie 的爬蟲階段；`test_module.py` 五個階段；`main.py` 完整流程。
4. 失敗行為：以極小 `max_prompt_tokens` 觸發，確認爬取失敗。

## 已知風險與限制

- **少頁站台驗證失效**：`LOW_COVERAGE = 0.05`，單頁獨有行的覆蓋率是 1/頁數，頁數 ≤ 20 時沒有行會被算成低覆蓋，所有詞的 low-occ ratio 都是 0。survey 只在 204 頁驗證。
- **各次詞清單穩定度低**：同一站台兩次爬取提出的詞可能不同（詞不同而非驗證差異）。
- **邊緣詞可能誤刪正文**：`分享`、`下一頁`、`最終頁`、`更多` 等 low-occ 接近 10% 的通用詞被保留。
- **驗證只能剔除，補不了詞**：首頁專屬內容（`焦點新聞` 區塊、輪播圖）殘留是全站統計方法難以處理的範圍。
- vote1 聯集會納入只在單次抽樣出現的詞。
- 只測了單一模型 `gpt-5.6-luna`。

## 後續候選

- 讓 `LOW_COVERAGE` 隨頁數調整（例如 `max(0.05, 2/頁數)`），讓小站也能驗證；需要另行決定，會改變 survey 定案的行為。
- 跑比較腳本（`scripts/ab_test_llm_exclude_words.py`）取得 ncucsie 全站的重合率、多刪行、殘留行，對照 survey 指標（99.3%／3 行／19 行）。
- 檢查 `分享`、`更多` 等邊緣詞實際刪掉哪些正文行。
- CLI 只開放 `--module.max-pages`，`[clean]` 參數需改 toml；可在 `WebsiteCrawlerModuleConfig` 加旗標。
- `cli.py` 不檢查爬取回傳值，失敗時 exit code 仍為 0。
- `create_rag` 內另外建立 `RunManager`，向量庫落在 `runs/<ts>/rag_build/<site>/<site>/results/`（兩層站台名），與 workflow 自己的 run 目錄不同，可整併。
