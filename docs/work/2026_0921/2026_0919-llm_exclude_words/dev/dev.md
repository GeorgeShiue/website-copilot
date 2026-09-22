# LLM 產生 exclude_words 整合正式流程：實作日誌

> 規劃與決策見 [plan.md](plan.md)，方案調查與實驗見 [../survey/survey.md](../survey/survey.md)。

## 實作紀錄

### [T001] 搬移並重新包裝 cleaner
- `git mv src/utils/markdown_cleaner.py src/app/engines/webpage_markdown_cleaner.py`，改寫為 `WebpageMarkdownCleaner`。
- 清理邏輯原樣搬入並改為 staticmethod，新增 `clean_pages`。
- 從實驗腳本搬入：`MIN_WORD_LEN`、`MIN_SAMPLE_PAGES`、`PROMPT`、`sample_pages`、`guard_words`、單次 LLM 呼叫 `_propose_words`；新增 `generate_exclude_words`、`count_word_hits`、`GenerationResult`、`ExcludeWordsGenerationError`。
- 與腳本的差異：prompt 超過上限改拋例外（腳本原為 `SystemExit`）；`raw_words` 不是 list 時視為空；`json` 解析失敗或 `AttributeError` 視為空詞。

### [T002] WebsiteCrawler 改流程
- `_filter_crawl_results` 只做 404／無 markdown／去重，保存原始 `fit_markdown`。
- 新增 `_clean_results`；`crawl_website` 依序執行並各自包 `_safe_step`，LLM 步驟失敗回傳 None。
- 新增 `cleaner` 建構參數，屬性 `generation_result`、`raw_pages`。（原本還有 `_resolve_exclude_words`、`llm_exclude_words` 參數，見 T009。）

### [T003] 設定與 toml 遷移
- `website_crawler_config.py`：新增 `[clean]` section、`CLEAN_KEYS`、欄位與驗證；`exclude_words` 移出 `CRAWL_KEYS`。
- 6 個 toml（`default`、`nculab`、`ncucsie`、`test`、`test_nculab`、`test_ncucsie`）以腳本遷移，並用 `from_toml` 逐一載入確認。
- `save_module_config_as_toml` 已能處理新 section，不需改動。

### [T004] workflow 與落盤
- `workflow.py`：以 `[clean]` 參數建立 `WebpageMarkdownCleaner` 傳入 crawler；有 `generation_result` 時呼叫 `save_generated_exclude_words`。
- 落盤函式先寫在 `workflow.py`，依 TODO 移到 `run_persistence.py` 並改為公開名稱；清掉 `workflow.py` 中不再使用的 import。

### [T005] 實驗腳本改用共用函式
- `scripts/ab_test_llm_exclude_words.py`：移除 `_RawCapturingCrawler`（改讀 `crawler.raw_pages`）、`sample_pages`、`guard_words`、`propose_exclude_words`、`word_hits`；改呼叫 `WebpageMarkdownCleaner`。報告與指標邏輯不變。

### [T006] 修正 Pylance 報錯
- `completion()` 回傳型別可能為串流物件：以 `isinstance(response, ModelResponse)` 收斂型別，不符則拋 `TypeError`（被 `generate_exclude_words` 視為單次失敗）。
- `usage` 改用 `getattr(response, "usage", None)`，與 `webpage_image_summarizer.py` 一致；缺欄位記 0。
- `pyright` 對 `src/app` 為 0 錯誤，不需 `type: ignore`。

### [T007] 文件同步（第一階段）
- `README.md`：目錄樹移除 `utils/markdown_cleaner.py`，加入 `engines/webpage_markdown_cleaner.py`。
- `docs/code/runs/config.md`：`crawl` 與新增 `clean` 的鍵列表。

### [T008] 補上全站行覆蓋率驗證
- `WebpageMarkdownCleaner` 新增 `normalize_line`、`line_coverage`、`word_stats`（皆為 staticmethod，自實驗腳本搬入）與 `validate_words`；常數 `LOW_COVERAGE = 0.05`、`LINK_URL_RE`；`__init__` 新增 `max_low_occ_ratio`（預設 0.1）。
- `generate_exclude_words` 末端驗證，回傳型別改為 `GenerationResult | None`：`words` 為驗證後的詞，新增 `rejected`、`stats`；`votes` 保留所有詞。全站頁數 < `MIN_SAMPLE_PAGES` 時跳過 LLM 回傳 `None`；驗證後為空只記 warning。
- `save_generated_exclude_words`：報告加 `low_occ_ratio` 與 `rejected`，log 表格加 Low-occ ratio 欄，並列出被剔除的詞。
- 實驗腳本改用共用函式，建立 cleaner 時傳 `max_low_occ_ratio=1.0` 以保留「未驗證 vote1」供比較，並改處理 `generation` 為 `None`。

### [T009] 移除人工 exclude_words 與 llm_exclude_words
- `[clean]` 移除 `exclude_words`、`llm_exclude_words`；`max_low_occ_ratio` 曾加進 toml 後撤銷，維持 cleaner 參數（預設 0.1，不進 toml）。最終 `[clean]`：`llm_model`、`sample_ratio`、`repeat`、`max_prompt_tokens`、`seed`。
- `WebsiteCrawler` 移除 `exclude_words`、`llm_exclude_words` 屬性與參數，刪掉 `_resolve_exclude_words`；`_clean_results` 直接呼叫 `generate_exclude_words`，結果為 `None` 時不過濾。
- 6 個 toml 遷移；nculab（6 詞）、ncucsie（31 詞）的人工清單保存到 `survey/manual_baseline/<site>.toml`，兩支實驗腳本以 `--manual-toml`（預設此目錄）讀取。
- 使用者調整 docs 目錄結構後，腳本的 `MANUAL_BASELINE_DIR` 一度指向舊路徑，已修正為 `.../survey/manual_baseline`，並驗證兩份清單能載入。

### [T010] 補回 RAG build 的向量庫發布
- **問題**：`main.py` 跑完後 `data/rag/<site>/` 沒有更新。原因：`run_rag_build` 只把 `data_manager` 傳給 `create_rag`，沒有任何 `publish_*`；commit `18a0bc2` 重構時刪掉了 `publish_vector_store` 的呼叫且沒有補回；`main.py` 又用 `save_vector_store_to_runs=True`，向量庫只寫在 `runs/`。
- `workflow.py`：`run_rag_build` 在 `data_manager` 不為 `None` 時，先 `rag.close()` 釋放 Milvus Lite，再 `publish_vector_store` 與 `publish_run_metadata(category="rag")`；補 `import os`。
- `RAG` 新增 `milvus_uri` 屬性，`create_rag` 建構後寫入實際使用的路徑（因為 `save_vector_store_to_runs=True` 時路徑是在 `create_rag` 內部被改到 `runs/`，外層拿不到）。
- 新增 `src/test/dev/test_run_rag_build_publish.py`（3 個）：有 `data_manager` 時發布向量庫與元資料、無 `data_manager` 不發布、向量庫路徑不存在時只發布元資料。

### [T011] `main.py` 支援 CLI 參數與運行時間
- `workflow_config.py` 新增 `MainRunConfig`（`config_name`）；`main.py` 新增 `MainCLI`，`main(config_name="default")`，tyro 的 import 與 `tyro.cli(MainCLI)` 放在 `__main__` 內，旗標為 `--run.config-name`（與 `cli.py` 一致）。
- 使用者將 Server 階段暫時固定為 `run_app(config_name="default")`（Agent config 為多站共用，沒有各站的檔案）。
- 以既有的 `log_run_time` 包住爬蟲 → 圖片摘要 → RAG build，輸出 `Main Workflow (<config>) Completed in X seconds`；不含阻塞的 Server 時間，失敗提早 `return` 時也會輸出。
- README 與 `docs/code/runs/workflow.md` 用法已更新。

### [T012] 測試 config 頁數
- `test.toml`、`test_nculab.toml`、`test_ncucsie.toml` 的 `max_pages` 由 10 → 20 → 40：頁數 ≤ 20 時驗證不會剔除任何詞（詳見「端到端驗證」）。

### [T013] 文件同步（第二階段）
- `docs/code/runs/config.md`：`[clean]` 鍵列表改為 `llm_model`、`sample_ratio`、`repeat`、`max_prompt_tokens`、`seed`，註明不再提供人工清單與開關。
- `docs/code/phase1/modules/data_collect.md`：兩處 `exclude_words` 型別說明改為已移除。
- `survey.md`：驗證已進正式流程，並註明少頁站台驗證失效。

## 單元測試

`src/test/dev/test_webpage_markdown_cleaner.py` 涵蓋：`guard_words` 規則、`sample_pages` 下限與可重現、`generate_exclude_words` 聯集與得票順序、單次失敗略過與全部失敗拋例外、prompt 超限不呼叫 API、串流型別被拒、`clean_pages`、`save_generated_exclude_words` 落盤內容；驗證階段新增 `line_coverage`／`word_stats`、`normalize_line`、`validate_words` 邊界、驗證剔除低覆蓋詞、全部剔除回傳空清單、頁數不足跳過 LLM。

- 測試 mock 需使用真的 `litellm.ModelResponse`（T006 加入型別檢查後，`SimpleNamespace` 會被擋）。
- 驗證相關測試用 30 頁：頁數 ≤ 20 時單頁獨有行覆蓋率 ≥ 5%，沒有行算低覆蓋。
- 結果：`uv run pytest src/test/dev` 共 176 個通過；`ruff check`、`pyright src/app` 為 0 錯誤。

## 端到端驗證

指令：`uv run python src/cli.py website-crawler-cli --run.config-name <config>`。

### 1. 第一階段（人工詞 + LLM 聯集，各 9 頁，seed = 42）
以臨時 toml（拿掉人工詞、`seed = 42`）測試，基準為關閉 LLM 的人工清單輸出：

| | test_nculab | test_ncucsie |
|---|---|---|
| LLM 詞數（5 次聯集） | 6 | 45 |
| 各次穩定度（交集/聯集） | 6/6 | 2/45 |
| 成本 | $0.0046 | $0.0108 |
| 殘留雜訊行（LLM 沒刪、人工有刪） | 0 | 32 行（25 種） |
| 多刪行（LLM 刪、人工沒刪） | 0 | 38 行（11 種） |

- 回歸（`llm_exclude_words=false`）：舊版與新版逐頁輸出完全相同。
- 失敗行為：`max_prompt_tokens = 50` 拋 `ExcludeWordsGenerationError`（prompt ≈ 4629 tokens），API 呼叫前即擋下；**exit code 仍為 0**，因 `cli.py` 不檢查 `run_website_crawler` 回傳值（既有行為）。
- ncucsie 的 `大學部`、`碩士班`、`博士班`、`外籍生`、`在職班` 各只得 1 票，卻刪掉 `## 大學部` 等正文標題（誤刪的來源，促成 T008）。

### 2. 加入驗證後：test config 頁數的影響

| `max_pages` | 成功頁 | 結果 |
|---|---|---|
| 20 | 約 19 | 驗證沒有剔除任何詞（ncucsie 56 個詞全數保留，low-occ 全為 0.0%；單頁獨有行覆蓋率 1/19 ≈ 5.3% > 5%） |
| 40 | ncucsie 39、nculab 34 | ncucsie 保留 45／剔除 7（`大學部` 38%、`碩士班` 68%、`博士班` 67%、`外籍生` 14%、`在職班` 25%、`資訊工程學系` 23%、`enter image descri…` 69%）；nculab 6 詞全保留、0 剔除 |

### 3. 完整站台的爬蟲階段

| | nculab | ncucsie（第一次） | ncucsie（隨 main 再跑） |
|---|---|---|---|
| 成功頁數 | 47（404 8 頁、重複 10 頁） | 204（錯誤 95、重複 1） | 204（錯誤 95、重複 1） |
| 保留 / 剔除詞 | 6 / 0 | 41 / 6 | 32 / 1 |
| 剔除的詞 | — | `大學部` 73.9%、`碩士班`／`博士班`／`外籍生`／`在職班` 100%、`資訊工程學系` 17.0% | `焦點新聞` 32.4% |
| LLM 成本 | $0.0108 | $0.0423 | $0.0444 |
| 耗時 | 28 秒 | 85 秒 | 102 秒 |

- nculab 的 6 詞都是 5/5 票、命中 47 行（每頁一行），與人工清單的英文 6 詞一致。
- 兩次 ncucsie 的詞清單差異大：第一次提出 `大學部` 等正文詞被剔除，第二次沒有提出；第二次大部分詞是 5/5 票，`焦點新聞` 被剔除（首頁區塊，殘留是已知限制）。
- 低覆蓋比例接近門檻但被保留的詞（兩次相同）：`分享` 6.9%、`下一頁 >` 7.8%、`最終頁 »` 7.8%、`更多` 8.8%（第一次）。

### 4. `src/test/test_module.py`（`test` config = nculab，`max_pages = 40`）
5 個測試全過，共 242 秒：

| 階段 | 結果 |
|---|---|
| 爬蟲 | 34 頁；LLM 5 次呼叫 $0.0082 |
| 圖片摘要 | 109 秒，VLM 成本 $0.0589 |
| RAG build | 99 秒，Milvus 向量庫建立成功（dim = 1536） |
| Agent 單次查詢 | 3.7 秒 |
| Server | 啟動後自動關閉 |

Agent 回答為反問「哪個實驗室」（system prompt 要求 `[網站 X]` 前綴，測試未加），因此**未驗證檢索與回答品質**，僅確認 Agent 能啟動並回應。

### 5. `main.py` 完整工作流

`uv run python src/main.py --run.config-name <site>`；Server 階段使用 `default`。

| | nculab | ncucsie |
|---|---|---|
| 圖片摘要 | 73 張成功、0 失敗，$0.0802，205 秒 | 137 張成功、2 失敗，$0.1730，380 秒 |
| RAG build | 47 份文件 → 277 節點，78 秒 | 737 節點，169 秒 |
| 發布 | `data/rag/nculab/milvus.db` 修改時間更新（原 Sep 8 → Sep 20） | `data/rag/ncucsie/milvus.db` 更新 |
| `Main Workflow` | **314.0 秒** | 未擷取到輸出；三階段加總約 651 秒（102 + 380 + 169） |
| Server | 正常啟動並處理 `POST /api/chat` | 正常啟動；使用者實際查詢課程資訊，Agent 呼叫 `webpage_retriever`（`site_id=ncucsie`），首次查詢觸發 `RAG cache miss`，之後為 `cache hit`，`Ctrl+C` 後正常關閉 |

- ncucsie 的向量庫是從 `data/rag/ncucsie/milvus.db` 載入（log：`Successfully loaded index from vector store`），證明 T010 補回的發布路徑可用。

## 問題與處置

| 問題 | 處置 |
|---|---|
| 少頁站台驗證失效（頁數 ≤ 20 時所有詞 low-occ = 0） | 先前誤判為「過度嚴格」，端到端 20 頁測試證實為「失效」；文件註明，test config 提到 40 頁；是否讓 `LOW_COVERAGE` 隨頁數調整留待後續 |
| RAG build 沒有 publish | T010 |
| 實驗腳本 `MANUAL_BASELINE_DIR` 指向舊路徑（docs 重組後） | T009 中修正 |
| RAG build 的 Milvus `Method not implemented!`（`AllocTimestamp`，每次 2 筆） | 來自 Milvus Lite gRPC，向量庫仍建立成功；test_module 與 main 兩次跑都出現，判斷為既有現象，未處理 |
| `llama-index-readers-file` 警告（每個文件一筆） | Markdown 讀取不受影響，未處理 |
| ncucsie 圖片摘要有 2 張失敗 | 未追查原因 |

## 未驗證項目

- 與人工基準的比較（重合率、多刪行、殘留行）：全站 ncucsie 的完整比較腳本未跑；`scripts/ab_test_llm_exclude_words.py` 改用共用函式後，只驗證了基準清單能載入，沒有實際執行整支腳本。
- `分享`、`更多`、`下一頁` 等邊緣詞實際刪掉哪些正文行未檢查。
- 檢索與回答品質：`test_module` 的 Agent 查詢只問了無站台前綴的問題；ncucsie 的 Server 查詢由使用者自行操作，沒有記錄回答內容。
- `repeat` 次中部分失敗、部分成功的情況只有 mock 測試，未用真實 API 驗證。
- 只測了單一模型 `gpt-5.6-luna`。
- 尚未 commit。
